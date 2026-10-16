# -*- coding: utf-8 -*-
# sync/api.py
# 跨站签到同步 · 接口层
#
# 对外接口（供另外两个签到软件调用）：
#
#   POST /api/sync/inbound/push   接收对端推送的事件（契约式）
#   GET  /api/sync/inbound/pull   供对端拉取本站增量（契约式）
#   POST /api/sync/check-dup      实时查重（契约式）
#   GET  /api/sync/health         健康探测（契约式）
#   POST /api/sync/reconcile      管理员手动对账
#
#   GET  /api/sync/export         整库快照导出（快照式对端拉取的数据源）
#   GET  /api/sync/download       同上，以文件形式下载
#   POST /api/sync/import         接收快照式对端推来的整库 JSON
#
# 契约式的 4 个接口统一用请求头 X-Sync-Token 鉴权
# （对端不是本站用户，无法走 JWT），令牌即 sync.config.PEERS 里配置的 token。
#
# 快照式的 3 个接口与 A 站约定一致：无令牌、无统一响应外壳，直接收发裸 JSON
# （A 站对 /api/sync/* 不校验令牌，也不会带 X-Sync-Token）。
#
# 管理员接口（本站后台使用，走 JWT）：
#
#   GET  /api/admin/sync/status
#   GET  /api/admin/sync/outbox
#   POST /api/admin/sync/outbox/retry
#   GET  /api/admin/sync/conflicts
#   POST /api/admin/sync/conflicts/handle
#   POST /api/admin/sync/conflicts/batch
#   POST /api/admin/sync/trigger

import json

from datetime import date, datetime
from concurrent.futures import ThreadPoolExecutor
import threading
import time

from flask import Blueprint, Response, jsonify, request
from flask_jwt_extended import jwt_required

from core.auth_utils import require_role

from sync.config import (
    PEERS,
    PROTOCOL_SNAPSHOT,
    SITE_CODE,
    SITE_NAME,
    SNAPSHOT_DEFAULT_ORIGIN,
    SNAPSHOT_TIMEOUT,
    peer_names,
    peer_protocol,
    get_peer_by_token,
    site_name_of,
)
from sync.contract import (
    SCHEMA_VERSION,
    STATUS_TEXT,
    build_align_key,
    normalize_period,
    normalize_text,
)
from sync.snapshot import build_snapshot, import_snapshot
from sync.store import (
    CONFLICT_PENDING,
    count_conflicts,
    count_pending_conflicts,
    count_pending_outbox,
    cross_record_count,
    cursor_snapshot,
    fetch_outbound_batch,
    find_cross_duplicate,
    find_local_duplicate,
    handle_conflict,
    handle_conflicts,
    ingest_events,
    list_conflicts,
    list_outbox,
    outbox_stats,
    reconcile,
    retry_outbox,
)
from sync.client import SyncHttpError, get_json, join_url
from sync.config import CHECK_TIMEOUT
from sync.worker import trigger_sync


sync_bp = Blueprint("sync", __name__)
sync_admin_bp = Blueprint("sync_admin", __name__)


# ============================================================
# 工具
# ============================================================

def _normalize_value(value):
    """把 datetime / date 转成字符串，方便直接 jsonify"""

    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")

    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")

    return value


def _row_to_dict(row):
    """把一行查询结果转成可序列化的 dict"""

    if not row:
        return None

    return {key: _normalize_value(value) for key, value in row.items()}


def _require_peer():
    """
    校验 X-Sync-Token

    返回 (peer, error)
    """

    token = request.headers.get("X-Sync-Token", "")

    peer = get_peer_by_token(token)

    if not peer:
        return None, (
            jsonify({
                "code": 401,
                "message": "同步令牌无效"
            }),
            401
        )

    return peer, None


def _require_admin():
    """校验当前登录用户是否为管理员"""

    user, error = require_role(3, "无管理员权限")

    if error:
        return None, error

    return user["user_id"], None


def _resolve_align_key(data):
    """优先用事件里的 align_key，没有就按四段字段现算

    对齐键 = 学号 | 班级键 | 课程日期 | 时段档(morning/afternoon)
    """

    align_key = normalize_text(data.get("align_key"))

    if align_key:
        return align_key

    return build_align_key(
        data.get("student_no"),
        data.get("class_name"),
        data.get("course_date"),
        normalize_period(data.get("period") or data.get("time_slot")),
    )


# ============================================================
# 对端接口
# ============================================================

@sync_bp.route("/api/sync/health", methods=["GET"])
def sync_health():
    """健康探测；不校验令牌，只暴露站点标识与时间"""

    return jsonify({
        "code": 200,
        "message": "ok",
        "data": {
            "site_code": SITE_CODE,
            "site_name": SITE_NAME,
            "schema_version": SCHEMA_VERSION,
            "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    }), 200


@sync_bp.route("/api/sync/export", methods=["GET"])
def sync_export():
    """
    整库快照导出（快照式对端拉取的数据源）

    与 A 站约定一致：裸 JSON、无令牌、无统一外壳。
    格式见 A 站对接指导：version / exported_at / students / sessions / records。
    """

    try:
        snapshot = build_snapshot()
    except Exception as e:
        return jsonify({"detail": "导出失败：%s" % e}), 500

    return jsonify(snapshot), 200


@sync_bp.route("/api/sync/download", methods=["GET"])
def sync_download():
    """整库快照以文件形式下载；内容与 /api/sync/export 完全一致"""

    try:
        snapshot = build_snapshot()
    except Exception as e:
        return jsonify({"detail": "导出失败：%s" % e}), 500

    filename = "checkin_sync_%s.json" % datetime.now().strftime("%Y%m%d_%H%M%S")

    response = Response(
        json.dumps(snapshot, ensure_ascii=False),
        mimetype="application/json",
    )
    response.headers["Content-Disposition"] = "attachment; filename*=UTF-8''%s" % filename

    return response


@sync_bp.route("/api/sync/import", methods=["POST"])
def sync_import():
    """
    接收快照式对端推来的整库 JSON，合并进本站同步表

    与 A 站约定一致：裸 JSON、无令牌；响应直接给计数（不带统一外壳）。

    合并只取 records 段，落进独立的 cross_site_record，
    不写本地 attendance_record（本站考勤数据只由本站签到流程产生）。
    """

    snapshot = request.get_json(silent=True)

    if not isinstance(snapshot, dict):
        return jsonify({"detail": "请求体不是 JSON 对象"}), 422

    try:
        result = import_snapshot(snapshot, SNAPSHOT_DEFAULT_ORIGIN)
    except Exception as e:
        return jsonify({"detail": "写入同步表失败：%s" % e}), 500

    # 收到新数据后立刻唤醒同步线程，让对账尽快跑起来
    if result["created_records"]:
        trigger_sync()

    return jsonify(result), 200


@sync_bp.route("/api/sync/inbound/push", methods=["POST"])
def sync_inbound_push():
    """
    接收对端推送的事件

    请求体：

        {"events": [ {...事件信封...}, ... ]}
    """

    peer, error = _require_peer()

    if error:
        return error

    data = request.get_json(silent=True) or {}

    events = data.get("events")

    if not isinstance(events, list):
        return jsonify({
            "code": 400,
            "message": "events 必须是数组"
        }), 400

    try:
        result = ingest_events(events)
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": "写入同步表失败",
            "error": str(e)
        }), 500

    # 收到新数据后立刻唤醒同步线程，让对账尽快跑起来
    if result["accepted"]:
        trigger_sync()

    return jsonify({
        "code": 200,
        "message": "接收完成",
        "data": result
    }), 200


@sync_bp.route("/api/sync/inbound/pull", methods=["GET"])
def sync_inbound_pull():
    """
    供对端拉取本站增量

    查询参数：

        since  上次拉到的游标，默认 0
        limit  单次上限，默认 200
    """

    peer, error = _require_peer()

    if error:
        return error

    try:
        since = int(request.args.get("since", 0))
    except (TypeError, ValueError):
        since = 0

    try:
        limit = int(request.args.get("limit", 200))
    except (TypeError, ValueError):
        limit = 200

    limit = max(1, min(limit, 500))

    events, next_cursor = fetch_outbound_batch(peer["code"], since, limit)

    return jsonify({
        "code": 200,
        "message": "ok",
        "data": {
            "events": events,
            "next_cursor": next_cursor,
            "has_more": len(events) >= limit,
        }
    }), 200


@sync_bp.route("/api/sync/check-dup", methods=["POST"])
def sync_check_dup():
    """
    实时查重：这个学生在这门课上，是否已经在本站签过？

    请求体（两种写法都支持）：

        {"student_no": "...", "align_key": "..."}
        {"student_no": "...", "class_name": "...", "course_date": "...",
         "period": "morning|afternoon"}          # period 也可写作 time_slot

    对齐键 = 学号 | 班级键 | 课程日期 | 时段档

    返回 data.duplicated / source_site / sign_time / course_name
    """

    peer, error = _require_peer()

    if error:
        return error

    data = request.get_json(silent=True) or {}

    student_no = normalize_text(data.get("student_no"))
    align_key = _resolve_align_key(data)

    if not student_no or not align_key:
        return jsonify({
            "code": 400,
            "message": "student_no 与对齐键不能为空"
        }), 400

    hit = None

    # 1) 本站自己的签到记录
    local = find_local_duplicate(student_no, align_key)

    if local:
        hit = {
            "source_site": SITE_CODE,
            "sign_time": _normalize_value(local["sign_time"]),
            "course_name": local.get("course_name"),
        }

    # 2) 本站已同步到的第三站记录
    if hit is None:

        cross = find_cross_duplicate(student_no, align_key)

        if cross:
            hit = {
                "source_site": cross["origin_site"],
                "sign_time": _normalize_value(cross["sign_time"]),
                "course_name": cross["course_name"],
            }

    names = peer_names()

    if hit:

        hit["source_site_name"] = names.get(hit["source_site"]) or SITE_NAME

        return jsonify({
            "code": 200,
            "message": "ok",
            "data": {
                "duplicated": True,
                "source_site": hit["source_site"],
                "source_site_name": hit["source_site_name"],
                "sign_time": hit["sign_time"],
                "course_name": hit["course_name"],
            }
        }), 200

    return jsonify({
        "code": 200,
        "message": "ok",
        "data": {
            "duplicated": False,
            "source_site": None,
            "sign_time": None,
            "course_name": None,
        }
    }), 200


@sync_bp.route("/api/sync/reconcile", methods=["POST"])
@jwt_required()
def sync_reconcile():
    """管理员手动触发对账"""

    user_id, error = _require_admin()

    if error:
        return error

    try:
        stats = reconcile()
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": "对账失败",
            "error": str(e)
        }), 500

    return jsonify({
        "code": 200,
        "message": "对账完成",
        "data": stats
    }), 200


# ============================================================
# 管理员接口
# ============================================================

# 对端连通性探测结果缓存
#
# 每个对端探测最坏要等 CHECK_TIMEOUT（1.2s），原先在 admin_sync_status()
# 里串行遍历 PEERS，接口耗时 = 对端数 × 1.2s（实测 p50 ≈ 1.2s，p99 ≈ 1.7s），
# 前端每次进同步页都要卡这么久。
#
# 这里做三件事：
#   1. 多个对端用线程池并发探测，总耗时 ≈ 单个对端超时，而不是累加；
#   2. 结果缓存 PEER_PROBE_TTL 秒，避免前端刷新/轮询时反复探测；
#   3. 缓存过期时也不阻塞请求：先返回旧值，另起后台线程刷新（见 _refresh_peers）。
_PEER_PROBE_TTL = 5
_PEER_PROBE_CACHE = {"time": 0.0, "data": None, "refreshing": False}
_PEER_PROBE_LOCK = threading.Lock()


def _probe_peer(peer):
    """探测单个对端的连通性，返回展示用的状态字典

    契约式对端探 /api/sync/health；快照式对端没有该接口，
    用 /api/sync/export 能返回 200 当连通性证据。
    """

    item = {
        "code": peer["code"],
        "name": peer["name"],
        "base_url": peer["base_url"],
        "online": False,
        "site_name": None,
        "server_time": None,
        "error": None,
    }

    if peer_protocol(peer) == PROTOCOL_SNAPSHOT:

        url = join_url(peer["base_url"], "/api/sync/export")

        try:
            snapshot = get_json(url, timeout=SNAPSHOT_TIMEOUT)

            if isinstance(snapshot, dict):
                item["online"] = True
                item["site_name"] = peer["name"]
                item["server_time"] = snapshot.get("exported_at")
            else:
                item["error"] = "导出接口未返回快照 JSON"
        except SyncHttpError as e:
            item["error"] = str(e)

        return item

    url = join_url(peer["base_url"], "/api/sync/health")

    try:
        response = get_json(url, token=peer["token"], timeout=CHECK_TIMEOUT)
        data = (response or {}).get("data") or {}
        item["online"] = True
        item["site_name"] = data.get("site_name")
        item["server_time"] = data.get("server_time")
    except SyncHttpError as e:
        item["error"] = str(e)

    return item


def _probe_all_peers():
    """并发探测所有对端，返回状态列表"""

    if not PEERS:
        return []

    with ThreadPoolExecutor(max_workers=min(len(PEERS), 8)) as pool:
        return list(pool.map(_probe_peer, PEERS))


def _peers_status():
    """
    读取对端连通性（带短时缓存 + 后台异步刷新）

    关键点：探测对不可达对端最坏要等 CHECK_TIMEOUT（1.2s），
    绝不能放在请求路径上等。因此：

      - 缓存新鲜 → 直接返回；
      - 缓存过期但已有旧数据 → 立刻返回旧数据，另起后台线程去刷新
        （本次请求 0 等待，下次请求就能拿到新值）；
      - 从未探测过（进程启动后第一次调用）→ 只能同步探测一次。

    前端跨站同步页会每 5s 重试连接对端，若把探测放在请求路径上，
    每次重试都会卡满超时；异步刷新后这一现象消失。
    """

    now = time.time()

    with _PEER_PROBE_LOCK:

        cached = _PEER_PROBE_CACHE

        if cached["data"] is not None:

            if now - cached["time"] < _PEER_PROBE_TTL:
                return cached["data"]

            # 已过期：先返回旧值，后台单飞刷新
            if not cached["refreshing"]:
                cached["refreshing"] = True
                threading.Thread(target=_refresh_peers, daemon=True).start()

            return cached["data"]

        # 首次调用：没有任何数据，同步探测一次
        data = _probe_all_peers()
        cached["time"] = time.time()
        cached["data"] = data

        return data


def _refresh_peers():
    """后台刷新对端连通性缓存"""

    try:
        data = _probe_all_peers()
    except Exception:
        data = None

    with _PEER_PROBE_LOCK:

        if data is not None:
            _PEER_PROBE_CACHE["time"] = time.time()
            _PEER_PROBE_CACHE["data"] = data

        _PEER_PROBE_CACHE["refreshing"] = False


@sync_admin_bp.route("/api/admin/sync/status", methods=["GET"])
@jwt_required()
def admin_sync_status():
    """同步总览：站点信息、各对端连通性、游标、队列与冲突计数"""

    user_id, error = _require_admin()

    if error:
        return error

    # 探测各对端连通性（并发 + 短时缓存，见 _peers_status）
    peers_status = _peers_status()

    cursors = {
        code: _row_to_dict(row)
        for code, row in (cursor_snapshot() or {}).items()
    }

    return jsonify({
        "code": 200,
        "message": "ok",
        "data": {
            "site_code": SITE_CODE,
            "site_name": SITE_NAME,
            "schema_version": SCHEMA_VERSION,
            "peers": peers_status,
            "cursors": cursors,
            "outbox": outbox_stats(),
            "pending_outbox": count_pending_outbox(),
            "pending_conflicts": count_pending_conflicts(),
            "cross_record": cross_record_count(),
        }
    }), 200


@sync_admin_bp.route("/api/admin/sync/outbox", methods=["GET"])
@jwt_required()
def admin_sync_outbox():
    """发送队列明细"""

    user_id, error = _require_admin()

    if error:
        return error

    status_arg = request.args.get("status")

    status = None

    if status_arg not in (None, "", "all"):

        try:
            status = int(status_arg)
        except (TypeError, ValueError):
            status = None

    try:
        limit = int(request.args.get("limit", 100))
    except (TypeError, ValueError):
        limit = 100

    rows = [_row_to_dict(row) for row in list_outbox(status, max(1, min(limit, 500)))]

    names = peer_names()

    for row in rows:
        row["target_peer_name"] = names.get(row["target_peer"]) or row["target_peer"]

    return jsonify({
        "code": 200,
        "message": "ok",
        "data": {"items": rows}
    }), 200


@sync_admin_bp.route("/api/admin/sync/outbox/retry", methods=["POST"])
@jwt_required()
def admin_sync_outbox_retry():
    """手动重试失败的队列行"""

    user_id, error = _require_admin()

    if error:
        return error

    data = request.get_json(silent=True) or {}

    try:
        outbox_id = int(data.get("id"))
    except (TypeError, ValueError):
        return jsonify({
            "code": 400,
            "message": "缺少有效的队列ID"
        }), 400

    affected = retry_outbox(outbox_id)

    if affected == 0:
        return jsonify({
            "code": 404,
            "message": "队列记录不存在"
        }), 404

    trigger_sync()

    return jsonify({
        "code": 200,
        "message": "已重新入队",
        "data": {"id": outbox_id}
    }), 200


@sync_admin_bp.route("/api/admin/sync/conflicts", methods=["GET"])
@jwt_required()
def admin_sync_conflicts():
    """冲突列表"""

    user_id, error = _require_admin()

    if error:
        return error

    state_arg = request.args.get("state", str(CONFLICT_PENDING))

    try:
        state = int(state_arg)
    except (TypeError, ValueError):
        state = CONFLICT_PENDING

    keyword = request.args.get("keyword")

    try:
        limit = int(request.args.get("limit", 200))
    except (TypeError, ValueError):
        limit = 200

    limit = max(1, min(limit, 500))

    # state < 0 表示「全部状态」，交给查询层当不过滤处理
    state_filter = state if state >= 0 else None

    rows = []

    for row in list_conflicts(state_filter, limit, keyword):

        item = _row_to_dict(row)

        loser = item.get("loser_json")

        if isinstance(loser, (str, bytes)):

            try:
                item["loser_json"] = json.loads(loser)
            except ValueError:
                item["loser_json"] = None

        item["winner_site_name"] = site_name_of(item.get("winner_site"))

        # 落败记录存的是 {winner, losers[]} 嵌套结构，这里就地补上中文站点名与
        # 中文状态名：前端不必再维护一份 code → 名称的映射
        if isinstance(item.get("loser_json"), dict):

            for entry in item["loser_json"].get("losers") or []:

                if isinstance(entry, dict):
                    entry["site_name"] = site_name_of(entry.get("site"))
                    entry["status_text"] = STATUS_TEXT.get(entry.get("attendance_status"))

            winner_entry = item["loser_json"].get("winner")

            if isinstance(winner_entry, dict):
                winner_entry["site_name"] = site_name_of(winner_entry.get("site"))

        rows.append(item)

    return jsonify({
        "code": 200,
        "message": "ok",
        "data": {
            "items": rows,
            "total": count_conflicts(state_filter, keyword),
            "pending": count_pending_conflicts(),
        }
    }), 200


@sync_admin_bp.route("/api/admin/sync/conflicts/handle", methods=["POST"])
@jwt_required()
def admin_sync_conflict_handle():
    """处理冲突：resolve 已裁决 / ignore 忽略"""

    user_id, error = _require_admin()

    if error:
        return error

    data = request.get_json(silent=True) or {}

    conflict_id = normalize_text(data.get("id"))
    action = normalize_text(data.get("action"))

    if not conflict_id or action not in ("resolve", "ignore"):
        return jsonify({
            "code": 400,
            "message": "参数不合法"
        }), 400

    affected = handle_conflict(conflict_id, action, user_id)

    if affected == 0:
        return jsonify({
            "code": 404,
            "message": "冲突记录不存在或已处理"
        }), 404

    return jsonify({
        "code": 200,
        "message": "已处理",
        "data": {"id": conflict_id, "action": action}
    }), 200


@sync_admin_bp.route("/api/admin/sync/conflicts/batch", methods=["POST"])
@jwt_required()
def admin_sync_conflict_batch():
    """批量处理冲突：resolve 已裁决 / ignore 忽略

    ids 为空数组表示处理全部「待处理」的行（一键清空）。
    """

    user_id, error = _require_admin()

    if error:
        return error

    data = request.get_json(silent=True) or {}

    action = normalize_text(data.get("action"))
    ids = data.get("ids")

    if action not in ("resolve", "ignore"):
        return jsonify({
            "code": 400,
            "message": "参数不合法"
        }), 400

    if ids in (None, ""):
        ids = []
    elif not isinstance(ids, list):
        return jsonify({
            "code": 400,
            "message": "ids 必须是数组"
        }), 400

    affected = handle_conflicts(action, user_id, ids)

    return jsonify({
        "code": 200,
        "message": "已处理 %s 条" % affected,
        "data": {"affected": affected, "action": action}
    }), 200


@sync_admin_bp.route("/api/admin/sync/trigger", methods=["POST"])
@jwt_required()
def admin_sync_trigger():
    """
    手动触发同步

    body.action = "sync"（默认，异步跑一轮推送+拉取+对账）
                 "reconcile"（只同步执行对账）
    """

    user_id, error = _require_admin()

    if error:
        return error

    data = request.get_json(silent=True) or {}
    action = normalize_text(data.get("action")) or "sync"

    if action == "reconcile":

        try:
            stats = reconcile()
        except Exception as e:
            return jsonify({
                "code": 500,
                "message": "对账失败",
                "error": str(e)
            }), 500

        return jsonify({
            "code": 200,
            "message": "对账完成",
            "data": stats
        }), 200

    trigger_sync()

    return jsonify({
        "code": 200,
        "message": "已触发同步，稍后刷新查看结果",
        "data": {}
    }), 200
