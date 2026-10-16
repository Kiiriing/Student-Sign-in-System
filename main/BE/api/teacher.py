from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from core.auth_utils import require_role
from core.database import db_cursor, get_db

from sync.config import SITE_CODE, SITE_NAME, site_name_of
from sync.contract import build_align_key, normalize_period
from sync.store import (
    attendance_status_counts,
    count_signed_students,
    cross_signs_for_course,
)


# ============================================================
# Blueprint
# ============================================================

# main.py：
#
# from api.teacher import teacher_bp
#
# 所以这里必须定义 teacher_bp
teacher_bp = Blueprint("teacher", __name__)


# ============================================================
# 检查教师权限
# ============================================================

def check_teacher():
    """校验当前用户是否为已登录的教师（role = 2）"""
    return require_role(2, "只有教师可以访问此接口")


# ============================================================
# 获取教师ID
# ============================================================

def get_teacher_id(cursor, user_id):

    sql = """
        SELECT id
        FROM teachers
        WHERE user_id = %s
        LIMIT 1
    """

    cursor.execute(sql, (user_id,))

    teacher = cursor.fetchone()

    if not teacher:
        return None

    return teacher["id"]


# ============================================================
# 1. 获取教师课程
#
# GET /api/teacher/courses
# ============================================================

@teacher_bp.route("/api/teacher/courses", methods=["GET"])
@jwt_required()
def get_teacher_courses():

    user, error = check_teacher()

    if error:
        return error

    try:

        with db_cursor() as cursor:

            teacher_id = get_teacher_id(
                cursor,
                user["user_id"]
            )

            if not teacher_id:

                return jsonify({
                    "code": 404,
                    "message": "教师信息不存在"
                }), 404

            sql = """
                SELECT
                    c.id,
                    c.name,
                    c.course_date AS date,
                    c.time,
                    c.class_id,
                    cl.name AS class_name
                FROM courses c

                LEFT JOIN classes cl
                    ON cl.id = c.class_id

                WHERE c.teacher_id = %s

                ORDER BY c.course_date DESC, c.time ASC
            """

            cursor.execute(
                sql,
                (teacher_id,)
            )

            courses = cursor.fetchall()

            for c in courses:
                if c.get("date") and hasattr(c["date"], "isoformat"):
                    c["date"] = c["date"].isoformat()

            return jsonify({
                "code": 200,
                "message": "获取课程成功",
                "data": courses
            }), 200

    except Exception as e:

        print("获取教师课程失败：", e)

        return jsonify({
            "code": 500,
            "message": "获取课程失败",
            "error": str(e)
        }), 500



# ============================================================
# 2. 创建签到任务
#
# POST /api/teacher/attendance/create
#
# 请求：
#
# {
#     "course_id": 1,
#     "start_time": "2026-09-11 19:00:00",
#     "end_time": "2026-09-11 19:30:00"
# }
#
# ============================================================

@teacher_bp.route(
    "/api/teacher/attendance/create",
    methods=["POST"]
)
@jwt_required()
def create_attendance():

    user, error = check_teacher()

    if error:
        return error

    data = request.get_json(silent=True) or {}

    course_id = data.get("course_id")
    start_time = data.get("start_time")
    end_time = data.get("end_time")

    # --------------------------------------------------------
    # 参数检查
    # --------------------------------------------------------

    if not course_id:

        return jsonify({
            "code": 400,
            "message": "课程ID不能为空"
        }), 400

    if not start_time:

        return jsonify({
            "code": 400,
            "message": "签到开始时间不能为空"
        }), 400

    if not end_time:

        return jsonify({
            "code": 400,
            "message": "签到结束时间不能为空"
        }), 400

    conn = None

    try:

        conn = get_db()
        cursor = conn.cursor()

        # ----------------------------------------------------
        # 获取教师ID
        # ----------------------------------------------------

        teacher_id = get_teacher_id(
            cursor,
            user["user_id"]
        )

        if not teacher_id:

            return jsonify({
                "code": 404,
                "message": "教师信息不存在"
            }), 404

        # ----------------------------------------------------
        # 检查课程是否属于当前教师
        # ----------------------------------------------------

        course_sql = """
            SELECT
                id,
                name,
                class_id
            FROM courses
            WHERE id = %s
              AND teacher_id = %s
            LIMIT 1
        """

        cursor.execute(
            course_sql,
            (
                course_id,
                teacher_id
            )
        )

        course = cursor.fetchone()

        if not course:

            return jsonify({
                "code": 403,
                "message": "你没有权限操作该课程"
            }), 403

        # ----------------------------------------------------
        # 检查时间
        # ----------------------------------------------------

        if str(start_time) >= str(end_time):

            return jsonify({
                "code": 400,
                "message": "签到结束时间必须晚于开始时间"
            }), 400

        # ----------------------------------------------------
        # 创建签到任务
        #
        # status：
        #
        # 1 = 进行中
        # 0 = 已关闭
        # ----------------------------------------------------

        from uuid import uuid4

        task_id = str(uuid4())

        insert_sql = """
            INSERT INTO attendance_task
            (
                id,
                course_id,
                start_time,
                end_time,
                status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                1
            )
        """

        cursor.execute(
            insert_sql,
            (
                task_id,
                course_id,
                start_time,
                end_time
            )
        )

        conn.commit()

        return jsonify({
            "code": 200,
            "message": "签到任务创建成功",
            "data": {
                "id": task_id,
                "course_id": course_id,
                "course_name": course["name"],
                "start_time": start_time,
                "end_time": end_time,
                "status": 1
            }
        }), 200

    except Exception as e:

        if conn:

            try:
                conn.rollback()
            except Exception:
                pass

        print("创建签到任务失败：", e)

        return jsonify({
            "code": 500,
            "message": "创建签到任务失败",
            "error": str(e)
        }), 500

    finally:

        if conn:

            try:
                conn.close()
            except Exception:
                pass


# ============================================================
# 3. 关闭签到任务
#
# POST /api/teacher/attendance/close
#
# 请求：
#
# {
#     "task_id": 1
# }
#
# ============================================================

@teacher_bp.route(
    "/api/teacher/attendance/close",
    methods=["POST"]
)
@jwt_required()
def close_attendance():

    user, error = check_teacher()

    if error:
        return error

    data = request.get_json(silent=True) or {}

    task_id = data.get("task_id")

    if not task_id:

        return jsonify({
            "code": 400,
            "message": "签到任务ID不能为空"
        }), 400

    conn = None

    try:

        conn = get_db()
        cursor = conn.cursor()

        teacher_id = get_teacher_id(
            cursor,
            user["user_id"]
        )

        if not teacher_id:

            return jsonify({
                "code": 404,
                "message": "教师信息不存在"
            }), 404

        # ----------------------------------------------------
        # 查询任务
        #
        # 同时验证课程属于当前教师
        # ----------------------------------------------------

        sql = """
            SELECT
                at.id,
                at.status,
                c.name AS course_name
            FROM attendance_task at

            INNER JOIN courses c
                ON c.id = at.course_id

            WHERE at.id = %s
              AND c.teacher_id = %s

            LIMIT 1
        """

        cursor.execute(
            sql,
            (
                task_id,
                teacher_id
            )
        )

        task = cursor.fetchone()

        if not task:

            return jsonify({
                "code": 404,
                "message": "签到任务不存在或无权限"
            }), 404

        # ----------------------------------------------------
        # 已经关闭
        # ----------------------------------------------------

        if task["status"] == 0:

            return jsonify({
                "code": 400,
                "message": "签到任务已经关闭"
            }), 400

        # ----------------------------------------------------
        # 关闭签到
        # ----------------------------------------------------

        update_sql = """
            UPDATE attendance_task
            SET status = 0
            WHERE id = %s
        """

        cursor.execute(
            update_sql,
            (task_id,)
        )

        conn.commit()

        return jsonify({
            "code": 200,
            "message": "签到任务已关闭"
        }), 200

    except Exception as e:

        if conn:

            try:
                conn.rollback()
            except Exception:
                pass

        print("关闭签到任务失败：", e)

        return jsonify({
            "code": 500,
            "message": "关闭签到任务失败",
            "error": str(e)
        }), 500

    finally:

        if conn:

            try:
                conn.close()
            except Exception:
                pass


# ============================================================
# 3.5 删除签到任务
#
# DELETE /api/teacher/attendance/delete
#
# 请求：
#
# {
#     "task_id": "uuid"
# }
#
# 级联删除该任务下的所有签到记录（FK ON DELETE CASCADE）
# ============================================================

@teacher_bp.route(
    "/api/teacher/attendance/delete",
    methods=["POST"]
)
@jwt_required()
def delete_attendance():

    user, error = check_teacher()

    if error:
        return error

    data = request.get_json(silent=True) or {}

    task_id = data.get("task_id")

    if not task_id:

        return jsonify({
            "code": 400,
            "message": "签到任务ID不能为空"
        }), 400

    conn = None

    try:

        conn = get_db()
        cursor = conn.cursor()

        teacher_id = get_teacher_id(
            cursor,
            user["user_id"]
        )

        if not teacher_id:

            return jsonify({
                "code": 404,
                "message": "教师信息不存在"
            }), 404

        # 验证任务属于当前教师
        cursor.execute("""
            SELECT at.id
            FROM attendance_task at
            INNER JOIN courses c ON c.id = at.course_id
            WHERE at.id = %s AND c.teacher_id = %s
            LIMIT 1
        """, (task_id, teacher_id))

        task = cursor.fetchone()

        if not task:

            return jsonify({
                "code": 404,
                "message": "签到任务不存在或无权限"
            }), 404

        # 级联删除签到记录（FK ON DELETE CASCADE 自动处理）
        cursor.execute(
            "DELETE FROM attendance_task WHERE id = %s",
            (task_id,)
        )

        conn.commit()

        return jsonify({
            "code": 200,
            "message": "签到任务已删除"
        }), 200

    except Exception as e:

        if conn:

            try:
                conn.rollback()
            except Exception:
                pass

        print("删除签到任务失败：", e)

        return jsonify({
            "code": 500,
            "message": "删除签到任务失败",
            "error": str(e)
        }), 500

    finally:

        if conn:

            try:
                conn.close()
            except Exception:
                pass


# ============================================================
# 4. 查看签到记录
#
# GET /api/teacher/attendance/records
#
# 可以传：
#
# ?task_id=1
#
# ============================================================

@teacher_bp.route(
    "/api/teacher/attendance/records",
    methods=["GET"]
)
@jwt_required()
def get_attendance_records():

    user, error = check_teacher()

    if error:
        return error

    task_id = request.args.get("task_id")

    try:

        with db_cursor() as cursor:

            teacher_id = get_teacher_id(
                cursor,
                user["user_id"]
            )

            if not teacher_id:

                return jsonify({
                    "code": 404,
                    "message": "教师信息不存在"
                }), 404

            # ----------------------------------------------------
            # 如果指定 task_id
            # ----------------------------------------------------

            if task_id:

                sql = """
                    SELECT
                        ar.id,
                        ar.status,
                        ar.sign_time,
                        ar.ip,
                        ar.device_id,
                        ar.location,
                        ar.is_script,

                        s.id AS student_id,
                        s.student_no,
                        s.name AS student_name,

                        cl.name AS class_name,

                        c.id AS course_id,
                        c.name AS course_name,

                        at.id AS task_id,
                        at.start_time,
                        at.end_time

                    FROM attendance_record ar

                    INNER JOIN students s
                        ON s.id = ar.student_id

                    LEFT JOIN classes cl
                        ON cl.id = s.class_id

                    INNER JOIN attendance_task at
                        ON at.id = ar.task_id

                    INNER JOIN courses c
                        ON c.id = at.course_id

                    WHERE at.id = %s
                      AND c.teacher_id = %s

                    ORDER BY ar.sign_time DESC
                """

                cursor.execute(
                    sql,
                    (
                        task_id,
                        teacher_id
                    )
                )

            # ----------------------------------------------------
            # 查询当前教师所有签到记录
            # ----------------------------------------------------

            else:

                sql = """
                    SELECT
                        ar.id,
                        ar.status,
                        ar.sign_time,
                        ar.ip,
                        ar.device_id,
                        ar.location,
                        ar.is_script,

                        s.id AS student_id,
                        s.student_no,
                        s.name AS student_name,

                        cl.name AS class_name,

                        c.id AS course_id,
                        c.name AS course_name,

                        at.id AS task_id,
                        at.start_time,
                        at.end_time

                    FROM attendance_record ar

                    INNER JOIN students s
                        ON s.id = ar.student_id

                    LEFT JOIN classes cl
                        ON cl.id = s.class_id

                    INNER JOIN attendance_task at
                        ON at.id = ar.task_id

                    INNER JOIN courses c
                        ON c.id = at.course_id

                    WHERE c.teacher_id = %s

                    ORDER BY ar.sign_time DESC
                """

                cursor.execute(
                    sql,
                    (teacher_id,)
                )

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
                    record["is_script"] = 1
                    record["status_text"] = "脚本签到"
                else:
                    record["is_script"] = 0
                    record["status_text"] = status_map.get(
                        record["status"],
                        "未知"
                    )

                # 来源站点：本站记录固定为自己
                record["source_site"] = SITE_CODE
                record["source_site_name"] = SITE_NAME
                record["is_cross"] = 0

            return jsonify({
                "code": 200,
                "message": "获取签到记录成功",
                "data": records
            }), 200

    except Exception as e:

        print("获取教师签到记录失败：", e)

        return jsonify({
            "code": 500,
            "message": "获取签到记录失败",
            "error": str(e)
        }), 500



# ============================================================
# 5. 获取签到任务列表
#
# GET /api/teacher/tasks
#
# 可选参数：
#   ?course_id=xxx   只看某课程的签到任务
#   ?date=2026-09-14 只看某天的签到任务
#
# 返回每个任务的课程、班级、时间段、状态、已签到人数、班级总人数
# ============================================================


@teacher_bp.route("/api/teacher/tasks", methods=["GET"])
@jwt_required()
def get_attendance_tasks():

    user, error = check_teacher()

    if error:
        return error

    course_id = request.args.get("course_id")
    date = request.args.get("date")

    try:

        with db_cursor() as cursor:

            teacher_id = get_teacher_id(cursor, user["user_id"])

            if not teacher_id:
                return jsonify({"code": 404, "message": "教师信息不存在"}), 404

            sql = """
                SELECT
                    at.id AS task_id,
                    at.course_id,
                    c.name AS course_name,
                    cl.id AS class_id,
                    cl.name AS class_name,
                    at.start_time,
                    at.end_time,
                    at.status,
                    c.course_date,
                    c.time AS course_time,
                    (SELECT COUNT(*) FROM students s WHERE s.class_id = c.class_id) AS total_count
                FROM attendance_task at
                INNER JOIN courses c ON c.id = at.course_id
                LEFT JOIN classes cl ON cl.id = c.class_id
                WHERE c.teacher_id = %s
            """

            params = [teacher_id]

            if course_id:
                sql += " AND at.course_id = %s"
                params.append(course_id)

            if date:
                sql += " AND DATE(at.start_time) = %s"
                params.append(date)

            sql += " ORDER BY at.start_time DESC"

            cursor.execute(sql, tuple(params))
            tasks = cursor.fetchall()

            for t in tasks:
                for key in ("start_time", "end_time"):
                    if t.get(key) and hasattr(t[key], "isoformat"):
                        t[key] = t[key].isoformat()

                # 已签到人数 = 本站签到 ∪ 有效外部签到，按学生去重
                # 口径统一收敛到 sync.store.count_signed_students
                t["signed_count"] = count_signed_students(
                    t["task_id"],
                    t.get("class_id"),
                    t.get("course_date"),
                    t.get("course_time"),
                )

                # 只用于计数的中间字段，不返回前端（避免 date 被 jsonify 序列化成 RFC 1123）
                t.pop("course_date", None)
                t.pop("course_time", None)

            return jsonify({
                "code": 200,
                "message": "获取签到任务成功",
                "data": tasks
            }), 200

    except Exception as e:
        print("获取签到任务失败：", e)
        return jsonify({
            "code": 500,
            "message": "获取签到任务失败",
            "error": str(e)
        }), 500



# ============================================================
# 6. 查看某次签到的全班名册（含未签到=旷课）
#
# GET /api/teacher/attendance/roster?task_id=xxx
#
# 返回该课程班级的全部学生，按学号排序。
# 有签到记录则返回实际状态，无记录则 status=3（旷课）。
# ============================================================


@teacher_bp.route("/api/teacher/attendance/roster", methods=["GET"])
@jwt_required()
def get_attendance_roster():

    user, error = check_teacher()

    if error:
        return error

    task_id = request.args.get("task_id")

    if not task_id:
        return jsonify({"code": 400, "message": "签到任务ID不能为空"}), 400

    try:

        with db_cursor() as cursor:

            teacher_id = get_teacher_id(cursor, user["user_id"])

            if not teacher_id:
                return jsonify({"code": 404, "message": "教师信息不存在"}), 404

            cursor.execute("""
                SELECT at.id, at.course_id, at.start_time, at.end_time, at.status,
                       c.name AS course_name, c.class_id, cl.name AS class_name,
                       c.course_date, c.time
                FROM attendance_task at
                INNER JOIN courses c ON c.id = at.course_id
                LEFT JOIN classes cl ON cl.id = c.class_id
                WHERE at.id = %s AND c.teacher_id = %s
                LIMIT 1
            """, (task_id, teacher_id))

            task = cursor.fetchone()

            if not task:
                return jsonify({"code": 404, "message": "签到任务不存在或无权限"}), 404

            # ----------------------------------------------------
            # 本站同步回来的异地签到（同一门课维度）
            # ----------------------------------------------------

            try:

                cross_map = cross_signs_for_course(
                    task["course_date"],
                )

            except Exception as e:

                cross_map = {}
                print("[跨站同步] 读取课程异地签到失败（忽略）：%s" % e)

            cursor.execute("""
                SELECT
                    s.id AS student_id,
                    s.student_no,
                    s.name AS student_name,
                    ar.id AS record_id,
                    ar.status AS record_status,
                    ar.sign_time,
                    ar.ip,
                    ar.location,
                    ar.is_script
                FROM students s
                LEFT JOIN attendance_record ar
                    ON ar.student_id = s.id AND ar.task_id = %s
                WHERE s.class_id = %s
                ORDER BY s.student_no ASC
            """, (task_id, task["class_id"]))

            students = cursor.fetchall()

            from datetime import datetime, timedelta

            now = datetime.now()
            task_start = task["start_time"]
            task_end = task["end_time"]

            # 签到窗口 = start_time ~ end_time + 10 分钟（含迟到宽限）
            in_window = task_start <= now <= (task_end + timedelta(minutes=10))

            status_map = {1: "正常", 2: "迟到", 3: "旷课", 4: "早退", 5: "病假", 6: "事假", 7: "未签到"}

            roster = []
            for s in students:

                # 本站同步回来的异地签到
                #
                # 对齐键 = 学号 | 班级键 | 课程日期 | 时段档，
                # 因此对方只给数字班级编号、也没有课程名，也一样能命中。
                cross = cross_map.get(build_align_key(
                    s["student_no"],
                    task["class_name"],
                    task["course_date"],
                    normalize_period(task["time"]),
                ))

                if s["record_status"] is not None:
                    status = s["record_status"]
                else:
                    # 无签到记录：时段内显示"未签到"，时段结束后显示"旷课"
                    status = 7 if in_window else 3

                sign_time = s["sign_time"]
                if sign_time and hasattr(sign_time, "isoformat"):
                    sign_time = sign_time.isoformat()

                # 是否脚本签到（is_script=1）
                is_script = int(s["is_script"]) if s.get("is_script") is not None else 0

                is_cross = 0
                source_site = SITE_CODE
                source_site_name = SITE_NAME
                cross_sign_time = None

                if is_script == 1:
                    # 脚本签到：状态文字改为"脚本签到"，前端用红色样式展示
                    status_text = "脚本签到"
                else:
                    status_text = status_map.get(status, "未知")

                # 本站无记录、但已在其他网站签到：
                # 计入实到（按异地记录的状态），同时单独成类标识
                if cross and s["record_status"] is None:

                    cross_status = cross.get("attendance_status")

                    if cross_status not in (1, 2, 3, 4, 5, 6):
                        cross_status = 1

                    status = cross_status

                    is_cross = 1
                    source_site = cross["origin_site"]
                    source_site_name = site_name_of(cross["origin_site"])
                    cross_sign_time = cross["sign_time"]

                    if cross_sign_time and hasattr(cross_sign_time, "isoformat"):
                        cross_sign_time = cross_sign_time.isoformat()
                        sign_time = cross_sign_time

                    status_text = "脚本签到" if is_script == 1 else "已在其他网站签到"

                roster.append({
                    "student_id": s["student_id"],
                    "student_no": s["student_no"],
                    "student_name": s["student_name"],
                    "record_id": s["record_id"],
                    "status": status,
                    "status_text": status_text,
                    "sign_time": sign_time,
                    "ip": s["ip"],
                    "location": s["location"],
                    "is_script": is_script,
                    "is_cross": is_cross,
                    "source_site": source_site,
                    "source_site_name": source_site_name,
                    "cross_sign_time": cross_sign_time
                })

            # 注意：键统一用字符串。jsonify 会对字典键排序，若这里是整数键
            # 又混入下面的 "cross" 字符串键，排序时会抛
            # "'<' not supported between instances of 'str' and 'int'"。
            # JSON 对象的键本来就是字符串，改成字符串键后返回给前端的内容不变。
            stats = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0}
            cross_count = 0
            for r in roster:
                # 脚本签到的记录仍按其底层 status（1=正常 / 2=迟到）计入 stats，
                # 这样统计接口里的"正常/迟到"数字不会因脚本签到丢失；
                # 前端在 roster 里通过 is_script 单独标识红色"脚本签到"。
                stats[str(r["status"])] += 1

                # 已在其他网站签到的，单独成类再计一次
                if r["is_cross"] == 1:
                    cross_count += 1

            stats["cross"] = cross_count

            start_time = task["start_time"]
            end_time = task["end_time"]
            if start_time and hasattr(start_time, "isoformat"):
                start_time = start_time.isoformat()
            if end_time and hasattr(end_time, "isoformat"):
                end_time = end_time.isoformat()

            return jsonify({
                "code": 200,
                "message": "获取签到名册成功",
                "data": {
                    "task": {
                        "task_id": task["id"],
                        "course_id": task["course_id"],
                        "course_name": task["course_name"],
                        "class_id": task["class_id"],
                        "class_name": task["class_name"],
                        "start_time": start_time,
                        "end_time": end_time,
                        "status": task["status"]
                    },
                    "stats": stats,
                    "roster": roster
                }
            }), 200

    except Exception as e:
        print("获取签到名册失败：", e)
        return jsonify({
            "code": 500,
            "message": "获取签到名册失败",
            "error": str(e)
        }), 500



# ============================================================
# 7. 修改学生签到状态
#
# PUT /api/teacher/attendance/record
#
# 请求：
# {
#     "task_id": "xxx",
#     "student_id": "xxx",
#     "status": 1            # 1正常 2迟到 3旷课 4早退 5病假 6事假
# }
#
# 若该学生已有签到记录则更新，否则新增一条记录（教师手动补录）。
# ============================================================


@teacher_bp.route("/api/teacher/attendance/record", methods=["PUT"])
@jwt_required()
def update_attendance_record():

    user, error = check_teacher()

    if error:
        return error

    data = request.get_json(silent=True) or {}

    task_id = data.get("task_id")
    student_id = data.get("student_id")
    status = data.get("status")

    if not task_id:
        return jsonify({"code": 400, "message": "签到任务ID不能为空"}), 400
    if not student_id:
        return jsonify({"code": 400, "message": "学生ID不能为空"}), 400
    if status not in (1, 2, 3, 4, 5, 6, 7):
        return jsonify({"code": 400, "message": "签到状态无效"}), 400

    conn = None

    try:

        conn = get_db()
        cursor = conn.cursor()

        teacher_id = get_teacher_id(cursor, user["user_id"])

        if not teacher_id:
            return jsonify({"code": 404, "message": "教师信息不存在"}), 404

        cursor.execute("""
            SELECT at.id
            FROM attendance_task at
            INNER JOIN courses c ON c.id = at.course_id
            WHERE at.id = %s AND c.teacher_id = %s
            LIMIT 1
        """, (task_id, teacher_id))

        if not cursor.fetchone():
            return jsonify({"code": 404, "message": "签到任务不存在或无权限"}), 404

        # status = 7（未签到）：删除该学生的签到记录，使其回到"未签到"状态
        if status == 7:
            cursor.execute("""
                DELETE FROM attendance_record
                WHERE task_id = %s AND student_id = %s
            """, (task_id, student_id))
            conn.commit()
            return jsonify({"code": 200, "message": "已重置为未签到"}), 200

        cursor.execute("""
            SELECT id FROM attendance_record
            WHERE task_id = %s AND student_id = %s
            LIMIT 1
        """, (task_id, student_id))

        record = cursor.fetchone()

        if record:
            # 教师手动修改签到状态时，清除脚本签到标记
            # （教师审核后认为不是脚本签到 / 不再视为脚本签到）
            cursor.execute("""
                UPDATE attendance_record
                SET status = %s, is_script = 0
                WHERE id = %s
            """, (status, record["id"]))
        else:
            from uuid import uuid4
            cursor.execute("""
                INSERT INTO attendance_record (id, task_id, student_id, status, sign_time, is_script)
                VALUES (%s, %s, %s, %s, NOW(), 0)
            """, (str(uuid4()), task_id, student_id, status))

        conn.commit()

        return jsonify({
            "code": 200,
            "message": "签到状态已更新"
        }), 200

    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        print("修改签到状态失败：", e)
        return jsonify({
            "code": 500,
            "message": "修改签到状态失败",
            "error": str(e)
        }), 500

    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


# ============================================================
# 8. 签到统计（供 ECharts 使用）
#
# GET /api/teacher/statistics
#
# 可选参数：
#   ?course_id=xxx   某课程的统计
#   ?date=2026-09-14 某天的统计
#
# 两个都不传则返回该教师所有签到任务的统计。
# 返回汇总状态分布 + 每个任务的明细分布。
# ============================================================


@teacher_bp.route("/api/teacher/statistics", methods=["GET"])
@jwt_required()
def get_attendance_statistics():

    user, error = check_teacher()

    if error:
        return error

    course_id = request.args.get("course_id")
    date = request.args.get("date")

    try:

        with db_cursor() as cursor:

            teacher_id = get_teacher_id(cursor, user["user_id"])

            if not teacher_id:
                return jsonify({"code": 404, "message": "教师信息不存在"}), 404

            where = " WHERE c.teacher_id = %s"
            params = [teacher_id]

            if course_id:
                where += " AND at.course_id = %s"
                params.append(course_id)

            if date:
                where += " AND DATE(at.start_time) = %s"
                params.append(date)

            cursor.execute(f"""
                SELECT
                    at.id AS task_id,
                    c.name AS course_name,
                    cl.id AS class_id,
                    cl.name AS class_name,
                    at.start_time,
                    at.end_time,
                    c.course_date,
                    c.time AS course_time,
                    (SELECT COUNT(*) FROM students s WHERE s.class_id = c.class_id) AS total_count
                FROM attendance_task at
                INNER JOIN courses c ON c.id = at.course_id
                LEFT JOIN classes cl ON cl.id = c.class_id
                {where}
                ORDER BY at.start_time DESC
            """, tuple(params))

            tasks = cursor.fetchall()

            for t in tasks:
                for key in ("start_time", "end_time"):
                    if t.get(key) and hasattr(t[key], "isoformat"):
                        t[key] = t[key].isoformat()

                # 状态分布：本站签到 ∪ 有效外部签到，按学生去重（本站优先）
                # 口径统一收敛到 sync.store.attendance_status_counts
                counts = attendance_status_counts(
                    t["task_id"],
                    t.get("class_id"),
                    t.get("course_date"),
                    t.get("course_time"),
                )

                t["normal_count"] = counts[1]
                t["late_count"] = counts[2]
                t["early_count"] = counts[4]
                t["sick_count"] = counts[5]
                t["leave_count"] = counts[6]

                # 已记录（非旷课）人数含外部签到，否则异地签到的学生会
                # 被 total_count - recorded 误算成旷课
                recorded = (t["normal_count"] + t["late_count"] + t["early_count"]
                            + t["sick_count"] + t["leave_count"])
                t["absent_count"] = max(t["total_count"] - recorded, 0)

                # 只用于统计的中间字段，不返回前端
                t.pop("course_date", None)
                t.pop("course_time", None)
                t.pop("class_id", None)

            summary = {
                "normal": sum(t["normal_count"] for t in tasks),
                "late": sum(t["late_count"] for t in tasks),
                "absent": sum(t["absent_count"] for t in tasks),
                "early": sum(t["early_count"] for t in tasks),
                "sick": sum(t["sick_count"] for t in tasks),
                "leave": sum(t["leave_count"] for t in tasks),
                "total": sum(t["total_count"] for t in tasks)
            }

            return jsonify({
                "code": 200,
                "message": "获取统计成功",
                "data": {
                    "summary": summary,
                    "tasks": tasks
                }
            }), 200

    except Exception as e:
        print("获取统计失败：", e)
        return jsonify({
            "code": 500,
            "message": "获取统计失败",
            "error": str(e)
        }), 500

