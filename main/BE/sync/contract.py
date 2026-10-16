# -*- coding: utf-8 -*-
# sync/contract.py
# 跨站签到数据同步 · 契约层
#
# 本文件是三站之间唯一的「约定」来源，职责有三：
#
#   1. 定义共用的归一化规则
#   2. 生成对齐键 align_key（只用于匹配与对账，不加唯一约束）
#   3. 构造 / 校验同步事件信封
#
# 重点：本文件的归一化实现属于契约的一部分。
#       另外两站必须照抄同样的规则，否则同一门课会对不上。

import re

from datetime import datetime
from uuid import uuid4


# ============================================================
# 常量
# ============================================================

SCHEMA_VERSION = "1.0"

# 事件类型
EVENT_SIGNIN = "attendance.signin"
EVENT_UPDATE = "attendance.update"
EVENT_DELETE = "attendance.delete"

EVENT_TYPES = (EVENT_SIGNIN, EVENT_UPDATE, EVENT_DELETE)

# 对齐键分隔符；各组成部分都会被归一化，理论上不会引入该字符
ALIGN_SEP = "|"

# 签到状态：与本地 attendance_record.status 语义完全一致
STATUS_TEXT = {
    1: "正常",
    2: "迟到",
    3: "旷课",
    4: "早退",
    5: "病假",
    6: "事假",
}

# 对方库的 status 是 enum('normal','late','absent')，这里做一层别名映射，
# 让对方的接入层可以直接把库里的原始值塞进事件，不必自己翻译
STATUS_ALIAS = {
    "normal": 1,
    "正常": 1,
    "late": 2,
    "迟到": 2,
    "absent": 3,
    "旷课": 3,
    "缺勤": 3,
    "early": 4,
    "早退": 4,
    "sick": 5,
    "病假": 5,
    "leave": 6,
    "事假": 6,
}

# 本地时区（三站同处一个局域网，共用同一时区）
LOCAL_TZ = datetime.now().astimezone().tzinfo

_TIME_RE = re.compile(r"(\d{1,2})\s*[:：]\s*(\d{1,2})")

# 班级名里的长数字串（如「大数据2532013」→ 2532013）
#
# 只在数字长度 >= 6 时才当作班级编码，否则退回完整班级名。
# 这样可以对上「对方只存数字编号（2532013）」与「本站班级名带中文前缀（大数据2532013）」，
# 又不会让「软件2401班 / 计算机2401班」这类短编号互相撞车。
_LONG_DIGITS_RE = re.compile(r"\d{6,}")

# 时段档：把 morning/afternoon、上午/下午、以及 08:30-11:50 这类时间范围统一成两个档位。
#
# 对方的签到表只有 morning / afternoon 两档（一天一场，不分课程），
# 本站课程时间段需要按开始时间归到同一档，两侧才能对上。
#
# 注意：只匹配完整英文单词与中文词，不匹配 "am"/"pm"，
# 否则 "exam"（考试）这类含 "am" 的文本会被误判成上午。
_PERIOD_WORDS = (
    ("afternoon", ("afternoon", "下午", "午后")),
    ("morning", ("morning", "上午", "早上", "清晨")),
)


# ============================================================
# 归一化
# ============================================================

def normalize_text(value):
    """
    文本归一化：去首尾空白、把全角空格折成半角、把连续空白折成单个空格

    三站必须使用完全相同的实现。
    """

    if value is None:
        return ""

    text = str(value).replace("\u3000", " ")

    return " ".join(text.split()).strip()


def normalize_time_slot(value):
    """
    时间段归一化

    支持 '13:30-17:00' / '13:30~17:00' / '13:30 至 17:00' / '13：30-17：00'
    统一输出为 'HH:MM-HH:MM'

    识别不出两个时间点时，退回「去空白 + 统一分隔符」的文本形式。
    """

    if value is None:
        return ""

    text = str(value)

    found = _TIME_RE.findall(text)

    if len(found) >= 2:
        return "%02d:%02d-%02d:%02d" % (
            int(found[0][0]), int(found[0][1]),
            int(found[1][0]), int(found[1][1]),
        )

    fallback = normalize_text(text).replace(" ", "")

    for sep in ("~", "至", "—", "－", "到"):

        if sep in fallback:
            fallback = fallback.replace(sep, "-")

    return fallback


def normalize_date(value):
    """日期归一化，统一输出 'YYYY-MM-DD'"""

    if value is None:
        return ""

    if hasattr(value, "strftime"):
        try:
            return value.strftime("%Y-%m-%d")
        except (AttributeError, ValueError):
            return ""

    text = normalize_text(value)

    if not text:
        return ""

    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d", "%Y%m%d"):

        try:
            return datetime.strptime(text[:10], fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    return text[:10]


def normalize_period(value):
    """
    时段档归一化

    统一输出 'morning' / 'afternoon'，识别不出来时返回 ''。

    支持三种写法：

      * 'morning' / 'afternoon'
      * '上午' / '下午'
      * '08:30-11:50' / '13:30-17:00'（按第一个时间点所在的小时判断）
    """

    if value is None:
        return ""

    text = normalize_text(value).lower()

    if not text:
        return ""

    for period, words in _PERIOD_WORDS:

        for word in words:

            if word in text:
                return period

    # 退化为解析时间范围：以开始时间是否早于 12:00 判断上下午
    found = _TIME_RE.search(text)

    if found:

        hour = int(found.group(1))

        return "morning" if hour < 12 else "afternoon"

    return ""


def normalize_attendance_status(value):
    """
    签到状态归一化 → STATUS_TEXT 里的整数（1~6）

    数字（含数字字符串）直接校验取值；文本走 STATUS_ALIAS 别名映射。

    这样对方可以直接把库里 enum('normal','late','absent') 的原始值塞进事件，
    不需要自己翻译成整数。
    """

    if value is None or value == "":
        return None

    if isinstance(value, bool):
        return None

    if isinstance(value, (int, float)):

        number = int(value)

        return number if number in STATUS_TEXT else None

    text = normalize_text(value).lower()

    if not text:
        return None

    if text.isdigit():

        number = int(text)

        return number if number in STATUS_TEXT else None

    return STATUS_ALIAS.get(text)


def normalize_class_key(value):
    """
    班级对齐键归一化

    优先提取班级名里的长数字串（>= 6 位），否则退回完整班级名：

      * '大数据2532013' → '2532013'
      * '2532013'      → '2532013'   （两侧能对上）
      * '软件2401班'    → '软件2401班'（4 位数字不算编码，保持完整名，避免与'计算机2401班'撞车）
    """

    text = normalize_text(value)

    if not text:
        return ""

    found = _LONG_DIGITS_RE.search(text)

    if found:
        return found.group(0)

    return text


def build_align_key(student_no, class_name, course_date, period):
    """
    生成对齐键：学号 | 班级键 | 课程日期 | 时段档

    用于「同一个学生、同一天、同一时段」的跨站匹配与对账。

    说明：
        对方库没有课程表，也没有课程名，一天只有一个上午场次和一个下午场次，
        因此对齐键里不放课程名，避免两侧根本对不上。

        课程名不影响对齐：接收方入库时会按（班级 + 日期 + 时段档）
        在本地 courses 表反查出课程名，只用于展示。
    """

    return ALIGN_SEP.join([
        normalize_text(student_no),
        normalize_class_key(class_name),
        normalize_date(course_date),
        normalize_period(period),
    ])


def align_key_of_payload(payload):
    """
    从事件的 payload 里算出对齐键

    时段优先取 period，缺失时退化为从 time_slot 推导。
    """

    if not isinstance(payload, dict):
        return ""

    return build_align_key(
        payload.get("student_no"),
        payload.get("class_name"),
        payload.get("course_date"),
        payload.get("period") or payload.get("time_slot"),
    )


# ============================================================
# 时间转换
# ============================================================

def to_iso(value):
    """本地 datetime → 带时区偏移的 ISO8601 字符串"""

    if value is None:
        return None

    if isinstance(value, str):
        return value

    if value.tzinfo is None:
        value = value.replace(tzinfo=LOCAL_TZ)

    return value.isoformat()


def to_db_datetime(value):
    """
    ISO8601（可带时区）/ 常见时间字符串 → 本地 naive datetime

    MySQL 的 DATETIME 不带时区，这里统一转成本地时间再入库。
    """

    if value in (None, ""):
        return None

    if isinstance(value, datetime):
        parsed = value
    else:
        text = str(value).strip()
        parsed = None

        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            for fmt in (
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M",
                "%Y-%m-%d",
            ):
                try:
                    parsed = datetime.strptime(text, fmt)
                    break
                except ValueError:
                    continue

        if parsed is None:
            return None

    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(LOCAL_TZ).replace(tzinfo=None)

    return parsed


# ============================================================
# 事件构造与校验
# ============================================================

def build_event(
    event_type,
    origin_site,
    origin_record_id,
    student_no,
    class_name,
    course_date,
    period,
    attendance_status,
    sign_time,
    course_name=None,
    time_slot=None,
    student_name=None,
    device_id=None,
    ip=None,
    location=None,
    is_script=0,
    task_start_time=None,
    task_end_time=None,
    origin_task_id=None,
):
    """
    构造一条同步事件

    幂等键是 (origin_site, origin_record_id)，不在这里生成 event_id 之外的东西。

    period 是对齐键的组成部分，必须给得出；course_name / time_slot 只是展示用，
    对方库没有课程名时可以留空，由接收方按（班级 + 日期 + 时段档）反查补齐。
    """

    payload = {
        "student_no": normalize_text(student_no),
        "student_name": normalize_text(student_name),
        "class_name": normalize_text(class_name),
        "course_name": normalize_text(course_name),
        "course_date": normalize_date(course_date),
        "period": normalize_period(period) or normalize_period(time_slot),
        "time_slot": normalize_time_slot(time_slot),
        "attendance_status": normalize_attendance_status(attendance_status),
        "sign_time": to_iso(sign_time),
        "device_id": normalize_text(device_id) or None,
        "ip": normalize_text(ip) or None,
        "location": normalize_text(location) or None,
        "is_script": int(is_script or 0),
        "task_start_time": to_iso(task_start_time),
        "task_end_time": to_iso(task_end_time),
        "server_time": to_iso(datetime.now()),
    }

    return {
        "schema_version": SCHEMA_VERSION,
        "event_id": str(uuid4()),
        "event_type": event_type,
        "origin_site": normalize_text(origin_site),
        "origin_record_id": str(origin_record_id),
        "origin_task_id": str(origin_task_id) if origin_task_id else None,
        "occurred_at": to_iso(datetime.now()),
        "align_key": align_key_of_payload(payload),
        "payload": payload,
    }


# course_name / time_slot 不再是必填项：对方库没有课程名，一天只有上下午两档
_REQUIRED_PAYLOAD_FIELDS = (
    "student_no",
    "class_name",
    "course_date",
    "sign_time",
)

_REQUIRED_EVENT_FIELDS = (
    "event_type",
    "origin_site",
    "origin_record_id",
)


def validate_event(event):
    """
    校验一条入站事件

    返回 (是否通过, 失败原因)
    """

    if not isinstance(event, dict):
        return False, "事件格式不是对象"

    for field in _REQUIRED_EVENT_FIELDS:

        if not normalize_text(event.get(field)):
            return False, "缺少必填字段 %s" % field

    if event.get("event_type") not in EVENT_TYPES:
        return False, "不支持的事件类型 %s" % event.get("event_type")

    payload = event.get("payload")

    if not isinstance(payload, dict):
        return False, "缺少 payload"

    for field in _REQUIRED_PAYLOAD_FIELDS:

        if not normalize_text(payload.get(field)):
            return False, "payload 缺少必填字段 %s" % field

    if to_db_datetime(payload.get("sign_time")) is None:
        return False, "sign_time 无法解析"

    if not normalize_date(payload.get("course_date")):
        return False, "course_date 无法解析"

    # 对齐键要靠时段档，period 与 time_slot 至少得有一个能识别出来
    if not normalize_period(payload.get("period") or payload.get("time_slot")):
        return False, "payload 的 period / time_slot 无法识别时段档"

    status = payload.get("attendance_status")

    # 允许整数，也允许对方库里的 normal / late / absent 这类文本别名
    if status is not None and normalize_attendance_status(status) is None:
        return False, "attendance_status 取值非法"

    return True, None
