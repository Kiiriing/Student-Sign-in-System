# -*- coding: utf-8 -*-
# sync/worker.py
# 跨站签到同步 · 后台同步线程
#
# 项目原本没有任何调度机制，这里用一条 daemon 线程承担四件事：
#
#   1. snapshot push 把本站整库快照推给快照式对端（A 站）
#   2. outbox flush  把本站事件推给契约式对端
#   3. 增量 pull     契约式对端按游标拉增量；快照式对端全量拉 /api/sync/export
#   4. reconcile     对账，找出跨站重复签到并按规则裁决
#
# 该线程是「按需触发」的：只有在本站签到、收到对端 push、
# 或管理员手动触发同步时才会跑一轮，不做定时间隔轮询。
#
# 另外对外提供 check_duplicate_on_peers()，
# 供签到时实时向各对端查询「这个学生是不是已经在别处签过」。

import json
import threading
import time

from concurrent.futures import ThreadPoolExecutor

from sync.client import SyncHttpError, get_json, join_url, post_json

from sync.config import (
    CACHE_TTL,
    CHECK_TIMEOUT,
    CHECK_TOTAL_TIMEOUT,
    PEERS,
    PROTOCOL_CONTRACT,
    PROTOCOL_SNAPSHOT,
    PULL_LIMIT,
    PULL_TIMEOUT,
    PUSH_BATCH_SIZE,
    PUSH_TIMEOUT,
    SITE_CODE,
    SNAPSHOT_MIN_INTERVAL,
    SNAPSHOT_TIMEOUT,
    contract_peers,
    get_peer,
    peer_protocol,
    snapshot_peers,
)

from sync.snapshot import build_snapshot, import_snapshot

from sync.store import (
    get_cursor,
    ingest_events,
    mark_outbox_failed,
    mark_outbox_rejected,
    mark_outbox_sent,
    pending_outbox,
    reconcile,
    save_cursor,
)


# ============================================================
# 线程状态
# ============================================================

_wakeup = threading.Event()
_start_lock = threading.Lock()
_worker_started = False

# 实时查重结果缓存：{(student_no, align_key): (时间戳, 结果)}
_check_cache = {}
_check_cache_lock = threading.Lock()


def trigger_sync():
    """唤醒后台线程立刻跑一轮（签到后调用，非阻塞）"""

    _wakeup.set()


def _log(message):
    """同步日志统一前缀，方便在 logs/ 里检索"""

    print("[跨站同步] %s" % message)


# ============================================================
# 出站：推送
# ============================================================

def _payload_of(row):
    """DB 里的 json 字段读出来是字符串，这里统一成 dict"""

    payload = row["payload"]

    if isinstance(payload, (str, bytes)):

        try:
            return json.loads(payload)
        except ValueError:
            return None

    return payload


def flush_outbox():
    """
    把到期可发送的队列行推给各对端

    逐条按目标站点分组，批量 POST 到 /api/sync/inbound/push。
    单个站点异常不影响其它站点。
    """

    rows = pending_outbox(PUSH_BATCH_SIZE * max(len(PEERS), 1))

    if not rows:
        return {"sent": 0, "failed": 0}

    by_peer = {}

    for row in rows:

        event = _payload_of(row)

        if event is None:
            # 事件体损坏，直接判失败，避免无限重试
            mark_outbox_rejected(row["id"], "事件体无法解析")
            continue

        by_peer.setdefault(row["target_peer"], []).append((row, event))

    sent = 0
    failed = 0

    for peer_code, items in by_peer.items():

        peer = get_peer(peer_code)

        if not peer:
            for row, _event in items:
                mark_outbox_rejected(row["id"], "对端配置不存在：%s" % peer_code)
            failed += len(items)
            continue

        if peer_protocol(peer) != PROTOCOL_CONTRACT:
            # 该对端已切换为快照式协议，事件流不再适用。
            # 正常路径不会给快照式对端入队，这里兜住历史遗留的待发行。
            for row, _event in items:
                mark_outbox_rejected(
                    row["id"],
                    "目标站点已切换为快照式协议（%s）" % PROTOCOL_SNAPSHOT,
                )
            failed += len(items)
            continue

        url = join_url(peer["base_url"], "/api/sync/inbound/push")

        events = [event for _row, event in items]

        try:
            response = post_json(
                url,
                {"events": events},
                token=peer["token"],
                timeout=PUSH_TIMEOUT,
            )
        except SyncHttpError as e:
            # 网络层失败 → 整批退避重试
            for row, _event in items:
                mark_outbox_failed(row["id"], row.get("retry_count"), str(e))
            failed += len(items)
            _log("推送到 %s 失败：%s" % (peer_code, e))
            continue

        data = (response or {}).get("data") or {}

        accepted = {item.get("event_id") for item in (data.get("accepted") or [])}
        duplicated = {item.get("event_id") for item in (data.get("duplicated") or [])}
        rejected = {
            item.get("event_id"): item.get("reason")
            for item in (data.get("rejected") or [])
        }

        if not accepted and not duplicated and not rejected:
            # 响应结构不符合契约 → 整批退避重试
            for row, _event in items:
                mark_outbox_failed(row["id"], row.get("retry_count"), "对端响应结构异常")
            failed += len(items)
            _log("推送到 %s 响应异常：%s" % (peer_code, response))
            continue

        for row, event in items:

            event_id = event.get("event_id")

            if event_id in accepted or event_id in duplicated:
                mark_outbox_sent(row["id"])
                sent += 1
            elif event_id in rejected:
                mark_outbox_rejected(row["id"], rejected.get(event_id) or "对端拒绝")
                failed += 1
            else:
                mark_outbox_failed(row["id"], row.get("retry_count"), "对端未确认该事件")
                failed += 1

    return {"sent": sent, "failed": failed}


# ============================================================
# 出站：快照推送（针对快照式对端）
# ============================================================

# 快照推送节流状态：两轮之间至少间隔 SNAPSHOT_MIN_INTERVAL 秒
_snapshot_lock = threading.Lock()
_last_snapshot_at = 0.0


def push_snapshot_to_peers(force=False):
    """
    把本站整库快照推给各快照式对端（POST 对端 /api/sync/import）

    快照式对端不接事件流，只认整库 JSON。整库报文比单条事件大得多，
    因此按 SNAPSHOT_MIN_INTERVAL 节流，避免每轮同步都推一次全库。

    force=True 时忽略节流（管理员手动触发「连接对端」时用）。
    """

    global _last_snapshot_at

    peers = snapshot_peers()

    if not peers:
        return {}

    with _snapshot_lock:

        now = time.time()

        if not force and now - _last_snapshot_at < SNAPSHOT_MIN_INTERVAL:
            return {
                peer["code"]: {
                    "skipped": "距上次快照推送不足 %s 秒" % SNAPSHOT_MIN_INTERVAL
                }
                for peer in peers
            }

        _last_snapshot_at = now

    snapshot = build_snapshot()

    result = {}

    for peer in peers:

        url = join_url(peer["base_url"], "/api/sync/import")

        try:
            # 快照式对端无令牌、无统一外壳，直接收裸 JSON
            response = post_json(url, snapshot, timeout=SNAPSHOT_TIMEOUT)
        except SyncHttpError as e:
            result[peer["code"]] = {"error": str(e)}
            save_cursor(peer["code"], 0, success=False, error=str(e))
            _log("快照推送到 %s 失败：%s" % (peer["code"], e))
            continue

        data = response if isinstance(response, dict) else {}

        save_cursor(peer["code"], 0, success=True)

        result[peer["code"]] = {
            "records": data.get("created_records", 0),
            "skipped": data.get("skipped_records", 0),
            "errors": len(data.get("errors") or []),
        }

        _log("快照推送到 %s 完成：新增 %s 条 / 跳过 %s 条" % (
            peer["code"],
            data.get("created_records", 0),
            data.get("skipped_records", 0),
        ))

    return result


# ============================================================
# 入站：拉取
# ============================================================

def _pull_snapshot(peer):
    """
    快照式对端：GET /api/sync/export 全量拉回，整份合并进同步表

    对端没有游标概念（一次性全量 + 判重保证幂等），因此不动 last_seq，
    只按成功与否刷新 last_success_at / fail_count。
    """

    peer_code = peer["code"]
    since = get_cursor(peer_code)

    url = join_url(peer["base_url"], "/api/sync/export")

    try:
        snapshot = get_json(url, timeout=SNAPSHOT_TIMEOUT)
    except SyncHttpError as e:
        save_cursor(peer_code, since, success=False, error=str(e))
        _log("从 %s 拉取快照失败：%s" % (peer_code, e))
        return {"pulled": 0, "error": str(e)}

    if not isinstance(snapshot, dict):
        error = "对端返回的不是快照 JSON 对象"
        save_cursor(peer_code, since, success=False, error=error)
        _log("从 %s 拉取快照失败：%s" % (peer_code, error))
        return {"pulled": 0, "error": error}

    ingest = import_snapshot(snapshot, peer_code)

    save_cursor(peer_code, since, success=True)

    records = snapshot.get("records")

    return {
        "pulled": len(records) if isinstance(records, list) else 0,
        "accepted": ingest["created_records"],
        "duplicated": ingest["skipped_records"],
        "rejected": len(ingest["errors"]),
    }


def pull_from_peers():
    """按各自协议把各对端的数据拉回来入库

    契约式对端走游标增量事件流；快照式对端走 /api/sync/export 全量快照。
    """

    result = {}

    for peer in PEERS:

        peer_code = peer["code"]

        if peer_protocol(peer) == PROTOCOL_SNAPSHOT:
            result[peer_code] = _pull_snapshot(peer)
            continue

        since = get_cursor(peer_code)

        url = join_url(peer["base_url"], "/api/sync/inbound/pull")

        try:
            response = get_json(
                "%s?since=%s&limit=%s" % (url, since, PULL_LIMIT),
                token=peer["token"],
                timeout=PULL_TIMEOUT,
            )
        except SyncHttpError as e:
            save_cursor(peer_code, since, success=False, error=str(e))
            result[peer_code] = {"pulled": 0, "error": str(e)}
            _log("从 %s 拉取失败：%s" % (peer_code, e))
            continue

        data = (response or {}).get("data") or {}
        events = data.get("events") or []
        next_cursor = data.get("next_cursor")

        if next_cursor is None:
            next_cursor = since

        summary = {"pulled": 0, "accepted": 0, "duplicated": 0, "rejected": 0}

        if events:

            ingest = ingest_events(events)

            summary["pulled"] = len(events)
            summary["accepted"] = len(ingest["accepted"])
            summary["duplicated"] = len(ingest["duplicated"])
            summary["rejected"] = len(ingest["rejected"])

        save_cursor(peer_code, next_cursor, success=True)

        result[peer_code] = summary

    return result


# ============================================================
# 单轮执行
# ============================================================

def run_once(with_reconcile=True):
    """跑一轮同步：快照推送 → 事件推送 → 拉取 → 对账"""

    summary = {}

    try:
        summary["snapshot_push"] = push_snapshot_to_peers()
    except Exception as e:
        summary["snapshot_push"] = {"error": str(e)}
        _log("快照推送异常：%s" % e)

    try:
        summary["push"] = flush_outbox()
    except Exception as e:
        summary["push"] = {"error": str(e)}
        _log("推送异常：%s" % e)

    try:
        summary["pull"] = pull_from_peers()
    except Exception as e:
        summary["pull"] = {"error": str(e)}
        _log("拉取异常：%s" % e)

    if with_reconcile:

        try:
            summary["reconcile"] = reconcile()
        except Exception as e:
            summary["reconcile"] = {"error": str(e)}
            _log("对账异常：%s" % e)

    return summary


def _loop():
    """后台线程主循环：被唤醒时跑一轮，不做定时轮询"""

    _log("同步线程已启动（按需触发，无定时轮询），站点标识=%s，对端=%s" % (
        SITE_CODE,
        [peer["code"] for peer in PEERS],
    ))

    while True:

        _wakeup.wait()

        _wakeup.clear()

        try:
            run_once()
        except Exception as e:
            _log("同步异常：%s" % e)


def start_worker():
    """启动后台同步线程（按需触发；重复调用只生效一次）"""

    global _worker_started

    with _start_lock:

        if _worker_started:
            return False

        _worker_started = True

    thread = threading.Thread(target=_loop, name="cross-site-sync", daemon=True)
    thread.start()

    return True


# ============================================================
# 签到时的实时跨站查重
# ============================================================

def check_duplicate_on_peers(student_no, align_key):
    """
    向所有契约式对端实时查询该学生是否已签到

    快照式对端（A 站）不实现 /api/sync/check-dup，不参与实时查重
    （A 站的重复靠快照全量拉回后的对账消解）。

    返回 (hit, warnings)：

        hit      命中返回 {"source_site", "sign_time", "course_name"}；没命中返回 None
        warnings 不可达的对端提示列表，例如 ["A 站 不可用"]

    fail-open：任意对端超时 / 报错都只记警告，不阻断签到。
    """

    peers = contract_peers()

    if not peers or not student_no or not align_key:
        return None, []

    cache_key = (str(student_no), str(align_key))
    now = time.time()

    with _check_cache_lock:

        cached = _check_cache.get(cache_key)

        if cached and now - cached[0] < CACHE_TTL:
            return cached[1]

    payload = {"student_no": student_no, "align_key": align_key}

    hit = None
    warnings = []

    executor = ThreadPoolExecutor(max_workers=len(peers))

    try:
        futures = {}

        for peer in peers:

            url = join_url(peer["base_url"], "/api/sync/check-dup")

            futures[executor.submit(
                post_json, url, payload, peer["token"], CHECK_TIMEOUT
            )] = peer

        deadline = now + CHECK_TOTAL_TIMEOUT

        for future, peer in futures.items():

            remaining = max(deadline - time.time(), 0)

            try:
                response = future.result(timeout=remaining)
            except SyncHttpError as e:
                warnings.append("%s %s" % (peer["name"], _short_error(e)))
                continue
            except Exception as e:
                warnings.append("%s %s" % (peer["name"], _short_error(e)))
                continue

            data = (response or {}).get("data") or {}

            if data.get("duplicated") and hit is None:
                hit = {
                    "source_site": data.get("source_site"),
                    "sign_time": data.get("sign_time"),
                    "course_name": data.get("course_name"),
                }
    finally:
        # 不等待未完成的任务，避免拖住签到请求
        executor.shutdown(wait=False)

    result = (hit, warnings)

    with _check_cache_lock:
        _check_cache[cache_key] = (time.time(), result)

        # 顺手清掉过期缓存，避免无界增长
        if len(_check_cache) > 500:
            for key, value in list(_check_cache.items()):
                if time.time() - value[0] >= CACHE_TTL:
                    _check_cache.pop(key, None)

    return result


def _short_error(error):
    """把出站错误压缩成一句人话"""

    text = str(error)

    if "超时" in text or "timed out" in text.lower():
        return "响应超时"

    if "不可达" in text:
        return "不可达"

    return "校验失败"
