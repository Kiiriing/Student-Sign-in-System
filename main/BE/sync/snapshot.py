# -*- coding: utf-8 -*-
# sync/snapshot.py
# 跨站签到同步 · 整库快照形态
#
# 对接不实现契约四接口、只提供整库快照的对端（A 站）：
#
#   我方导出：build_snapshot()            → A 站 GET /api/sync/export 的格式
#   我方入账：import_snapshot(snapshot)    → A 站 POST /api/sync/import 的格式
#
# 入账不写本地考勤表：快照里的 records 会先转成契约事件（build_event），
# 再走 sync.store.ingest_events() 落进独立的 cross_site_record，
# 这样展示层、签到查重、对账三处既有逻辑全部照常生效。

import hashlib

from datetime import datetime, timedelta

from core.database import get_db

from sync.config import RECONCILE_DAYS
from sync.contract import (
    EVENT_SIGNIN,
    build_event,
    normalize_attendance_status,
    normalize_class_key,
    normalize_period,
    normalize_text,
    normalize_time_slot,
    to_db_datetime,
)
from sync.store import ingest_events


# ============================================================
# 常量
# ============================================================

SNAPSHOT_VERSION = 1

# 本站 status(1~6) → 对端 enum(normal/late/absent)
#
# 4早退 / 5病假 / 6事假 在对端枚举里没有对应取值，一律按 normal 上报：
# 映射成 absent 等于把请假误判成旷课，错判比丢细分严重。
_REMOTE_STATUS = {
    1: "normal",
    2: "late",
    3: "absent",
}

_REMOTE_STATUS_DEFAULT = "normal"

# 快照里的班级键必须是纯数字，超过 int 安全范围时改用哈希
_MAX_CLASS_DIGITS = 9


# ============================================================
# 小工具
# ============================================================

def _list(value):
    """把响应里的段取成列表，缺失或类型不对时返回空列表"""

    return value if isinstance(value, list) else []


def _stamp(value):
    """datetime → A 站快照使用的时间写法（不带时区偏移）"""

    if value is None:
        return None

    return value.strftime("%Y-%m-%dT%H:%M:%S")


def _second_text(value):
    """时间值 → 精确到秒的文本，用于合成幂等键"""

    parsed = to_db_datetime(value)

    if parsed is None:
        return normalize_text(value)

    return parsed.strftime("%Y-%m-%d %H:%M:%S")


def _split_time_slot(text):
    """课程时间段「08:30-11:50」→ (开始, 结束)；解析不出时返回 (None, None)"""

    normalized = normalize_time_slot(text)

    if "-" not in normalized:
        return None, None

    start, _, end = normalized.partition("-")

    return start.strip() or None, end.strip() or None


def _day_start(date_text, time_text):
    """「2026-10-12」+「08:30」→ datetime"""

    if not date_text or not time_text:
        return None

    return to_db_datetime("%s %s" % (date_text, time_text))


# ============================================================
# 字段映射
# ============================================================

def class_id_of(class_name):
    """班级名 → 对端使用的纯数字 class_id

    优先取班级名里的长数字串（大数据2532013 → 2532013），与对方库的
    class_id 直接对上；班级名里没有长数字串时（软件2401班），用稳定哈希
    折成一个正整数——同一班级名恒等映射、不同班级不会撞车。

    另外：对端 class_id 是 int 列，数字串过长时同样走哈希，避免溢出。
    """

    key = normalize_class_key(class_name)

    if key.isdigit() and len(key) <= _MAX_CLASS_DIGITS:
        return int(key)

    if not key:
        return 0

    return int(hashlib.md5(key.encode("utf-8")).hexdigest()[:8], 16)


def status_to_remote(status):
    """本站 status(1~6) → 对端 enum(normal/late/absent)"""

    return _REMOTE_STATUS.get(
        normalize_attendance_status(status),
        _REMOTE_STATUS_DEFAULT,
    )


def source_of(is_script, device_id):
    """本站记录 → 对端 source 取值（manual 手动 / auto 自动 / script 脚本）"""

    if int(is_script or 0) == 1:
        return "script"

    return "manual" if normalize_text(device_id) else "auto"


def snapshot_record_id(student_no, check_in_time, period):
    """给快照里没有主键的 records 合成一个稳定的幂等键

    对端导出的 records 不带记录主键，而 cross_site_record 的唯一键是
    (origin_site, origin_record_id)，不合成稳定值就谈不上幂等。

    只用「签到时间」做键是不行的：同一秒会有多名学生签到，
    唯一索引 + INSERT IGNORE 会把不同人的记录当成重复静默丢弃。
    这里把学号一起放进哈希，冲突面收敛到「同一人同一秒」。
    """

    raw = "%s|%s|%s" % (
        normalize_text(student_no),
        _second_text(check_in_time),
        normalize_period(period),
    )

    return "snap-" + hashlib.md5(raw.encode("utf-8")).hexdigest()[:16]


# ============================================================
# 导出：本站 → 快照
# ============================================================

def _snapshot_students(cursor):
    """学生段：学号、姓名、纯数字班级编号、班内名册序号"""

    cursor.execute(
        """
        SELECT
            s.student_no AS student_no,
            s.name AS student_name,
            cl.name AS class_name
        FROM `students` s

        LEFT JOIN `classes` cl
            ON cl.id = s.class_id

        WHERE s.student_no IS NOT NULL
          AND s.student_no <> ''

        ORDER BY cl.name ASC, s.student_no ASC
        """
    )

    rows = []
    seq_by_class = {}

    for row in cursor.fetchall():

        class_key = normalize_class_key(row["class_name"])
        seq = seq_by_class.get(class_key, 0) + 1
        seq_by_class[class_key] = seq

        rows.append({
            "name": row["student_name"],
            "student_id": row["student_no"],
            "class_id": class_id_of(row["class_name"]),
            "seq": seq,
        })

    return rows


def _snapshot_sessions(cursor, since_date):
    """场次段：由本站 courses 推导（本站没有独立的签到场次表）

    一场 = 一个班级某天某个时间段，正好对应对方「上午场 / 下午场」的粒度。
    location / client_ip 本站没有对应列，按 null 上报。
    """

    cursor.execute(
        """
        SELECT
            cl.name AS class_name,
            c.course_date AS course_date,
            c.time AS course_time
        FROM `courses` c

        LEFT JOIN `classes` cl
            ON cl.id = c.class_id

        WHERE c.course_date >= %s

        ORDER BY cl.name ASC, c.course_date ASC, c.time ASC
        """,
        (since_date,),
    )

    now = datetime.now()
    sessions = []

    for row in cursor.fetchall():

        start_time, end_time = _split_time_slot(row["course_time"])

        start_at = _day_start(row["course_date"], start_time)
        end_at = _day_start(row["course_date"], end_time)

        sessions.append({
            "class_id": class_id_of(row["class_name"]),
            "start_time": _stamp(start_at),
            "end_time": _stamp(end_at),
            "location": None,
            "client_ip": None,
            "is_active": bool(start_at and end_at and start_at <= now <= end_at),
        })

    return sessions


def _snapshot_records(cursor, since_date):
    """签到记录段：student_id 用学号（不是本地主键），与对端约定一致"""

    cursor.execute(
        """
        SELECT
            s.student_no AS student_no,
            ar.sign_time AS sign_time,
            ar.status AS status,
            ar.ip AS ip,
            ar.device_id AS device_id,
            ar.location AS location,
            ar.is_script AS is_script,
            c.time AS course_time
        FROM `attendance_record` ar

        JOIN `students` s
            ON s.id = ar.student_id

        JOIN `attendance_task` at
            ON at.id = ar.task_id

        JOIN `courses` c
            ON c.id = at.course_id

        WHERE ar.sign_time >= %s

        ORDER BY ar.sign_time ASC
        """,
        (since_date,),
    )

    records = []

    for row in cursor.fetchall():

        sign_time = row["sign_time"]

        records.append({
            "student_id": row["student_no"],
            "check_in_time": _stamp(sign_time),
            "status": status_to_remote(row["status"]),
            "period": normalize_period(row["course_time"]),
            "source": source_of(row["is_script"], row["device_id"]),
            "client_ip": row["ip"],
            "client_fp": None,
            "is_script": bool(int(row["is_script"] or 0)),
            "location": row["location"],
            "device_fp": row["device_id"],
            "suspicious": False,
            "suspicious_reason": None,
        })

    return records


def build_snapshot(days=RECONCILE_DAYS):
    """导出本站整库快照（对端 /api/sync/export 的格式）

    只覆盖最近 days 天的课程与签到：对端是「全量 + 判重」的合并模型，
    窗口太小会漏数据，窗口太大又会让每轮同步的报文无限增长。
    """

    since = datetime.now().date() - timedelta(days=int(days))
    since_date = since.strftime("%Y-%m-%d")

    db = get_db()

    try:
        cursor = db.cursor()

        try:
            students = _snapshot_students(cursor)
            sessions = _snapshot_sessions(cursor, since_date)
            records = _snapshot_records(cursor, since_date)
        finally:
            cursor.close()
    finally:
        db.close()

    return {
        "version": SNAPSHOT_VERSION,
        "exported_at": _stamp(datetime.now()),
        "students": students,
        "sessions": sessions,
        "records": records,
    }


# ============================================================
# 入账：快照 → 本站同步表
# ============================================================

def _class_of_student(snapshot):
    """{学号: 班级键文本}；对端 records 不带班级，只能从 students 段取"""

    mapping = {}

    for item in _list(snapshot.get("students")):

        student_no = normalize_text(item.get("student_id"))

        if student_no:
            mapping[student_no] = normalize_text(item.get("class_id"))

    return mapping


def _time_slots_of_sessions(snapshot):
    """{(班级键, 日期): 时间段}，用对端 sessions 段给 records 补展示用时间段"""

    slots = {}

    for item in _list(snapshot.get("sessions")):

        class_key = normalize_class_key(item.get("class_id"))
        start_at = to_db_datetime(item.get("start_time"))
        end_at = to_db_datetime(item.get("end_time"))

        if not class_key or start_at is None:
            continue

        if end_at is None:
            slots.setdefault((class_key, start_at.strftime("%Y-%m-%d")), "")
            continue

        slots[(class_key, start_at.strftime("%Y-%m-%d"))] = "%02d:%02d-%02d:%02d" % (
            start_at.hour, start_at.minute, end_at.hour, end_at.minute,
        )

    return slots


def _period_of(item, sign_time):
    """时段档：优先用对端给的 period，缺省时按签到时间的小时判断"""

    period = normalize_period(item.get("period"))

    if period:
        return period

    return "morning" if sign_time.hour < 12 else "afternoon"


def _records_to_events(snapshot, origin_site):
    """快照 records → (学号, 契约事件) 列表；字段不全的记录直接跳过"""

    class_of = _class_of_student(snapshot)
    slots = _time_slots_of_sessions(snapshot)

    pairs = []

    for item in _list(snapshot.get("records")):

        student_no = normalize_text(item.get("student_id"))
        sign_time = to_db_datetime(item.get("check_in_time"))

        if not student_no or sign_time is None:
            continue

        class_name = class_of.get(student_no) or ""
        period = _period_of(item, sign_time)

        pairs.append((student_no, build_event(
            EVENT_SIGNIN,
            origin_site,
            snapshot_record_id(student_no, sign_time, period),
            student_no=student_no,
            class_name=class_name,
            course_date=sign_time.date(),
            period=period,
            attendance_status=item.get("status"),
            sign_time=sign_time,
            time_slot=slots.get(
                (normalize_class_key(class_name), sign_time.strftime("%Y-%m-%d")),
                "",
            ),
            device_id=item.get("device_fp"),
            ip=item.get("client_ip"),
            location=item.get("location"),
            is_script=1 if item.get("is_script") else 0,
        )))

    return pairs


def snapshot_to_events(snapshot, origin_site):
    """把一份整库快照转成契约事件列表"""

    return [event for _student_no, event in _records_to_events(snapshot, origin_site)]


def import_snapshot(snapshot, origin_site):
    """把一份整库快照入账进 cross_site_record

    只取 records 段：students / sessions 用于补班级键与展示用时间段，
    本站不为对端的学生建本地档案（那属于本地管理流程的事）。

    返回对端 /api/sync/import 的计数口径，方便对方核对。
    """

    if not isinstance(snapshot, dict):
        return {
            "success": False,
            "created_students": 0,
            "skipped_students": 0,
            "created_sessions": 0,
            "skipped_sessions": 0,
            "created_records": 0,
            "skipped_records": 0,
            "errors": ["快照不是 JSON 对象"],
        }

    pairs = _records_to_events(snapshot, origin_site)

    result = ingest_events([event for _student_no, event in pairs])

    by_event_id = {
        event["event_id"]: student_no
        for student_no, event in pairs
    }

    errors = []

    for rejected in result["rejected"]:

        student_no = by_event_id.get(rejected.get("event_id"))

        if student_no:
            errors.append("签到记录 %s：%s" % (student_no, rejected.get("reason")))
        else:
            errors.append(str(rejected.get("reason")))

    students = _list(snapshot.get("students"))
    sessions = _list(snapshot.get("sessions"))

    return {
        "success": True,
        "created_students": 0,
        "skipped_students": len(students),
        "created_sessions": 0,
        "skipped_sessions": len(sessions),
        "created_records": len(result["accepted"]),
        "skipped_records": len(result["duplicated"]),
        "errors": errors,
    }
