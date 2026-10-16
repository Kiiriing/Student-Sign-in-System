# -*- coding: utf-8 -*-
# sync/store.py
# 跨站签到同步 · 数据访问层
#
# 负责 4 张同步表的建表与读写：
#
#   cross_site_record    入站同步表（独立存放外来记录，不动本地 attendance_record）
#   sync_cursor          对每个对端的 pull 水位
#   sync_outbox          待发送队列
#   cross_site_conflict  冲突登记
#
# 建表沿用 api/system.py 里 ensure_update_table() 的幂等写法，
# 项目没有迁移框架，用 CREATE TABLE IF NOT EXISTS 保证表一定存在。

import json

from datetime import datetime
from uuid import uuid4

from core.database import db_cursor, get_db

from sync.config import (
    MAX_RETRY,
    PULL_LIMIT,
    PROTOCOL_CONTRACT,
    RECONCILE_DAYS,
    SITE_CODE,
    PEERS,
    peer_protocol,
    snapshot_peers,
)
from sync.contract import (
    EVENT_SIGNIN,
    align_key_of_payload,
    build_align_key,
    build_event,
    normalize_attendance_status,
    normalize_class_key,
    normalize_date,
    normalize_period,
    normalize_text,
    normalize_time_slot,
    to_db_datetime,
    validate_event,
)


# ============================================================
# 状态常量
# ============================================================

RESOLVE_PENDING = 0     # 待裁决
RESOLVE_VALID = 1       # 有效
RESOLVE_VOID = 2        # 作废

OUTBOX_PENDING = 0      # 待发送
OUTBOX_SENT = 1         # 已发送
OUTBOX_FAILED = 2       # 发送失败（超过最大重试次数）

CONFLICT_PENDING = 0    # 待处理
CONFLICT_RESOLVED = 1   # 已裁决
CONFLICT_IGNORED = 2    # 已忽略

# 「有效跨站签到」统一判定（唯一来源）
#
# 各调用点原先各写各的过滤（有的 resolve_state <> 2，有的 =1 AND is_duplicate=0），
# 口径漂移正是最近多处 bug 的成因。语义：已入库且未被判为回声重复的异地签到。
# 注：resolve_state 只会写 1/2（RESOLVE_PENDING 从未使用），故它等价于「非作废」。
_VALID_CROSS_CONDITION = "resolve_state = 1 AND is_duplicate = 0"


# ============================================================
# 建表
# ============================================================

_CREATE_STATEMENTS = (
    # 入站同步表
    """
    CREATE TABLE IF NOT EXISTS `cross_site_record` (
      `id` char(36) NOT NULL COMMENT '本站记录ID',
      `origin_site` varchar(32) NOT NULL COMMENT '来源站点标识',
      `origin_record_id` varchar(64) NOT NULL COMMENT '来源站点的签到记录ID',
      `origin_task_id` varchar(64) DEFAULT NULL COMMENT '来源站点的签到任务ID',
      `student_no` varchar(32) NOT NULL COMMENT '学号',
      `student_name` varchar(50) DEFAULT NULL COMMENT '学生姓名',
      `class_name` varchar(50) DEFAULT NULL COMMENT '班级名',
      `course_name` varchar(100) DEFAULT NULL COMMENT '课程名',
      `course_date` date DEFAULT NULL COMMENT '课程日期',
      `period` varchar(20) DEFAULT NULL COMMENT '时段档 morning/afternoon（对齐键组成部分）',
      `time_slot` varchar(50) DEFAULT NULL COMMENT '时间段（精确时分，可能为空）',
      `align_key` varchar(255) DEFAULT NULL COMMENT '归一化对齐键 学号|班级键|日期|时段档',
      `attendance_status` tinyint DEFAULT NULL COMMENT '签到状态 1正常 2迟到 3旷课 4早退 5病假 6事假',
      `sign_time` datetime DEFAULT NULL COMMENT '异地签到时间',
      `device_id` varchar(255) DEFAULT NULL COMMENT '签到设备ID',
      `ip` varchar(45) DEFAULT NULL COMMENT '签到IP',
      `location` varchar(255) DEFAULT NULL COMMENT '签到位置',
      `is_script` tinyint NOT NULL DEFAULT 0 COMMENT '是否脚本签到',
      `task_start_time` datetime DEFAULT NULL COMMENT '来源站点任务开始时间',
      `task_end_time` datetime DEFAULT NULL COMMENT '来源站点任务结束时间',
      `raw_json` json DEFAULT NULL COMMENT '原始事件留档',
      `resolve_state` tinyint NOT NULL DEFAULT 1 COMMENT '0待裁决 1有效 2作废',
      `is_duplicate` tinyint NOT NULL DEFAULT 0 COMMENT '是否被判为重复',
      `duplicate_of` char(36) DEFAULT NULL COMMENT '重复指向的有效记录ID',
      `ingest_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '入库时间',
      PRIMARY KEY (`id`),
      UNIQUE KEY `uk_cross_origin` (`origin_site`, `origin_record_id`),
      KEY `idx_cross_align` (`student_no`, `class_name`, `course_name`, `course_date`, `time_slot`),
      KEY `idx_cross_sign_time` (`sign_time`),
      KEY `idx_cross_state` (`resolve_state`)
    ) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '跨站签到同步表'
    """,

    # 对端 pull 水位
    """
    CREATE TABLE IF NOT EXISTS `sync_cursor` (
      `peer_code` varchar(32) NOT NULL COMMENT '对端站点标识',
      `last_seq` bigint NOT NULL DEFAULT 0 COMMENT '已拉取到的对端 outbox 序号',
      `last_pull_at` datetime DEFAULT NULL COMMENT '最近一次拉取时间',
      `last_success_at` datetime DEFAULT NULL COMMENT '最近一次拉取成功时间',
      `fail_count` int NOT NULL DEFAULT 0 COMMENT '连续失败次数',
      `last_error` varchar(500) DEFAULT NULL COMMENT '最近一次错误',
      `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      PRIMARY KEY (`peer_code`)
    ) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '跨站同步游标表'
    """,

    # 待发送队列
    """
    CREATE TABLE IF NOT EXISTS `sync_outbox` (
      `id` bigint NOT NULL AUTO_INCREMENT COMMENT '队列序号（同时作为 pull 游标）',
      `target_peer` varchar(32) NOT NULL COMMENT '目标站点标识',
      `event_id` char(36) NOT NULL COMMENT '事件ID',
      `event_type` varchar(32) NOT NULL COMMENT '事件类型',
      `payload` json NOT NULL COMMENT '完整事件信封',
      `status` tinyint NOT NULL DEFAULT 0 COMMENT '0待发 1已发 2失败',
      `retry_count` int NOT NULL DEFAULT 0 COMMENT '已重试次数',
      `next_retry_at` datetime DEFAULT NULL COMMENT '下次重试时间',
      `last_error` varchar(500) DEFAULT NULL COMMENT '最近一次错误',
      `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '入队时间',
      `sent_at` datetime DEFAULT NULL COMMENT '发送成功时间',
      PRIMARY KEY (`id`),
      UNIQUE KEY `uk_outbox_event` (`target_peer`, `event_id`),
      KEY `idx_outbox_pending` (`status`, `next_retry_at`)
    ) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '跨站同步发送队列表'
    """,

    # 冲突登记
    """
    CREATE TABLE IF NOT EXISTS `cross_site_conflict` (
      `id` char(36) NOT NULL COMMENT '冲突ID',
      `align_key` varchar(255) NOT NULL COMMENT '归一化对齐键',
      `winner_record_id` varchar(64) DEFAULT NULL COMMENT '胜出记录ID',
      `winner_site` varchar(32) DEFAULT NULL COMMENT '胜出记录来源站点',
      `loser_json` json DEFAULT NULL COMMENT '落败记录（本站记录不会被改动，只在此登记）',
      `state` tinyint NOT NULL DEFAULT 0 COMMENT '0待处理 1已裁决 2忽略',
      `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
      `handled_by` char(36) DEFAULT NULL COMMENT '处理人用户ID',
      `handled_at` datetime DEFAULT NULL COMMENT '处理时间',
      PRIMARY KEY (`id`),
      KEY `idx_conflict_align` (`align_key`),
      KEY `idx_conflict_state` (`state`)
    ) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '跨站签到冲突登记表'
    """,
)


def _column_exists(cursor, table, column):
    """查 information_schema 判断列是否已存在（MySQL 8 的 ADD COLUMN 不支持 IF NOT EXISTS）"""

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = %s
          AND COLUMN_NAME = %s
        """,
        (table, column),
    )

    return cursor.fetchone()["total"] > 0


def _ensure_column(cursor, table, column, definition):
    """
    幂等补列：老库（已建过表）升级对齐键方案时需要补出 period 列
    """

    if _column_exists(cursor, table, column):
        return

    cursor.execute("ALTER TABLE `%s` ADD COLUMN %s" % (table, definition))


def ensure_sync_tables():
    """幂等创建 4 张同步表（启动时调用一次）"""

    db = get_db()

    try:
        cursor = db.cursor()

        try:
            for statement in _CREATE_STATEMENTS:
                cursor.execute(statement)

            # 对齐键从 5 段改为 4 段（学号|班级键|日期|时段档）后新增的列
            _ensure_column(
                cursor,
                "cross_site_record",
                "period",
                "`period` varchar(20) DEFAULT NULL COMMENT '时段档 morning/afternoon（对齐键组成部分）' AFTER `course_date`",
            )
        finally:
            cursor.close()
    finally:
        db.close()


# ============================================================
# 入站：写入同步表
# ============================================================

_INGEST_SQL = """
    INSERT IGNORE INTO `cross_site_record`
    (
        id,
        origin_site,
        origin_record_id,
        origin_task_id,
        student_no,
        student_name,
        class_name,
        course_name,
        course_date,
        period,
        time_slot,
        align_key,
        attendance_status,
        sign_time,
        device_id,
        ip,
        location,
        is_script,
        task_start_time,
        task_end_time,
        raw_json,
        resolve_state
    )
    VALUES
    (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
"""

# 回声检测：本站 attendance_record 里是否已有「同一学生 + 同一秒」的签到
#
# attendance_record 只有 student_id，没有学号，所以要 join 学生表。
# 命中即说明对端带回来的这条记录就是本站记录的副本（见 ingest_events 注释）。
_ECHO_CHECK_SQL = """
    SELECT ar.id
    FROM attendance_record ar
    JOIN `students` s ON s.id = ar.student_id
    WHERE s.student_no = %s
      AND ar.sign_time = %s
    LIMIT 1
"""


def resolve_local_course(cursor, class_name, course_date, period):
    """
    按（班级 + 课程日期 + 时段档）在本站 courses 表反查课程名

    对方库没有课程表、没有课程名，一天只有上午 / 下午两个场次；
    本站同一班级同一天同一时段只有一门课，所以这三个条件足以反推出课程名。

    返回 (本站班级名, 课程名)；查不到时返回 (None, None)。
    """

    date_text = normalize_date(course_date)
    period_key = normalize_period(period)
    class_key = normalize_class_key(class_name)

    if not (date_text and period_key and class_key):
        return None, None

    cursor.execute(
        """
        SELECT
            cl.name AS class_name,
            c.name AS course_name,
            c.time AS course_time
        FROM courses c

        LEFT JOIN classes cl
            ON cl.id = c.class_id

        WHERE c.course_date = %s

        ORDER BY c.time ASC
        """,
        (date_text,),
    )

    for row in cursor.fetchall():

        if normalize_class_key(row["class_name"]) != class_key:
            continue

        if normalize_period(row["course_time"]) != period_key:
            continue

        return row["class_name"], row["course_name"]

    return None, None


def ingest_events(events):
    """
    把一批入站事件写进 cross_site_record

    幂等由唯一索引 uk_cross_origin(origin_site, origin_record_id) 保证，
    配合 INSERT IGNORE 实现「重复推送不产生重复行」。

    返回 {accepted: [...], duplicated: [...], rejected: [{event_id, reason}]}
    """

    accepted = []
    duplicated = []
    rejected = []

    if not events:
        return {"accepted": accepted, "duplicated": duplicated, "rejected": rejected}

    db = get_db()

    try:
        cursor = db.cursor()

        try:
            for event in events:

                valid, reason = validate_event(event)

                if not valid:
                    rejected.append({
                        "event_id": (event or {}).get("event_id"),
                        "reason": reason,
                    })
                    continue

                origin_site = normalize_text(event.get("origin_site"))

                # 对端不应把本站的事件回传，防止自环
                if origin_site == SITE_CODE:
                    rejected.append({
                        "event_id": event.get("event_id"),
                        "reason": "origin_site 与本站相同",
                    })
                    continue

                payload = event.get("payload") or {}

                record_id = str(uuid4())

                student_no = normalize_text(payload.get("student_no"))[:32]
                sign_time = to_db_datetime(payload.get("sign_time"))

                # 回声抑制
                #
                # 本站把整库快照 push 给快照式对端后，对端落库、再整库导出时会把
                # 这些记录当成自己的数据带回来。幂等键是 (origin_site, origin_record_id)，
                # 站点不同拦不住，于是同一笔签到会多出一条「对端来源」的记录
                # （两边 sign_time / IP 完全相同）。
                #
                # 只要本站 attendance_record 里已有「同一学生 + 同一秒」的签到，
                # 就判定这条是回声：入库即置作废，并指向本站原始记录。
                # 这样它既不会参与对账取胜，也不会在前台重复展示。
                echo_of = None

                if student_no and sign_time:
                    cursor.execute(_ECHO_CHECK_SQL, (student_no, sign_time))
                    hit = cursor.fetchone()
                    if hit:
                        echo_of = hit["id"]

                # 对方库没有课程表，class_name 可能只给数字编号（2532013）、
                # 课程名也可能直接是空的：这里按（班级 + 日期 + 时段档）在本地课程表反查，
                # 补出本站班级名与课程名，只用于展示，不影响对齐
                period = normalize_period(
                    payload.get("period") or payload.get("time_slot")
                )

                local_class_name, local_course_name = resolve_local_course(
                    cursor,
                    payload.get("class_name"),
                    payload.get("course_date"),
                    period,
                )

                class_name = local_class_name or normalize_text(payload.get("class_name"))
                course_name = local_course_name or normalize_text(payload.get("course_name"))

                cursor.execute(
                    _INGEST_SQL,
                    (
                        record_id,
                        origin_site,
                        normalize_text(event.get("origin_record_id"))[:64],
                        normalize_text(event.get("origin_task_id"))[:64] or None,
                        student_no,
                        normalize_text(payload.get("student_name"))[:50] or None,
                        class_name[:50],
                        course_name[:100],
                        normalize_date(payload.get("course_date")) or None,
                        period[:20],
                        normalize_time_slot(payload.get("time_slot"))[:50],
                        align_key_of_payload(payload)[:255],
                        normalize_attendance_status(payload.get("attendance_status")),
                        sign_time,
                        normalize_text(payload.get("device_id"))[:255] or None,
                        normalize_text(payload.get("ip"))[:45] or None,
                        normalize_text(payload.get("location"))[:255] or None,
                        1 if int(payload.get("is_script") or 0) == 1 else 0,
                        to_db_datetime(payload.get("task_start_time")),
                        to_db_datetime(payload.get("task_end_time")),
                        json.dumps(event, ensure_ascii=False),
                        RESOLVE_VOID if echo_of else RESOLVE_VALID,
                    )
                )

                if cursor.rowcount == 1:

                    if echo_of:

                        # 留痕：标成重复并回指本站原始记录，便于事后排查
                        cursor.execute(
                            """
                            UPDATE `cross_site_record`
                            SET `is_duplicate` = 1, `duplicate_of` = %s
                            WHERE `id` = %s
                            """,
                            (echo_of, record_id)
                        )

                        # 不作为新的有效记录上报，避免触发无意义的一轮同步
                        duplicated.append({"event_id": event.get("event_id")})

                    else:
                        accepted.append({
                            "event_id": event.get("event_id"),
                            "record_id": record_id,
                        })
                else:
                    duplicated.append({"event_id": event.get("event_id")})
        finally:
            cursor.close()
    finally:
        db.close()

    return {"accepted": accepted, "duplicated": duplicated, "rejected": rejected}


# ============================================================
# 出站：写发送队列
# ============================================================

def build_local_signin_event(
    record_id,
    task_id,
    student_no,
    student_name,
    class_name,
    course_date,
    period,
    attendance_status,
    sign_time,
    course_name=None,
    time_slot=None,
    device_id=None,
    ip=None,
    location=None,
    is_script=0,
    task_start_time=None,
    task_end_time=None,
):
    """
    把本站的一次签到打包成同步事件

    period 是对齐键的一部分（本站由 courses.time 推导），course_name / time_slot 只用于展示。
    """

    return build_event(
        EVENT_SIGNIN,
        SITE_CODE,
        record_id,
        student_no=student_no,
        student_name=student_name,
        class_name=class_name,
        course_name=course_name,
        course_date=course_date,
        period=period,
        time_slot=time_slot,
        attendance_status=attendance_status,
        sign_time=sign_time,
        device_id=device_id,
        ip=ip,
        location=location,
        is_script=is_script,
        task_start_time=task_start_time,
        task_end_time=task_end_time,
        origin_task_id=task_id,
    )


def enqueue_event_to_peers(event):
    """
    把一条本站事件放进「每个契约式对端各一条」的待发送队列

    快照式对端（A 站）不做事件流，直接从本站导出整库快照，
    因此不给它们入队——入队只会堆出永远发不出去的行。

    返回入队的对端数量。
    """

    if not PEERS or not event:
        return 0

    db = get_db()
    queued = 0

    try:
        cursor = db.cursor()

        try:
            for peer in PEERS:

                if peer_protocol(peer) != PROTOCOL_CONTRACT:
                    continue

                cursor.execute(
                    """
                    INSERT IGNORE INTO `sync_outbox`
                    (`target_peer`, `event_id`, `event_type`, `payload`)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        peer["code"],
                        event["event_id"],
                        event["event_type"],
                        json.dumps(event, ensure_ascii=False),
                    )
                )

                queued += cursor.rowcount
        finally:
            cursor.close()
    finally:
        db.close()

    return queued


def retire_outbox_for_snapshot_peers():
    """
    把目标站点已切成快照式的历史待发行，一次性转为失败（幂等）

    这些行是按老的契约式配置入队的，现在对端不再接收事件流，
    留在队列里每轮都会白试一次；转成失败态等于显式告诉运维
    「它已被快照同步取代」，不再参与重试。

    返回被退役的行数。
    """

    peers = [peer["code"] for peer in snapshot_peers()]

    if not peers:
        return 0

    placeholders = ", ".join(["%s"] * len(peers))

    db = get_db()
    retired = 0

    try:
        cursor = db.cursor()

        try:
            cursor.execute(
                """
                UPDATE `sync_outbox`
                SET status = %s,
                    last_error = %s,
                    next_retry_at = NULL
                WHERE status = %s
                  AND target_peer IN (%s)
                """ % ("%s", "%s", "%s", placeholders),
                tuple([OUTBOX_FAILED, "目标站点已切换为快照式协议", OUTBOX_PENDING] + peers)
            )

            retired = cursor.rowcount
        finally:
            cursor.close()
    finally:
        db.close()

    return retired


def pending_outbox(limit):
    """取出到期可发送的队列行"""

    with db_cursor() as cursor:
        cursor.execute(
            """
            SELECT
                id,
                target_peer,
                event_id,
                event_type,
                payload,
                retry_count
            FROM `sync_outbox`
            WHERE status = %s
              AND (next_retry_at IS NULL OR next_retry_at <= NOW())
            ORDER BY id ASC
            LIMIT %s
            """,
            (OUTBOX_PENDING, limit)
        )

        return cursor.fetchall()


def mark_outbox_sent(outbox_id):
    """标记发送成功"""

    db = get_db()

    try:
        cursor = db.cursor()

        try:
            cursor.execute(
                """
                UPDATE `sync_outbox`
                SET status = %s, sent_at = NOW(), last_error = NULL
                WHERE id = %s
                """,
                (OUTBOX_SENT, outbox_id)
            )
        finally:
            cursor.close()
    finally:
        db.close()


def mark_outbox_rejected(outbox_id, error):
    """对端明确拒绝（如字段非法）→ 直接置为失败，重试也不会成功"""

    db = get_db()

    try:
        cursor = db.cursor()

        try:
            cursor.execute(
                """
                UPDATE `sync_outbox`
                SET status = %s, last_error = %s
                WHERE id = %s
                """,
                (OUTBOX_FAILED, str(error)[:500], outbox_id)
            )
        finally:
            cursor.close()
    finally:
        db.close()


def mark_outbox_failed(outbox_id, retry_count, error):
    """
    标记发送失败

    退避：next_retry_at = now + min(2^retry_count, 300) 秒；
    超过 MAX_RETRY 次则置为彻底失败，等待管理员手动重试。
    """

    retry_count = int(retry_count or 0) + 1

    if retry_count >= MAX_RETRY:
        next_retry = None
        status = OUTBOX_FAILED
    else:
        delay = min(2 ** retry_count, 300)
        next_retry = delay
        status = OUTBOX_PENDING

    db = get_db()

    try:
        cursor = db.cursor()

        try:
            if next_retry is None:
                cursor.execute(
                    """
                    UPDATE `sync_outbox`
                    SET status = %s, retry_count = %s, last_error = %s
                    WHERE id = %s
                    """,
                    (status, retry_count, str(error)[:500], outbox_id)
                )
            else:
                cursor.execute(
                    """
                    UPDATE `sync_outbox`
                    SET status = %s,
                        retry_count = %s,
                        last_error = %s,
                        next_retry_at = DATE_ADD(NOW(), INTERVAL %s SECOND)
                    WHERE id = %s
                    """,
                    (status, retry_count, str(error)[:500], next_retry, outbox_id)
                )
        finally:
            cursor.close()
    finally:
        db.close()


def fetch_outbound_batch(peer_code, since_id, limit=PULL_LIMIT):
    """
    提供给对端的增量拉取

    游标就是 sync_outbox.id（单调递增）。
    已发送的行也保留，因此对端离线期间的数据不会丢。
    """

    with db_cursor() as cursor:
        cursor.execute(
            """
            SELECT id, payload
            FROM `sync_outbox`
            WHERE target_peer = %s
              AND id > %s
            ORDER BY id ASC
            LIMIT %s
            """,
            (peer_code, int(since_id or 0), int(limit))
        )

        rows = cursor.fetchall()

    events = []
    next_cursor = int(since_id or 0)

    for row in rows:
        payload = row["payload"]

        if isinstance(payload, (str, bytes)):
            try:
                payload = json.loads(payload)
            except ValueError:
                continue

        events.append(payload)
        next_cursor = int(row["id"])

    return events, next_cursor


# ============================================================
# 游标
# ============================================================

def get_cursor(peer_code):
    """读取对端 pull 水位，没有记录时返回 0"""

    with db_cursor() as cursor:
        cursor.execute(
            "SELECT last_seq FROM `sync_cursor` WHERE peer_code = %s",
            (peer_code,)
        )

        row = cursor.fetchone()

    return int(row["last_seq"]) if row else 0


def save_cursor(peer_code, last_seq, success=True, error=None):
    """更新对端 pull 水位"""

    db = get_db()

    try:
        cursor = db.cursor()

        try:
            if success:
                cursor.execute(
                    """
                    INSERT INTO `sync_cursor`
                        (peer_code, last_seq, last_pull_at, last_success_at, fail_count, last_error)
                    VALUES (%s, %s, NOW(), NOW(), 0, NULL)
                    ON DUPLICATE KEY UPDATE
                        last_seq = VALUES(last_seq),
                        last_pull_at = NOW(),
                        last_success_at = NOW(),
                        fail_count = 0,
                        last_error = NULL
                    """,
                    (peer_code, int(last_seq or 0))
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO `sync_cursor`
                        (peer_code, last_seq, last_pull_at, fail_count, last_error)
                    VALUES (%s, %s, NOW(), 1, %s)
                    ON DUPLICATE KEY UPDATE
                        last_pull_at = NOW(),
                        fail_count = fail_count + 1,
                        last_error = VALUES(last_error)
                    """,
                    (peer_code, int(last_seq or 0), str(error)[:500])
                )
        finally:
            cursor.close()
    finally:
        db.close()


def cursor_snapshot():
    """各对端的同步进度快照，供管理页展示"""

    with db_cursor() as cursor:
        cursor.execute(
            """
            SELECT peer_code, last_seq, last_pull_at, last_success_at, fail_count, last_error
            FROM `sync_cursor`
            """
        )

        rows = cursor.fetchall()

    return {row["peer_code"]: row for row in rows}


# ============================================================
# 查重
# ============================================================

def find_local_duplicate(student_no, align_key):
    """
    本站签到前，先查本站 attendance_record 里有没有该学生同一门课的记录

    对齐键在字段级由 build_align_key 现算（不依赖数据库里的原始写法），
    因此这里按学号取出候选行后在内存里比对。

    返回 None 表示没有；否则返回 sign_time 最早的一条。
    """

    if not student_no or not align_key:
        return None

    with db_cursor() as cursor:
        cursor.execute(
            """
            SELECT
                ar.id AS record_id,
                ar.sign_time,
                ar.status AS attendance_status,
                s.student_no,
                s.name AS student_name,
                cl.name AS class_name,
                c.name AS course_name,
                c.course_date,
                c.time AS time_raw
            FROM attendance_record ar
            JOIN students s ON s.id = ar.student_id
            JOIN attendance_task at ON at.id = ar.task_id
            JOIN courses c ON c.id = at.course_id
            LEFT JOIN classes cl ON cl.id = s.class_id
            WHERE s.student_no = %s
            """,
            (normalize_text(student_no)[:32],)
        )

        rows = cursor.fetchall()

    best = None

    for row in rows:

        row_key = build_align_key(
            row["student_no"],
            row["class_name"],
            row["course_date"],
            row["time_raw"],
        )

        if row_key != align_key:
            continue

        if best is None or (row["sign_time"] or datetime.max) < (best["sign_time"] or datetime.max):
            best = {
                "record_id": row["record_id"],
                "sign_time": row["sign_time"],
                "attendance_status": row["attendance_status"],
                "student_name": row["student_name"],
                "course_name": row["course_name"],
            }

    return best


def find_cross_duplicate(student_no, align_key):
    """
    本站签到前，先查同步表里有没有该学生同一门课的异地记录

    返回 None 表示没有；否则返回命中的最早一条。
    """

    if not student_no or not align_key:
        return None

    with db_cursor() as cursor:
        cursor.execute(
            """
            SELECT
                origin_site,
                origin_record_id,
                course_name,
                course_date,
                period,
                time_slot,
                attendance_status,
                sign_time
            FROM `cross_site_record`
            WHERE student_no = %s
              AND align_key = %s
              AND resolve_state <> %s
            ORDER BY sign_time ASC
            LIMIT 1
            """,
            (normalize_text(student_no)[:32], align_key[:255], RESOLVE_VOID)
        )

        row = cursor.fetchone()

    return row


def cross_signs_for_student(student_no, course_date=None):
    """
    取本站同步回来的、该学生的异地签到记录（按 align_key 索引）

    供学生课程列表标记「已在其他网站签到」。

    返回 {align_key: {"origin_site": ..., "sign_time": ...}}
    """

    if not student_no:
        return {}

    with db_cursor() as cursor:
        if course_date:
            cursor.execute(
                f"""
                SELECT align_key, origin_site, sign_time
                FROM `cross_site_record`
                WHERE student_no = %s
                  AND course_date = %s
                  AND {_VALID_CROSS_CONDITION}
                """,
                (normalize_text(student_no)[:32], course_date)
            )
        else:
            cursor.execute(
                f"""
                SELECT align_key, origin_site, sign_time
                FROM `cross_site_record`
                WHERE student_no = %s
                  AND {_VALID_CROSS_CONDITION}
                """,
                (normalize_text(student_no)[:32],)
            )

        rows = cursor.fetchall()

    result = {}

    for row in rows:

        key = row["align_key"]

        if not key:
            continue

        prev = result.get(key)

        if prev is None or (row["sign_time"] or datetime.max) < (prev["sign_time"] or datetime.max):
            result[key] = {
                "origin_site": row["origin_site"],
                "sign_time": row["sign_time"],
            }

    return result


def cross_signs_for_course(course_date):
    """
    取某一天本站同步回来的所有异地签到（按 align_key 索引）

    供教师名册标记「已在其他网站签到」。

    align_key 已经包含「学号|班级键|日期|时段档」，教师侧只要用
    （学号 + 本班班级名 + 课程日期 + 课程时段档）算出同一个键就能命中，
    所以这里不需要再按班级名 / 课程名过滤。

    返回 {align_key: {"origin_site", "sign_time", "student_no", "attendance_status"}}
    """

    if not course_date:
        return {}

    with db_cursor() as cursor:
        cursor.execute(
            f"""
            SELECT
                align_key,
                student_no,
                origin_site,
                sign_time,
                attendance_status,
                student_name,
                class_name,
                period,
                course_name,
                course_date
            FROM `cross_site_record`
            WHERE course_date = %s
              AND {_VALID_CROSS_CONDITION}
            """,
            (
                normalize_date(course_date),
            )
        )

        rows = cursor.fetchall()

    result = {}

    for row in rows:

        key = row["align_key"] or build_align_key(
            row["student_no"],
            row["class_name"],
            row["course_date"],
            row["period"],
        )

        if not key:
            continue

        prev = result.get(key)

        if prev is None or (row["sign_time"] or datetime.max) < (prev["sign_time"] or datetime.max):
            result[key] = {
                "origin_site": row["origin_site"],
                "sign_time": row["sign_time"],
                "student_no": row["student_no"],
                "attendance_status": row["attendance_status"],
            }

    return result


# ============================================================
# 跨站签到读路径（进度 / 统计 / 学生明细共用同一口径）
# ============================================================

def count_signed_students(task_id, class_id, course_date, period):
    """
    进度口径：本站签到 ∪ 有效外部签到，按学号去重计数

    外部记录按（课程日期 + 时段档）匹配，且学号属于该班级；
    时段档沿用 sync.contract.normalize_period，避免另造规则对不上。
    """

    if not (task_id and class_id and course_date):
        return 0

    period_key = normalize_period(period) or None

    with db_cursor() as cursor:
        cursor.execute(
            f"""
            SELECT COUNT(*) AS signed_count
            FROM (
                SELECT s.student_no AS student_no
                FROM attendance_record ar
                INNER JOIN students s ON s.id = ar.student_id
                WHERE ar.task_id = %s
                UNION
                SELECT csr.student_no AS student_no
                FROM cross_site_record csr
                WHERE {_VALID_CROSS_CONDITION}
                  AND csr.course_date = %s
                  AND csr.period = %s
                  AND csr.student_no IN (
                      SELECT s2.student_no FROM students s2 WHERE s2.class_id = %s
                  )
            ) u
            """,
            (task_id, course_date, period_key, class_id),
        )

        row = cursor.fetchone()
        return int(row["signed_count"] or 0) if row else 0


def attendance_status_counts(task_id, class_id, course_date, period):
    """
    统计口径：本站签到 ∪ 有效外部签到，按学生去重（本站优先），返回 {状态: 人数}

    同一学生本地与外部都有时只留本地（外部子查询排除本 task 已有本地记录的学生）。
    """

    counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}

    if not (task_id and class_id and course_date):
        return counts

    period_key = normalize_period(period) or None

    with db_cursor() as cursor:
        cursor.execute(
            f"""
            SELECT u.status AS status, COUNT(*) AS cnt
            FROM (
                SELECT s.student_no AS student_no,
                       MIN(ar.status) AS status
                FROM attendance_record ar
                INNER JOIN students s ON s.id = ar.student_id
                WHERE ar.task_id = %s
                GROUP BY s.student_no
                UNION
                SELECT csr.student_no AS student_no,
                       MIN(csr.attendance_status) AS status
                FROM cross_site_record csr
                WHERE {_VALID_CROSS_CONDITION}
                  AND csr.course_date = %s
                  AND csr.period = %s
                  AND csr.student_no IN (
                      SELECT s2.student_no FROM students s2 WHERE s2.class_id = %s
                  )
                  AND csr.student_no NOT IN (
                      SELECT s3.student_no
                      FROM attendance_record ar3
                      INNER JOIN students s3 ON s3.id = ar3.student_id
                      WHERE ar3.task_id = %s
                  )
                GROUP BY csr.student_no
            ) u
            WHERE u.status IS NOT NULL
            GROUP BY u.status
            """,
            (task_id, course_date, period_key, class_id, task_id),
        )

        for row in cursor.fetchall():
            status = row["status"]
            if status in counts:
                counts[int(status)] += int(row["cnt"] or 0)

    return counts


def cross_records_for_student(student_no, date_filter=None):
    """
    取该学生同步回来的有效异地签到明细（用于「我的记录」列表）

    只保留 _VALID_CROSS_CONDITION 命中的行：作废行（含回声副本）不出现，
    否则同一笔签到会在学生历史里显示两遍。
    """

    if not student_no:
        return []

    with db_cursor() as cursor:
        sql = f"""
            SELECT
                id,
                origin_site,
                class_name,
                course_name,
                course_date,
                period,
                time_slot,
                attendance_status,
                sign_time,
                device_id,
                location,
                ip,
                is_script
            FROM `cross_site_record`
            WHERE student_no = %s
              AND {_VALID_CROSS_CONDITION}
        """

        params = [normalize_text(student_no)[:32]]

        if date_filter:
            sql += " AND DATE(sign_time) = %s"
            params.append(date_filter)

        sql += " ORDER BY sign_time DESC"

        cursor.execute(sql, tuple(params))

        return list(cursor.fetchall())


# ============================================================
# 对账
# ============================================================

def _local_align_rows(cursor, student_nos):
    """按学号批量取出本站签到记录，并算出对齐键"""

    if not student_nos:
        return []

    placeholders = ",".join(["%s"] * len(student_nos))

    cursor.execute(
        f"""
        SELECT
            ar.id AS record_id,
            ar.sign_time,
            ar.status,
            s.student_no,
            s.name AS student_name,
            cl.name AS class_name,
            c.name AS course_name,
            c.course_date,
            c.time AS time_raw
        FROM attendance_record ar
        JOIN students s ON s.id = ar.student_id
        JOIN attendance_task at ON at.id = ar.task_id
        JOIN courses c ON c.id = at.course_id
        LEFT JOIN classes cl ON cl.id = s.class_id
        WHERE s.student_no IN ({placeholders})
          AND c.course_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
        """,
        tuple(student_nos) + (RECONCILE_DAYS,)
    )

    rows = cursor.fetchall()
    result = []

    for row in rows:
        result.append({
            "kind": "local",
            "id": row["record_id"],
            "origin_site": SITE_CODE,
            "origin_record_id": row["record_id"],
            "sign_time": row["sign_time"],
            "student_name": row["student_name"],
            "attendance_status": row["status"],
            "align_key": build_align_key(
                row["student_no"],
                row["class_name"],
                row["course_date"],
                row["time_raw"],
            ),
        })

    return result


def reconcile():
    """
    对账：找出「同一学生 + 同一门课」下跨站的重复签到

    裁决规则（三站结果一致）：
        sign_time 最早者胜；时间相同时依次比较 origin_site 升序、origin_record_id 升序。

    处理后：
        - 落败的异地记录 → resolve_state = 作废，并记录 duplicate_of
        - 落败的本站记录 → 本站数据一律不动，只在 cross_site_conflict 登记，交人工处理
        - 同一站内部的重复不处理（交给该站自身的查重逻辑，避免多任务课程误判）
    """

    db = get_db()

    stats = {"groups": 0, "voided": 0, "conflicts": 0}

    try:
        cursor = db.cursor()

        try:
            cursor.execute(
                """
                SELECT
                    id,
                    origin_site,
                    origin_record_id,
                    student_no,
                    student_name,
                    class_name,
                    course_name,
                    course_date,
                    period,
                    time_slot,
                    align_key,
                    attendance_status,
                    sign_time
                FROM `cross_site_record`
                WHERE resolve_state <> %s
                  AND sign_time >= DATE_SUB(NOW(), INTERVAL %s DAY)
                """,
                (RESOLVE_VOID, RECONCILE_DAYS)
            )

            cross_rows = cursor.fetchall()

            if not cross_rows:
                return stats

            student_nos = sorted({
                normalize_text(row["student_no"]) for row in cross_rows if row["student_no"]
            })

            groups = {}

            for row in _local_align_rows(cursor, student_nos):
                groups.setdefault(row["align_key"], []).append(row)

            for row in cross_rows:

                align_key = row["align_key"] or build_align_key(
                    row["student_no"],
                    row["class_name"],
                    row["course_date"],
                    row["period"],
                )

                groups.setdefault(align_key, []).append({
                    "kind": "cross",
                    "id": row["id"],
                    "origin_site": row["origin_site"],
                    "origin_record_id": row["origin_record_id"],
                    "sign_time": row["sign_time"],
                    "student_name": row["student_name"],
                    "attendance_status": row["attendance_status"],
                    "align_key": align_key,
                })

            for align_key, candidates in groups.items():

                if len(candidates) < 2:
                    continue

                # 只有涉及两个及以上站点的才判为跨站重复
                if len({c["origin_site"] for c in candidates}) < 2:
                    continue

                stats["groups"] += 1

                winner = min(
                    candidates,
                    key=lambda c: (
                        c["sign_time"] or datetime.max,
                        # 同秒平局本站优先
                        #
                        # 物理上一个学生不可能在同一秒于两个站点各签一次，
                        # 出现同秒只可能是同一笔签到的副本（例如快照回声）。
                        # 所以平局以本部数据为准，不再按 origin_site 字典序
                        # （"site_a" < "site_local" 会让本站记录永远落败）。
                        0 if c["kind"] == "local" else 1,
                        c["origin_site"] or "",
                        str(c["origin_record_id"] or ""),
                    )
                )

                losers = [c for c in candidates if c is not winner]

                cross_losers = [c for c in losers if c["kind"] == "cross"]
                local_losers = [c for c in losers if c["kind"] == "local"]

                for loser in cross_losers:

                    cursor.execute(
                        """
                        UPDATE `cross_site_record`
                        SET resolve_state = %s,
                            is_duplicate = 1,
                            duplicate_of = %s
                        WHERE id = %s
                        """,
                        (RESOLVE_VOID, winner["id"], loser["id"])
                    )

                    stats["voided"] += 1

                if local_losers:

                    # 同一 align_key + 同一胜出记录只要登记过（不论待处理 / 已裁决 / 已忽略）
                    # 就不再重复登记。否则用户每次处理完，下一轮对账又会把同一条重新
                    # 变成「待处理」，逼用户反复评判。
                    # 若胜出记录变了（例如对端改了签到时间导致胜方翻转），视为新冲突，重新登记。
                    cursor.execute(
                        """
                        SELECT COUNT(*) AS cnt
                        FROM `cross_site_conflict`
                        WHERE align_key = %s AND winner_record_id = %s
                        """,
                        (align_key[:255], str(winner["id"]))
                    )

                    exists = cursor.fetchone()

                    if not exists or exists["cnt"] == 0:

                        cursor.execute(
                            """
                            INSERT INTO `cross_site_conflict`
                            (`id`, `align_key`, `winner_record_id`, `winner_site`, `loser_json`, `state`)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            """,
                            (
                                str(uuid4()),
                                align_key[:255],
                                str(winner["id"]),
                                winner["origin_site"],
                                json.dumps({
                                    "winner": {
                                        "site": winner["origin_site"],
                                        "record_id": winner["id"],
                                        "sign_time": str(winner["sign_time"] or ""),
                                    },
                                    "losers": [
                                        {
                                            "site": c["origin_site"],
                                            "record_id": c["id"],
                                            "sign_time": str(c["sign_time"] or ""),
                                            "attendance_status": c["attendance_status"],
                                        }
                                        for c in local_losers
                                    ],
                                }, ensure_ascii=False),
                                CONFLICT_PENDING,
                            )
                        )

                        stats["conflicts"] += 1
        finally:
            cursor.close()
    finally:
        db.close()

    return stats


# ============================================================
# 管理页辅助查询
# ============================================================

def outbox_stats():
    """队列统计"""

    with db_cursor() as cursor:
        cursor.execute(
            """
            SELECT status, COUNT(*) AS cnt
            FROM `sync_outbox`
            GROUP BY status
            """
        )

        rows = cursor.fetchall()

    stats = {OUTBOX_PENDING: 0, OUTBOX_SENT: 0, OUTBOX_FAILED: 0}

    for row in rows:
        stats[int(row["status"])] = int(row["cnt"])

    return stats


def list_outbox(status=None, limit=100):
    """队列明细"""

    with db_cursor() as cursor:
        if status is None:
            cursor.execute(
                """
                SELECT id, target_peer, event_id, event_type, status,
                       retry_count, next_retry_at, last_error, created_at, sent_at
                FROM `sync_outbox`
                ORDER BY id ASC
                LIMIT %s
                """,
                (int(limit),)
            )
        else:
            cursor.execute(
                """
                SELECT id, target_peer, event_id, event_type, status,
                       retry_count, next_retry_at, last_error, created_at, sent_at
                FROM `sync_outbox`
                WHERE status = %s
                ORDER BY id ASC
                LIMIT %s
                """,
                (int(status), int(limit))
            )

        return cursor.fetchall()


def retry_outbox(outbox_id):
    """手动重试一条失败队列"""

    db = get_db()

    try:
        cursor = db.cursor()

        try:
            cursor.execute(
                """
                UPDATE `sync_outbox`
                SET status = %s, retry_count = 0, next_retry_at = NOW(), last_error = NULL
                WHERE id = %s
                """,
                (OUTBOX_PENDING, int(outbox_id))
            )

            return cursor.rowcount
        finally:
            cursor.close()
    finally:
        db.close()


def count_pending_outbox():
    """待发送条数（含到期与未到期）"""

    with db_cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) AS cnt FROM `sync_outbox` WHERE status = %s",
            (OUTBOX_PENDING,)
        )

        row = cursor.fetchone()

    return int(row["cnt"]) if row else 0


def _conflict_filters(state, keyword):
    """把（状态 / 关键字）拼成 WHERE 子句与参数，供列表与计数共用"""

    clauses = []
    params = []

    if state is not None:
        clauses.append("`state` = %s")
        params.append(int(state))

    keyword = normalize_text(keyword)

    if keyword:
        clauses.append("`align_key` LIKE %s")
        params.append("%" + keyword + "%")

    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""

    return where, params


def list_conflicts(state=None, limit=100, keyword=None):
    """
    冲突列表

    state 为 None 时不过滤状态；keyword 按对齐键模糊匹配
    （对齐键是 学号|班级键|日期|时段档，筛学号或日期都走这里）。
    """

    where, params = _conflict_filters(state, keyword)

    with db_cursor() as cursor:
        cursor.execute(
            """
            SELECT id, align_key, winner_record_id, winner_site,
                   loser_json, state, created_at, handled_by, handled_at
            FROM `cross_site_conflict`
            """ + where + """
            ORDER BY created_at DESC
            LIMIT %s
            """,
            tuple(params + [int(limit)])
        )

        return cursor.fetchall()


def count_conflicts(state=None, keyword=None):
    """冲突总数，与 list_conflicts 用同一套筛选条件"""

    where, params = _conflict_filters(state, keyword)

    with db_cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) AS cnt FROM `cross_site_conflict`" + where,
            tuple(params)
        )

        row = cursor.fetchone()

    return int(row["cnt"]) if row else 0


def handle_conflicts(action, user_id, ids=None):
    """
    批量处理冲突

    ids 为空（None / []）时处理全部「待处理」的行，否则只处理指定 id。
    action = resolve（已裁决）/ ignore（忽略）；返回受影响行数。
    """

    state = CONFLICT_RESOLVED if action == "resolve" else CONFLICT_IGNORED

    clean_ids = [text for text in (normalize_text(value) for value in (ids or [])) if text]

    sql = """
        UPDATE `cross_site_conflict`
        SET state = %s, handled_by = %s, handled_at = NOW()
        WHERE state = %s
    """

    params = [state, user_id, CONFLICT_PENDING]

    if clean_ids:
        sql += "  AND `id` IN (%s)" % ", ".join(["%s"] * len(clean_ids))
        params.extend(clean_ids)

    db = get_db()

    try:
        cursor = db.cursor()

        try:
            cursor.execute(sql, tuple(params))

            return cursor.rowcount
        finally:
            cursor.close()
    finally:
        db.close()


def count_pending_conflicts():
    """未处理冲突数"""

    with db_cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) AS cnt FROM `cross_site_conflict` WHERE state = %s",
            (CONFLICT_PENDING,)
        )

        row = cursor.fetchone()

    return int(row["cnt"]) if row else 0


def handle_conflict(conflict_id, action, user_id):
    """
    处理冲突

    action = resolve（已裁决）/ ignore（忽略）
    """

    state = CONFLICT_RESOLVED if action == "resolve" else CONFLICT_IGNORED

    db = get_db()

    try:
        cursor = db.cursor()

        try:
            cursor.execute(
                """
                UPDATE `cross_site_conflict`
                SET state = %s, handled_by = %s, handled_at = NOW()
                WHERE id = %s AND state = %s
                """,
                (state, user_id, conflict_id, CONFLICT_PENDING)
            )

            return cursor.rowcount
        finally:
            cursor.close()
    finally:
        db.close()


def cross_record_count():
    """同步表总量，用于管理页概览"""

    with db_cursor() as cursor:
        cursor.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN resolve_state = 2 THEN 1 ELSE 0 END) AS voided
            FROM `cross_site_record`
            """
        )

        row = cursor.fetchone()

    return {
        "total": int(row["total"] or 0) if row else 0,
        "voided": int(row["voided"] or 0) if row else 0,
    }
