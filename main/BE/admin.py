from flask import Blueprint, jsonify, request

from flask_jwt_extended import jwt_required

from werkzeug.security import generate_password_hash

from auth_utils import require_role
from database import get_db

from uuid import uuid4



# =====================================================
# Blueprint
# =====================================================


admin_bp = Blueprint(
    "admin",
    __name__
)



# =====================================================
# 管理员权限验证
# =====================================================


def check_admin():
    """校验当前用户是否为已登录的管理员（role = 3），返回 (user_id, error)"""

    user, error = require_role(3, "无管理员权限")

    if error:
        return None, error

    return user["user_id"], None





# =====================================================
# 管理员信息
# =====================================================


@admin_bp.route(
    "/api/admin/profile",
    methods=["GET"]
)
@jwt_required()
def admin_profile():


    admin_id,error=check_admin()


    if error:

        return error



    db=None
    cursor=None


    try:


        db=get_db()

        cursor=db.cursor()



        cursor.execute(
            """
            SELECT

                id,
                username,
                phone,
                role,
                status,
                create_time

            FROM users

            WHERE id=%s

            """,
            (
                admin_id,
            )
        )



        user=cursor.fetchone()



        return jsonify({

            "code":200,

            "data":user

        })



    except Exception as e:


        return jsonify({

            "code":500,

            "message":str(e)

        }),500



    finally:


        if cursor:

            cursor.close()


        if db:

            db.close()




# =====================================================
# 获取所有用户
# =====================================================


@admin_bp.route(
    "/api/admin/users",
    methods=["GET"]
)
@jwt_required()
def users_list():


    _,error=check_admin()


    if error:

        return error



    db=None
    cursor=None



    try:


        db=get_db()

        cursor=db.cursor()



        cursor.execute(
            """
            SELECT

                id,
                username,
                phone,
                role,
                status,
                create_time


            FROM users

            ORDER BY create_time DESC

            """
        )


        users=cursor.fetchall()



        return jsonify({

            "code":200,

            "data":users

        })



    except Exception as e:


        return jsonify({

            "code":500,

            "message":str(e)

        }),500



    finally:


        if cursor:

            cursor.close()


        if db:

            db.close()

# =====================================================
# 创建教师账号
#
# POST
# /api/admin/teacher/create
#
# JSON:
#
# {
#   username:"teacher01",
#   password:"123456",
#   name:"张老师",
#   department:"计算机学院",
#   phone:"13800000000"
# }
#
# =====================================================


@admin_bp.route(
    "/api/admin/teacher/create",
    methods=["POST"]
)
@jwt_required()
def create_teacher():


    admin_id,error = check_admin()


    if error:

        return error



    data=request.get_json() or {}



    username=data.get(
        "username"
    )


    password=data.get(
        "password"
    )


    name=data.get(
        "name"
    )


    department=data.get(
        "department"
    )


    phone=data.get(
        "phone"
    )



    if not username or not password or not name:


        return jsonify({

            "code":400,

            "message":
            "用户名、密码、姓名不能为空"

        }),400




    db=None

    cursor=None



    try:


        db=get_db()

        cursor=db.cursor()



        # =================================
        # 检查用户名
        # =================================


        cursor.execute(

            """
            SELECT id

            FROM users

            WHERE username=%s

            """,

            (
                username,
            )

        )



        if cursor.fetchone():


            return jsonify({

                "code":400,

                "message":
                "用户名已经存在"

            }),400




        # =================================
        # 创建UUID
        # =================================


        user_id=str(
            uuid4()
        )


        teacher_id=str(
            uuid4()
        )



        password_hash=generate_password_hash(
            password
        )



        # =================================
        # 创建用户
        # role=2 教师
        # =================================


        cursor.execute(

            """
            INSERT INTO users
            (
                id,
                username,
                password,
                role,
                phone,
                status
            )

            VALUES
            (
                %s,
                %s,
                %s,
                2,
                %s,
                1
            )

            """,

            (

                user_id,

                username,

                password_hash,

                phone

            )

        )




        # =================================
        # 创建教师信息
        # =================================


        cursor.execute(

            """
            INSERT INTO teachers
            (
                id,
                user_id,
                name,
                department
            )

            VALUES
            (
                %s,
                %s,
                %s,
                %s
            )

            """,

            (

                teacher_id,

                user_id,

                name,

                department

            )

        )




        db.commit()



        return jsonify({

            "code":200,

            "message":
            "教师创建成功",

            "data":{

                "user_id":
                user_id,


                "teacher_id":
                teacher_id

            }

        })




    except Exception as e:


        if db:

            db.rollback()



        return jsonify({

            "code":500,

            "message":
            "创建教师失败",

            "error":
            str(e)

        }),500



    finally:


        if cursor:

            cursor.close()



        if db:

            db.close()







# =====================================================
# 创建学生账号
#
# POST
# /api/admin/student/create
#
# JSON:
#
# {
# username:"",
# password:"",
# student_no:"",
# name:"",
# class_id:"",
# phone:""
# }
#
# =====================================================


@admin_bp.route(
    "/api/admin/student/create",
    methods=["POST"]
)
@jwt_required()
def create_student():


    admin_id,error=check_admin()



    if error:

        return error




    data=request.get_json() or {}



    username=data.get(
        "username"
    )


    password=data.get(
        "password"
    )


    student_no=data.get(
        "student_no"
    )


    name=data.get(
        "name"
    )


    class_id=data.get(
        "class_id"
    )


    phone=data.get(
        "phone"
    )




    if not username or not password or not student_no or not name:


        return jsonify({

            "code":400,

            "message":
            "参数不能为空"

        }),400





    db=None

    cursor=None



    try:


        db=get_db()

        cursor=db.cursor()




        # =====================================
        # 检查用户名
        # =====================================


        cursor.execute(

            """
            SELECT id

            FROM users

            WHERE username=%s

            """,

            (
                username,
            )

        )



        if cursor.fetchone():


            return jsonify({

                "code":400,

                "message":
                "用户名已经存在"

            }),400




        # =====================================
        # 检查学号
        # =====================================


        cursor.execute(

            """
            SELECT id

            FROM students

            WHERE student_no=%s

            """,

            (
                student_no,
            )

        )


        if cursor.fetchone():


            return jsonify({

                "code":400,

                "message":
                "学号已经存在"

            }),400





        user_id=str(
            uuid4()
        )


        student_id=str(
            uuid4()
        )




        password_hash=generate_password_hash(
            password
        )





        # =====================================
        # 创建用户
        # role=1 学生
        # =====================================


        cursor.execute(

            """
            INSERT INTO users
            (
                id,
                username,
                password,
                role,
                phone,
                status
            )

            VALUES
            (
                %s,
                %s,
                %s,
                1,
                %s,
                1
            )

            """,

            (

                user_id,

                username,

                password_hash,

                phone

            )

        )






        # =====================================
        # 创建学生信息
        # =====================================


        cursor.execute(

            """
            INSERT INTO students
            (
                id,
                user_id,
                student_no,
                name,
                class_id
            )

            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s
            )

            """,

            (

                student_id,

                user_id,

                student_no,

                name,

                class_id

            )

        )





        db.commit()




        return jsonify({

            "code":200,

            "message":
            "学生创建成功",

            "data":{

                "user_id":
                user_id,


                "student_id":
                student_id

            }

        })




    except Exception as e:


        if db:

            db.rollback()



        return jsonify({

            "code":500,

            "message":
            "创建学生失败",

            "error":
            str(e)

        }),500




    finally:


        if cursor:

            cursor.close()



        if db:

            db.close()

# =====================================================
# 创建课程
#
# POST
# /api/admin/courses/create
#
# JSON:
#
# {
#   name:"",
#   teacher_id:"",
#   class_id:"",
#   course_date:"",
#   time:""
# }
#
# =====================================================


@admin_bp.route(
    "/api/admin/courses/create",
    methods=["POST"]
)
@jwt_required()
def create_course():


    admin_id,error=check_admin()


    if error:

        return error



    data=request.get_json() or {}



    name=data.get(
        "name"
    )


    teacher_id=data.get(
        "teacher_id"
    )


    class_id=data.get(
        "class_id"
    )


    course_date=data.get(
        "course_date"
    )


    course_time=data.get(
        "time"
    )




    if not all([
        name,
        teacher_id,
        class_id
    ]):


        return jsonify({

            "code":400,

            "message":
            "课程参数不完整"

        }),400




    db=None

    cursor=None



    try:


        db=get_db()

        cursor=db.cursor()



        # ============================
        # 检查教师
        # ============================


        cursor.execute(

            """
            SELECT id

            FROM teachers

            WHERE id=%s

            """,

            (
                teacher_id,
            )

        )


        if not cursor.fetchone():


            return jsonify({

                "code":404,

                "message":
                "教师不存在"

            }),404





        # ============================
        # 检查班级
        # ============================


        cursor.execute(

            """
            SELECT id

            FROM classes

            WHERE id=%s

            """,

            (
                class_id,
            )

        )



        if not cursor.fetchone():


            return jsonify({

                "code":404,

                "message":
                "班级不存在"

            }),404





        course_id=str(
            uuid4()
        )




        cursor.execute(

            """
            INSERT INTO courses
            (
                id,
                name,
                teacher_id,
                class_id,
                course_date,
                time
            )

            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )

            """,

            (

                course_id,

                name,

                teacher_id,

                class_id,

                course_date,

                course_time

            )

        )



        db.commit()



        return jsonify({

            "code":200,

            "message":
            "课程创建成功",

            "data":{

                "course_id":
                course_id

            }

        })




    except Exception as e:


        if db:

            db.rollback()



        return jsonify({

            "code":500,

            "message":
            "课程创建失败",

            "error":
            str(e)

        }),500




    finally:


        if cursor:

            cursor.close()



        if db:

            db.close()






# =====================================================
# 修改用户密码
#
# PUT
# /api/admin/user/password
#
# JSON:
#
# {
#   user_id:"",
#   password:"123456"
# }
#
# =====================================================



@admin_bp.route(
    "/api/admin/user/password",
    methods=["PUT"]
)
@jwt_required()
def update_password():


    admin_id,error=check_admin()


    if error:

        return error



    data=request.get_json() or {}



    user_id=data.get(
        "user_id"
    )


    password=data.get(
        "password"
    )



    if not user_id or not password:


        return jsonify({

            "code":400,

            "message":
            "参数错误"

        }),400





    db=None

    cursor=None



    try:


        db=get_db()

        cursor=db.cursor()



        cursor.execute(

            """
            UPDATE users

            SET password=%s

            WHERE id=%s

            """,

            (

                generate_password_hash(
                    password
                ),

                user_id

            )

        )



        db.commit()



        return jsonify({

            "code":200,

            "message":
            "密码修改成功"

        })




    except Exception as e:


        if db:

            db.rollback()



        return jsonify({

            "code":500,

            "message":
            "密码修改失败",

            "error":
            str(e)

        }),500




    finally:


        if cursor:

            cursor.close()



        if db:

            db.close()







# =====================================================
# 修改账号状态
#
# PUT
# /api/admin/user/status
#
# JSON:
#
# {
#   user_id:"",
#   status:1
# }
#
# =====================================================



@admin_bp.route(
    "/api/admin/user/status",
    methods=["PUT"]
)
@jwt_required()
def update_user_status():


    admin_id,error=check_admin()


    if error:

        return error




    data=request.get_json() or {}



    user_id=data.get(
        "user_id"
    )


    status=data.get(
        "status"
    )



    if user_id is None or status is None:


        return jsonify({

            "code":400,

            "message":
            "参数错误"

        }),400





    db=None

    cursor=None



    try:


        db=get_db()

        cursor=db.cursor()



        cursor.execute(

            """
            UPDATE users

            SET status=%s

            WHERE id=%s

            """,

            (

                status,

                user_id

            )

        )



        db.commit()



        return jsonify({

            "code":200,

            "message":
            "账号状态修改成功"

        })




    except Exception as e:


        if db:

            db.rollback()



        return jsonify({

            "code":500,

            "message":
            "状态修改失败",

            "error":
            str(e)

        }),500




    finally:


        if cursor:

            cursor.close()



        if db:

            db.close()


# =====================================================
# 获取教师列表（含登录账号信息）
#
# GET /api/admin/teachers
#
# =====================================================


@admin_bp.route(
    "/api/admin/teachers",
    methods=["GET"]
)
@jwt_required()
def teachers_list():

    _, error = check_admin()

    if error:
        return error

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            """
            SELECT
                t.id AS teacher_id,
                t.user_id,
                t.name,
                t.department,
                t.class_id,
                c.name AS class_name,
                u.username,
                u.phone,
                u.status,
                u.create_time
            FROM teachers t
            INNER JOIN users u
                ON u.id = t.user_id
            LEFT JOIN classes c
                ON c.id = t.class_id
            ORDER BY u.create_time DESC, t.name ASC
            """
        )

        teachers = cursor.fetchall()

        return jsonify({
            "code": 200,
            "data": teachers
        })

    except Exception as e:

        return jsonify({
            "code": 500,
            "message": "获取教师列表失败",
            "error": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =====================================================
# 获取学生列表（含班级、登录账号信息）
#
# GET /api/admin/students
#
# =====================================================


@admin_bp.route(
    "/api/admin/students",
    methods=["GET"]
)
@jwt_required()
def students_list():

    _, error = check_admin()

    if error:
        return error

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            """
            SELECT
                s.id AS student_id,
                s.user_id,
                s.student_no,
                s.name,
                s.class_id,
                c.name AS class_name,
                u.username,
                u.phone,
                u.status,
                u.create_time
            FROM students s
            INNER JOIN users u
                ON u.id = s.user_id
            LEFT JOIN classes c
                ON c.id = s.class_id
            ORDER BY s.student_no ASC
            """
        )

        students = cursor.fetchall()

        return jsonify({
            "code": 200,
            "data": students
        })

    except Exception as e:

        return jsonify({
            "code": 500,
            "message": "获取学生列表失败",
            "error": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =====================================================
# 获取班级列表
#
# GET /api/admin/classes
#
# =====================================================


@admin_bp.route(
    "/api/admin/classes",
    methods=["GET"]
)
@jwt_required()
def classes_list():

    _, error = check_admin()

    if error:
        return error

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            """
            SELECT
                c.id,
                c.name,
                c.grade,
                t.name AS teacher_name
            FROM classes c
            LEFT JOIN teachers t
                ON t.id = c.teacher_id
            ORDER BY c.grade DESC, c.name ASC
            """
        )

        classes = cursor.fetchall()

        return jsonify({
            "code": 200,
            "data": classes
        })

    except Exception as e:

        return jsonify({
            "code": 500,
            "message": "获取班级列表失败",
            "error": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =====================================================
# 获取课程列表（含教师、班级名称）
#
# GET /api/admin/courses
#
# =====================================================


@admin_bp.route(
    "/api/admin/courses",
    methods=["GET"]
)
@jwt_required()
def courses_list():

    _, error = check_admin()

    if error:
        return error

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            """
            SELECT
                co.id,
                co.name,
                co.teacher_id,
                co.class_id,
                co.course_date,
                co.time,
                t.name AS teacher_name,
                c.name AS class_name
            FROM courses co
            INNER JOIN teachers t
                ON t.id = co.teacher_id
            INNER JOIN classes c
                ON c.id = co.class_id
            ORDER BY co.course_date DESC, co.time ASC
            """
        )

        courses = cursor.fetchall()

        for course in courses:
            if course.get("course_date") and hasattr(
                course["course_date"], "isoformat"
            ):
                course["course_date"] = course["course_date"].isoformat()

        return jsonify({
            "code": 200,
            "data": courses
        })

    except Exception as e:

        return jsonify({
            "code": 500,
            "message": "获取课程列表失败",
            "error": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =====================================================
# 创建班级
#
# POST /api/admin/class/create
#
# JSON:
# {
#   "name": "软件2403班",
#   "grade": "2024级",
#   "teacher_id": "可选，班主任教师ID"
# }
#
# =====================================================


@admin_bp.route(
    "/api/admin/class/create",
    methods=["POST"]
)
@jwt_required()
def create_class():

    _, error = check_admin()

    if error:
        return error

    data = request.get_json() or {}

    name = data.get("name")
    grade = data.get("grade")
    teacher_id = data.get("teacher_id")

    if not name:
        return jsonify({
            "code": 400,
            "message": "班级名称不能为空"
        }), 400

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        if teacher_id:
            cursor.execute(
                "SELECT id FROM teachers WHERE id = %s",
                (teacher_id,)
            )
            if not cursor.fetchone():
                return jsonify({
                    "code": 404,
                    "message": "教师不存在"
                }), 404

        class_id = str(uuid4())

        cursor.execute(
            """
            INSERT INTO classes (id, name, grade, teacher_id)
            VALUES (%s, %s, %s, %s)
            """,
            (class_id, name, grade, teacher_id)
        )

        db.commit()

        return jsonify({
            "code": 200,
            "message": "班级创建成功",
            "data": {"class_id": class_id}
        })

    except Exception as e:

        if db:
            db.rollback()

        return jsonify({
            "code": 500,
            "message": "班级创建失败",
            "error": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =====================================================
# 删除班级
#
# DELETE /api/admin/class/<class_id>
#
# 删除班级时：
#   - 关联课程级联删除（courses.class_id FK ON DELETE CASCADE）
#   - 学生 class_id 置空（students.class_id FK ON DELETE SET NULL）
#   - 教师 class_id 置空（teachers.class_id FK ON DELETE SET NULL）
#
# =====================================================


@admin_bp.route(
    "/api/admin/class/<class_id>",
    methods=["DELETE"]
)
@jwt_required()
def delete_class(class_id):

    _, error = check_admin()

    if error:
        return error

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            "SELECT id, name FROM classes WHERE id = %s",
            (class_id,)
        )
        cls = cursor.fetchone()

        if not cls:
            return jsonify({
                "code": 404,
                "message": "班级不存在"
            }), 404

        cursor.execute(
            "DELETE FROM classes WHERE id = %s",
            (class_id,)
        )

        db.commit()

        return jsonify({
            "code": 200,
            "message": "班级删除成功"
        })

    except Exception as e:

        if db:
            db.rollback()

        return jsonify({
            "code": 500,
            "message": "班级删除失败",
            "error": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =====================================================
# 删除教师账户
#
# DELETE /api/admin/teacher/<teacher_id>
#
# 删除 users 记录，teachers 表由 FK (teachers.user_id) ON DELETE CASCADE 级联删除。
# 该教师的课程由 courses.teacher_id FK ON DELETE CASCADE 级联删除。
#
# =====================================================


@admin_bp.route(
    "/api/admin/teacher/<teacher_id>",
    methods=["DELETE"]
)
@jwt_required()
def delete_teacher(teacher_id):

    _, error = check_admin()

    if error:
        return error

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            "SELECT id, user_id, name FROM teachers WHERE id = %s",
            (teacher_id,)
        )
        teacher = cursor.fetchone()

        if not teacher:
            return jsonify({
                "code": 404,
                "message": "教师不存在"
            }), 404

        cursor.execute(
            "DELETE FROM users WHERE id = %s",
            (teacher["user_id"],)
        )

        db.commit()

        return jsonify({
            "code": 200,
            "message": "教师账户删除成功"
        })

    except Exception as e:

        if db:
            db.rollback()

        return jsonify({
            "code": 500,
            "message": "教师账户删除失败",
            "error": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =====================================================
# 删除学生账户
#
# DELETE /api/admin/student/<student_id>
#
# 删除 users 记录，students 表由 FK (students.user_id) ON DELETE CASCADE 级联删除。
#
# =====================================================


@admin_bp.route(
    "/api/admin/student/<student_id>",
    methods=["DELETE"]
)
@jwt_required()
def delete_student(student_id):

    _, error = check_admin()

    if error:
        return error

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            "SELECT id, user_id, name FROM students WHERE id = %s",
            (student_id,)
        )
        student = cursor.fetchone()

        if not student:
            return jsonify({
                "code": 404,
                "message": "学生不存在"
            }), 404

        cursor.execute(
            "DELETE FROM users WHERE id = %s",
            (student["user_id"],)
        )

        db.commit()

        return jsonify({
            "code": 200,
            "message": "学生账户删除成功"
        })

    except Exception as e:

        if db:
            db.rollback()

        return jsonify({
            "code": 500,
            "message": "学生账户删除失败",
            "error": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =====================================================
# 删除课程
#
# DELETE /api/admin/course/<course_id>
#
# 关联签到任务由 attendance_task.course_id FK ON DELETE CASCADE 级联删除。
#
# =====================================================


@admin_bp.route(
    "/api/admin/course/<course_id>",
    methods=["DELETE"]
)
@jwt_required()
def delete_course(course_id):

    _, error = check_admin()

    if error:
        return error

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            "SELECT id, name FROM courses WHERE id = %s",
            (course_id,)
        )
        course = cursor.fetchone()

        if not course:
            return jsonify({
                "code": 404,
                "message": "课程不存在"
            }), 404

        cursor.execute(
            "DELETE FROM courses WHERE id = %s",
            (course_id,)
        )

        db.commit()

        return jsonify({
            "code": 200,
            "message": "课程删除成功"
        })

    except Exception as e:

        if db:
            db.rollback()

        return jsonify({
            "code": 500,
            "message": "课程删除失败",
            "error": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =====================================================
# 分配学生到班级
#
# PUT /api/admin/student/class
#
# JSON:
# {
#   "student_id": "",
#   "class_id": ""   // 传 null 或空字符串表示移出班级
# }
#
# =====================================================


@admin_bp.route(
    "/api/admin/student/class",
    methods=["PUT"]
)
@jwt_required()
def assign_student_class():

    _, error = check_admin()

    if error:
        return error

    data = request.get_json() or {}

    student_id = data.get("student_id")
    class_id = data.get("class_id") or None

    if not student_id:
        return jsonify({
            "code": 400,
            "message": "学生ID不能为空"
        }), 400

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            "SELECT id FROM students WHERE id = %s",
            (student_id,)
        )
        if not cursor.fetchone():
            return jsonify({
                "code": 404,
                "message": "学生不存在"
            }), 404

        if class_id:
            cursor.execute(
                "SELECT id FROM classes WHERE id = %s",
                (class_id,)
            )
            if not cursor.fetchone():
                return jsonify({
                    "code": 404,
                    "message": "班级不存在"
                }), 404

        cursor.execute(
            "UPDATE students SET class_id = %s WHERE id = %s",
            (class_id, student_id)
        )

        db.commit()

        return jsonify({
            "code": 200,
            "message": "学生班级分配成功"
        })

    except Exception as e:

        if db:
            db.rollback()

        return jsonify({
            "code": 500,
            "message": "学生班级分配失败",
            "error": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =====================================================
# 分配教师到班级
#
# PUT /api/admin/teacher/class
#
# JSON:
# {
#   "teacher_id": "",
#   "class_id": ""   // 传 null 或空字符串表示移出班级
# }
#
# =====================================================


@admin_bp.route(
    "/api/admin/teacher/class",
    methods=["PUT"]
)
@jwt_required()
def assign_teacher_class():

    _, error = check_admin()

    if error:
        return error

    data = request.get_json() or {}

    teacher_id = data.get("teacher_id")
    class_id = data.get("class_id") or None

    if not teacher_id:
        return jsonify({
            "code": 400,
            "message": "教师ID不能为空"
        }), 400

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            "SELECT id FROM teachers WHERE id = %s",
            (teacher_id,)
        )
        if not cursor.fetchone():
            return jsonify({
                "code": 404,
                "message": "教师不存在"
            }), 404

        if class_id:
            cursor.execute(
                "SELECT id FROM classes WHERE id = %s",
                (class_id,)
            )
            if not cursor.fetchone():
                return jsonify({
                    "code": 404,
                    "message": "班级不存在"
                }), 404

        cursor.execute(
            "UPDATE teachers SET class_id = %s WHERE id = %s",
            (class_id, teacher_id)
        )

        db.commit()

        return jsonify({
            "code": 200,
            "message": "教师班级分配成功"
        })

    except Exception as e:

        if db:
            db.rollback()

        return jsonify({
            "code": 500,
            "message": "教师班级分配失败",
            "error": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()