from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from auth_utils import require_role
from database import get_db


# ============================================================
# Blueprint
# ============================================================

# main.py 中：
#
# from student import student_bp
#
# 所以这里必须叫 student_bp
student_bp = Blueprint("student", __name__)


# ============================================================
# 脚本签到检测
# ============================================================
#
# 学生可能使用 selenium / puppeteer / playwright / phantomjs
# 等自动化工具进行自动签到。这里复用 main.py 中已有的爬虫
# 检测能力 + 自身请求特征判断本次签到是否为脚本签到。
#
# 判断依据（命中任意一条即视为脚本签到）：
#   1. User-Agent 命中爬虫/自动化工具关键字
#   2. 请求体（含 device_id 等）泄露脚本关键字
#   3. 当前 IP 在 main.py 的 _crawler_sessions 中已被标记为爬虫会话
#      （例如该 IP 此前用 python-requests 登录过、或此前 UA 含 selenium）
#   4. 缺少浏览器核心请求头（Accept / Accept-Language / Accept-Encoding
#      至少缺 2 个，且 UA 不像主流浏览器）
#
# 注意：本函数只读取请求信息，不会触发 main.py 中 detect_crawler
# 的状态变更，避免与 main.py 的 after_request 日志钩子重复计数。
# ============================================================

import re as _re

# 与 main.py 保持一致的爬虫/自动化工具关键字
_SCRIPT_UA_PATTERNS = _re.compile(
    r"python-requests|python-urllib|scrapy|curl|wget|postman|insomnia|"
    r"httpclient|okhttp|java/|go-http-client|node-fetch|axios|bot|"
    r"spider|crawler|scraper|headless|selenium|phantomjs|puppeteer|"
    r"playwright|aiohttp|httpx|mechanize|googlehttpclient|webdriver",
    _re.IGNORECASE
)

# 请求体中泄露脚本特征的关键字
_SCRIPT_BODY_PATTERNS = _re.compile(
    r"scraper|spider|crawler|selenium|puppeteer|playwright|headless|"
    r"phantomjs|mechanize|scrapy|aiohttp|httpx|webdriver",
    _re.IGNORECASE
)

# 主流浏览器 UA 特征
_BROWSER_UA_REGEX = _re.compile(
    r"Mozilla|Chrome|Safari|Edge|Firefox|OPR|Opera|MSIE|Trident",
    _re.IGNORECASE
)

# 浏览器必备请求头
_BROWSER_CORE_HEADERS = ["Accept", "Accept-Language", "Accept-Encoding"]


def _get_client_ip() -> str:
    """获取客户端真实 IP（处理反向代理）"""
    xff = request.headers.get("X-Forwarded-For")
    if xff:
        return xff.split(",")[0].strip()
    return request.remote_addr or "unknown"


def _is_script_signin_request() -> bool:
    """
    判断本次签到请求是否来自脚本/自动化工具

    返回 True 表示是脚本签到；False 表示是正常浏览器签到
    """
    ua = request.headers.get("User-Agent", "") or ""

    # 1. UA 中含爬虫/自动化工具关键字（selenium、puppeteer、playwright 等）
    if ua and _SCRIPT_UA_PATTERNS.search(ua):
        return True

    # 2. 请求体泄露脚本特征（如 device_id="selenium-xxx"）
    try:
        body = request.get_data(as_text=True) or ""
    except Exception:
        body = ""
    if body and _SCRIPT_BODY_PATTERNS.search(body):
        return True

    # 3. 同 IP 此前已被 main.py 标记为爬虫会话
    #    （如该 IP 用 python-requests 登录过、UA 含 selenium 等）
    try:
        from main import _crawler_sessions
        ip = _get_client_ip()
        if ip in _crawler_sessions:
            return True
    except Exception:
        # main.py 未加载或导入失败时不影响主流程
        pass

    # 4. 缺少浏览器核心请求头（仅在 UA 不像浏览器时检测）
    if not _BROWSER_UA_REGEX.search(ua):
        missing = [h for h in _BROWSER_CORE_HEADERS if not request.headers.get(h)]
        if len(missing) >= 2:
            return True

    # 5. 前端浏览器指纹检测命中（client_fp 字段）
    #
    # 前端 src/utils/fingerprint.ts 会检测 navigator.webdriver、
    # chrome.runtime、plugins、cdc_ 变量、WebGL renderer 等浏览器
    # 原生 JS API 特征，命中后把命中的 key 列表（逗号分隔）放到
    # 请求体的 client_fp 字段。这是 HTTP 层难以伪造的检测维度，
    # 默认 selenium（不隐藏 webdriver）会被识别。
    try:
        data = request.get_json(silent=True) or {}
        client_fp = str(data.get("client_fp") or "").strip()
        if client_fp:
            return True
    except Exception:
        pass

    return False


# ============================================================
# 检查学生权限
# ============================================================

def check_student():
    """校验当前用户是否为已登录的学生（role = 1）"""
    return require_role(1, "只有学生可以访问此接口")


# ============================================================
# 1. 获取学生课程
#
# GET /api/student/courses
# ============================================================

@student_bp.route("/api/student/courses", methods=["GET"])
@jwt_required()
def get_courses():

    user, error = check_student()

    if error:
        return error

    conn = None

    try:

        conn = get_db()
        cursor = conn.cursor()

        # ----------------------------------------------------
        # 根据用户ID找到学生
        # ----------------------------------------------------

        sql = """
            SELECT
                s.id AS student_id,
                s.student_no,
                s.name AS student_name,
                s.class_id,
                c.name AS class_name
            FROM students s
            LEFT JOIN classes c
                ON c.id = s.class_id
            WHERE s.user_id = %s
            LIMIT 1
        """

        cursor.execute(
            sql,
            (user["user_id"],)
        )

        student = cursor.fetchone()

        if not student:

            return jsonify({
                "code": 404,
                "message": "学生信息不存在"
            }), 404

        # ----------------------------------------------------
        # 查询该班级今日课程（按 course_date = CURDATE() 过滤）
        # 返回字段包含 date（日期）和 time（时间段）
        # ----------------------------------------------------

        course_sql = """
            SELECT
                c.id,
                c.name,
                c.course_date AS date,
                c.time,
                c.teacher_id,
                t.name AS teacher_name
            FROM courses c
            LEFT JOIN teachers t
                ON t.id = c.teacher_id
            WHERE c.class_id = %s
              AND c.course_date = CURDATE()
            ORDER BY c.time ASC
        """

        cursor.execute(
            course_sql,
            (student["class_id"],)
        )

        courses = cursor.fetchall()

        today_str = None
        try:
            import datetime
            today_str = datetime.date.today().isoformat()  # e.g. "2026-09-14"
        except Exception:
            today_str = None

        # ----------------------------------------------------
        # 批量查询「进行中的签到任务」和「本人是否已签到」
        #
        # 原来是在课程循环里逐门课程查两次数据库（N+1），
        # 课程数量多时会产生大量往返。这里改成固定 2 条 SQL：
        #   1) 一次查出今日所有课程的进行中任务
        #   2) 一次查出这些任务中本人已签到的任务ID
        # ----------------------------------------------------

        task_map = {}          # { course_id: task_id }
        signed_task_ids = set()

        if courses:
            course_ids = [c["id"] for c in courses]
            placeholders = ",".join(["%s"] * len(course_ids))

            cursor.execute(
                f"""
                SELECT
                    at.course_id,
                    at.id AS task_id
                FROM attendance_task at
                WHERE at.course_id IN ({placeholders})
                  AND at.status = 1
                  AND NOW() BETWEEN at.start_time AND DATE_ADD(at.end_time, INTERVAL 10 MINUTE)
                ORDER BY at.start_time ASC
                """,
                tuple(course_ids)
            )

            for row in cursor.fetchall():
                # 同一课程存在多个进行中任务时，保留最早开始的那个
                task_map.setdefault(str(row["course_id"]), str(row["task_id"]))

            if task_map:
                task_ids = list(task_map.values())
                task_placeholders = ",".join(["%s"] * len(task_ids))

                cursor.execute(
                    f"""
                    SELECT DISTINCT task_id
                    FROM attendance_record
                    WHERE student_id = %s
                      AND task_id IN ({task_placeholders})
                    """,
                    tuple([student["student_id"]] + task_ids)
                )

                signed_task_ids = {str(row["task_id"]) for row in cursor.fetchall()}

        for c in courses:
            if c.get("date") and hasattr(c["date"], "isoformat"):
                c["date"] = c["date"].isoformat()
            elif c.get("date") is None:
                c["date"] = today_str

            task_id = task_map.get(str(c["id"]))

            c["signed"] = task_id in signed_task_ids
            c["task_id"] = task_id
            c["has_active_task"] = task_id is not None

        return jsonify({
            "code": 200,
            "message": "获取课程成功",
            "data": {
                "student_id": str(student["student_id"]),
                "student_no": student["student_no"],
                "student_name": student["student_name"],
                "class_name": student["class_name"],
                "courses": courses
            }
        }), 200

    except Exception as e:

        print("获取学生课程失败：", e)

        return jsonify({
            "code": 500,
            "message": "获取课程失败",
            "error": str(e)
        }), 500

    finally:

        if conn:

            try:
                conn.close()
            except Exception:
                pass


# ============================================================
# 2. 学生签到
#
# POST /api/student/signin
#
# 请求：
#
# {
#     "course_id": 1,
#     "device_id": "xxxx",
#     "location": "..."
# }
#
# ============================================================

@student_bp.route("/api/student/signin", methods=["POST"])
@jwt_required()
def student_signin():

    user, error = check_student()

    if error:
        return error

    data = request.get_json(silent=True) or {}

    course_id = data.get("course_id")
    device_id = str(data.get("device_id", "")).strip()
    location = str(data.get("location", "")).strip()

    # --------------------------------------------------------
    # 参数检查
    # --------------------------------------------------------

    if not course_id:

        return jsonify({
            "code": 400,
            "message": "课程ID不能为空"
        }), 400

    if not device_id:

        return jsonify({
            "code": 400,
            "message": "设备标识不能为空"
        }), 400

    conn = None

    try:

        conn = get_db()
        cursor = conn.cursor()

        # ----------------------------------------------------
        # 获取学生
        # ----------------------------------------------------

        student_sql = """
            SELECT
                id,
                student_no,
                name,
                class_id
            FROM students
            WHERE user_id = %s
            LIMIT 1
        """

        cursor.execute(
            student_sql,
            (user["user_id"],)
        )

        student = cursor.fetchone()

        if not student:

            return jsonify({
                "code": 404,
                "message": "学生信息不存在"
            }), 404

        student_id = student["id"]

        # ----------------------------------------------------
        # 检查课程是否属于学生所在班级
        # ----------------------------------------------------

        course_sql = """
            SELECT
                id,
                name,
                class_id
            FROM courses
            WHERE id = %s
              AND class_id = %s
            LIMIT 1
        """

        cursor.execute(
            course_sql,
            (
                course_id,
                student["class_id"]
            )
        )

        course = cursor.fetchone()

        if not course:

            return jsonify({
                "code": 404,
                "message": "课程不存在或不属于你的班级"
            }), 404

        # ----------------------------------------------------
        # 查找当前正在进行的签到任务
        #
        # 使用数据库当前时间
        # ----------------------------------------------------

        task_sql = """
            SELECT
                id,
                course_id,
                start_time,
                end_time,
                status
            FROM attendance_task
            WHERE course_id = %s
              AND status = 1
              AND NOW() BETWEEN start_time AND DATE_ADD(end_time, INTERVAL 10 MINUTE)
            ORDER BY start_time DESC
            LIMIT 1
        """

        cursor.execute(
            task_sql,
            (course_id,)
        )

        task = cursor.fetchone()

        if not task:

            return jsonify({
                "code": 400,
                "message": "当前没有正在进行的签到"
            }), 400

        task_id = task["id"]

        # ----------------------------------------------------
        # 检查学生是否已经签到
        # ----------------------------------------------------

        duplicate_sql = """
            SELECT
                id,
                status,
                sign_time
            FROM attendance_record
            WHERE task_id = %s
              AND student_id = %s
            LIMIT 1
        """

        cursor.execute(
            duplicate_sql,
            (
                task_id,
                student_id
            )
        )

        duplicate = cursor.fetchone()

        if duplicate:

            return jsonify({
                "code": 400,
                "message": "你已经签到过了",
                "data": {
                    "status": duplicate["status"],
                    "sign_time": duplicate["sign_time"]
                }
            }), 400

        # ----------------------------------------------------
        # 防止同一个设备给不同学生签到
        #
        # 一个签到任务：
        #
        # device A -> 张三     允许
        # device A -> 李四     拒绝
        # ----------------------------------------------------

        device_sql = """
            SELECT
                id,
                student_id
            FROM attendance_record
            WHERE task_id = %s
              AND device_id = %s
            LIMIT 1
        """

        cursor.execute(
            device_sql,
            (
                task_id,
                device_id
            )
        )

        device_record = cursor.fetchone()

        if device_record:

            if device_record["student_id"] != student_id:

                return jsonify({
                    "code": 403,
                    "message": "该设备已经为其他学生完成本次签到"
                }), 403

        # ----------------------------------------------------
        # 获取客户端IP
        # ----------------------------------------------------

        ip = request.headers.get(
            "X-Forwarded-For",
            request.remote_addr
        )

        if ip and "," in ip:

            ip = ip.split(",")[0].strip()

        # ----------------------------------------------------
        # 判断签到状态
        #
        # 以签到结束时间 end_time 为基准：
        #   NOW() <= end_time                              → 正常 (1)
        #   end_time < NOW() <= end_time + 10 分钟         → 迟到 (2)
        #   NOW() > end_time + 10 分钟                     → 不允许签到（旷课）
        #
        # 签到窗口已在 task_sql 中限制为 start_time ~ end_time+10min
        # ----------------------------------------------------

        late_sql = """
            SELECT
                CASE
                    WHEN NOW() <= end_time
                    THEN 1
                    ELSE 2
                END AS attendance_status
            FROM attendance_task
            WHERE id = %s
            LIMIT 1
        """

        cursor.execute(
            late_sql,
            (task_id,)
        )

        status_result = cursor.fetchone()

        attendance_status = status_result["attendance_status"]

        # ----------------------------------------------------
        # 脚本签到检测
        #
        # 在写入签到记录前判断本次请求是否来自脚本
        # （selenium / puppeteer / playwright 等自动化工具）
        # 命中则在 attendance_record.is_script 写入 1
        # ----------------------------------------------------

        is_script = 1 if _is_script_signin_request() else 0

        # ----------------------------------------------------
        # 写入签到记录
        # ----------------------------------------------------

        from uuid import uuid4
        record_id = str(uuid4())

        insert_sql = """
            INSERT INTO attendance_record
            (
                id,
                task_id,
                student_id,
                status,
                sign_time,
                ip,
                device_id,
                location,
                is_script
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                NOW(),
                %s,
                %s,
                %s,
                %s
            )
        """

        cursor.execute(
            insert_sql,
            (
                record_id,
                task_id,
                student_id,
                attendance_status,
                ip,
                device_id,
                location,
                is_script
            )
        )

        conn.commit()

        # ----------------------------------------------------
        # 返回结果
        # ----------------------------------------------------

        status_text = (
            "签到成功"
            if attendance_status == 1
            else "签到成功，但已迟到"
        )

        return jsonify({
            "code": 200,
            "message": status_text,
            "data": {
                "record_id": record_id,
                "course_id": course_id,
                "course_name": course["name"],
                "status": attendance_status,
                "is_script": is_script,
                "status_text": (
                    "脚本签到"
                    if is_script == 1
                    else (
                        "正常"
                        if attendance_status == 1
                        else "迟到"
                    )
                )
            }
        }), 200

    except Exception as e:

        if conn:

            try:
                conn.rollback()
            except Exception:
                pass

        print("学生签到失败：", e)

        return jsonify({
            "code": 500,
            "message": "签到失败",
            "error": str(e)
        }), 500

    finally:

        if conn:

            try:
                conn.close()
            except Exception:
                pass


# ============================================================
# 3. 获取签到记录
#
# GET /api/student/records
# ============================================================

@student_bp.route("/api/student/records", methods=["GET"])
@jwt_required()
def get_records():

    user, error = check_student()

    if error:
        return error

    conn = None

    try:

        conn = get_db()
        cursor = conn.cursor()

        # 可选日期筛选：?date=YYYY-MM-DD
        date_filter = request.args.get("date")

        sql = """
            SELECT
                ar.id,
                ar.status,
                ar.sign_time,
                ar.ip,
                ar.device_id,
                ar.location,
                ar.create_time,
                ar.is_script,

                at.id AS task_id,
                at.start_time,
                at.end_time,

                c.id AS course_id,
                c.name AS course_name,

                t.name AS teacher_name

            FROM attendance_record ar

            INNER JOIN students s
                ON s.id = ar.student_id

            INNER JOIN attendance_task at
                ON at.id = ar.task_id

            INNER JOIN courses c
                ON c.id = at.course_id

            LEFT JOIN teachers t
                ON t.id = c.teacher_id

            WHERE s.user_id = %s
        """

        params = [user["user_id"]]

        if date_filter:
            sql += " AND DATE(ar.sign_time) = %s"
            params.append(date_filter)

        sql += " ORDER BY ar.sign_time DESC"

        cursor.execute(sql, tuple(params))

        records = cursor.fetchall()

        # ----------------------------------------------------
        # 状态文字
        # ----------------------------------------------------

        status_map = {
            1: "正常",
            2: "迟到",
            3: "缺勤",
            4: "早退",
            5: "病假",
            6: "事假"
        }

        for record in records:

            is_script = int(record.get("is_script") or 0)
            if is_script == 1:
                # 脚本签到覆盖为"脚本签到"，前端用红色样式展示
                record["is_script"] = 1
                record["status_text"] = "脚本签到"
            else:
                record["is_script"] = 0
                record["status_text"] = status_map.get(
                    record["status"],
                    "未知"
                )

        return jsonify({
            "code": 200,
            "message": "获取签到记录成功",
            "data": records
        }), 200

    except Exception as e:

        print("获取签到记录失败：", e)

        return jsonify({
            "code": 500,
            "message": "获取签到记录失败",
            "error": str(e)
        }), 500

    finally:

        if conn:

            try:
                conn.close()
            except Exception:
                pass


# ============================================================
# 4. 获取班级签到情况
#
# GET /api/student/class-attendance?date=YYYY-MM-DD
#
# 返回当前学生所在班级在指定日期（默认今日）所有课程
# 以及全班每位学生的签到情况。
# ============================================================

@student_bp.route("/api/student/class-attendance", methods=["GET"])
@jwt_required()
def get_class_attendance():

    user, error = check_student()

    if error:
        return error

    conn = None

    try:

        conn = get_db()
        cursor = conn.cursor()

        # ----------------------------------------------------
        # 获取学生
        # ----------------------------------------------------

        student_sql = """
            SELECT
                s.id AS student_id,
                s.student_no,
                s.name AS student_name,
                s.class_id,
                c.name AS class_name
            FROM students s
            LEFT JOIN classes c ON c.id = s.class_id
            WHERE s.user_id = %s
            LIMIT 1
        """

        cursor.execute(student_sql, (user["user_id"],))
        student = cursor.fetchone()

        if not student:
            return jsonify({"code": 404, "message": "学生信息不存在"}), 404

        class_id = student["class_id"]

        if not class_id:
            return jsonify({"code": 400, "message": "未分配班级"}), 400

        # ----------------------------------------------------
        # 日期筛选（默认今天）
        # ----------------------------------------------------

        import datetime as _dt
        date_str = request.args.get("date")
        if date_str:
            try:
                _dt.datetime.strptime(date_str, "%Y-%m-%d")
            except Exception:
                return jsonify({"code": 400, "message": "日期格式错误，应为 YYYY-MM-DD"}), 400
        else:
            date_str = _dt.date.today().isoformat()

        # ----------------------------------------------------
        # 查询当天该班级所有课程及对应签到任务
        # ----------------------------------------------------

        course_sql = """
            SELECT
                c.id AS course_id,
                c.name AS course_name,
                c.time,
                t.name AS teacher_name,
                at.id AS task_id,
                at.start_time,
                at.end_time,
                at.status AS task_status
            FROM courses c
            LEFT JOIN teachers t ON t.id = c.teacher_id
            LEFT JOIN attendance_task at
                ON at.course_id = c.id
                AND DATE(at.start_time) = %s
            WHERE c.class_id = %s
              AND c.course_date = %s
            ORDER BY c.time ASC
        """

        cursor.execute(course_sql, (date_str, class_id, date_str))
        course_rows = cursor.fetchall()

        courses_list = []
        task_ids = []
        for c in course_rows:
            start_time = c.get("start_time")
            end_time = c.get("end_time")
            if start_time and hasattr(start_time, "isoformat"):
                start_time = start_time.isoformat()
            if end_time and hasattr(end_time, "isoformat"):
                end_time = end_time.isoformat()
            task_id = c.get("task_id")
            if task_id:
                task_ids.append(task_id)
                task_id = str(task_id)
            courses_list.append({
                "course_id": str(c["course_id"]),
                "course_name": c["course_name"],
                "time": c.get("time"),
                "teacher_name": c.get("teacher_name"),
                "task_id": task_id,
                "start_time": start_time,
                "end_time": end_time,
                "task_status": c.get("task_status")
            })

        # ----------------------------------------------------
        # 查询全班学生
        # ----------------------------------------------------

        cursor.execute("""
            SELECT id, student_no, name
            FROM students
            WHERE class_id = %s
            ORDER BY student_no ASC
        """, (class_id,))
        students_list = cursor.fetchall()

        # ----------------------------------------------------
        # 查询这些任务下所有学生的签到记录
        # ----------------------------------------------------

        records_map = {}  # {(student_id, task_id): record}
        if task_ids:
            placeholders = ",".join(["%s"] * len(task_ids))
            cursor.execute(
                f"""
                SELECT student_id, task_id, status, sign_time, is_script
                FROM attendance_record
                WHERE task_id IN ({placeholders})
                """,
                tuple(task_ids)
            )
            for r in cursor.fetchall():
                records_map[(str(r["student_id"]), str(r["task_id"]))] = r

        status_map = {1: "正常", 2: "迟到", 3: "旷课", 4: "早退", 5: "病假", 6: "事假", 7: "未签到"}

        # ----------------------------------------------------
        # 组装每位学生在每节课的签到情况
        # ----------------------------------------------------

        roster = []
        now = _dt.datetime.now()
        from datetime import datetime, timedelta
        for s in students_list:
            row_status = {}
            summary = {"normal": 0, "late": 0, "absent": 0, "early": 0, "sick": 0, "leave": 0, "unsigned": 0, "script": 0}
            for c in courses_list:
                tid = c["task_id"]
                key = (str(s["id"]), tid) if tid else None
                rec = records_map.get(key) if key else None

                status = None
                status_text = "无任务"
                sign_time = None
                is_script = 0

                if tid:
                    if rec:
                        status = rec["status"]
                        sign_time = rec["sign_time"]
                        if sign_time and hasattr(sign_time, "isoformat"):
                            sign_time = sign_time.isoformat()
                        is_script = int(rec.get("is_script") or 0)
                        if is_script == 1:
                            # 脚本签到：状态文字改为"脚本签到"，前端用红色样式展示
                            status_text = "脚本签到"
                        else:
                            status_text = status_map.get(status, "未知")
                    else:
                        # 无签到记录
                        try:
                            t_end = c["end_time"]
                            t_start = c["start_time"]
                            if isinstance(t_end, str):
                                t_end = datetime.fromisoformat(t_end)
                            if isinstance(t_start, str):
                                t_start = datetime.fromisoformat(t_start)
                            in_window = bool(t_start and t_end and t_start <= now <= (t_end + timedelta(minutes=10)))
                        except Exception:
                            in_window = False
                        status = 7 if in_window else 3
                        status_text = status_map.get(status, "未知")
                    # 汇总
                    if is_script == 1:
                        summary["script"] += 1
                    elif status == 1: summary["normal"] += 1
                    elif status == 2: summary["late"] += 1
                    elif status == 3: summary["absent"] += 1
                    elif status == 4: summary["early"] += 1
                    elif status == 5: summary["sick"] += 1
                    elif status == 6: summary["leave"] += 1
                    elif status == 7: summary["unsigned"] += 1

                row_status[str(c["course_id"])] = {
                    "task_id": tid,
                    "status": status,
                    "status_text": status_text,
                    "sign_time": sign_time,
                    "is_script": is_script
                }

            roster.append({
                "student_id": str(s["id"]),
                "student_no": s["student_no"],
                "student_name": s["name"],
                "is_me": str(s["id"]) == str(student["student_id"]),
                "row_status": row_status,
                "summary": summary
            })

        return jsonify({
            "code": 200,
            "message": "获取班级签到情况成功",
            "data": {
                "date": date_str,
                "class_name": student["class_name"],
                "courses": courses_list,
                "roster": roster
            }
        }), 200

    except Exception as e:
        print("获取班级签到情况失败：", e)
        return jsonify({"code": 500, "message": "获取班级签到情况失败", "error": str(e)}), 500

    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass