from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash

from database import get_db


# ============================================================
# Blueprint
# ============================================================

login_bp = Blueprint("login", __name__)


# ============================================================
# 登录接口
# POST /api/auth/login
# ============================================================

@login_bp.route("/api/auth/login", methods=["POST"])
def login():
    """
    用户登录

    请求：

    学生：
    {
        "username": "20240001",
        "password": "123456",
        "device_id": "xxxx"
    }

    教师/管理员：
    {
        "username": "teacher01",
        "password": "123456",
        "device_id": "xxxx"
    }
    """

    data = request.get_json(silent=True) or {}

    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))
    device_id = str(data.get("device_id", "")).strip()

    # --------------------------------------------------------
    # 参数检查
    # --------------------------------------------------------

    if not username:
        return jsonify({
            "code": 400,
            "message": "请输入账号"
        }), 400

    if not password:
        return jsonify({
            "code": 400,
            "message": "请输入密码"
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

        # ====================================================
        # 第一步：查询用户
        #
        # 学生：
        #   username 可以是 student_no
        #
        # 教师/管理员：
        #   username 使用 users.username
        # ====================================================

        sql = """
            SELECT
                u.id AS user_id,
                u.username,
                u.password,
                u.role,
                u.phone,
                u.status,

                s.id AS student_id,
                s.student_no,
                s.name AS student_name,
                s.class_id,

                c.name AS class_name,

                t.id AS teacher_id,
                t.name AS teacher_name,
                t.department

            FROM users u

            LEFT JOIN students s
                ON s.user_id = u.id

            LEFT JOIN classes c
                ON c.id = s.class_id

            LEFT JOIN teachers t
                ON t.user_id = u.id

            WHERE
                u.username = %s
                OR s.student_no = %s
                OR s.name = %s

            LIMIT 1
        """

        cursor.execute(sql, (username, username, username))

        user = cursor.fetchone()

        # ====================================================
        # 用户不存在
        # ====================================================

        if not user:
            return jsonify({
                "code": 401,
                "message": "账号或密码错误"
            }), 401

        # ====================================================
        # 用户状态
        #
        # 这里按照：
        # 1 = 正常
        # 0 = 禁用
        # ====================================================

        if user["status"] != 1:
            return jsonify({
                "code": 403,
                "message": "账号已被禁用"
            }), 403

        # ====================================================
        # 密码验证
        # ====================================================

        if not check_password_hash(
            user["password"],
            password
        ):
            return jsonify({
                "code": 401,
                "message": "账号或密码错误"
            }), 401

        # ====================================================
        # 第二步：学生每日设备限制
        #
        # 只有 role = 1 的学生执行。
        #
        # 规则：
        #
        # 今天：
        #
        # 设备A -> 张三
        # 设备A -> 张三   允许
        # 设备A -> 李四   拒绝
        #
        # 明天：
        #
        # 设备A -> 李四   允许
        #
        # ====================================================

        if user["role"] == 1:

            # ------------------------------------------------
            # 检查今天这个设备是否已经登录过其他账号
            # ------------------------------------------------

            check_sql = """
                SELECT
                    id,
                    user_id,
                    login_date
                FROM device_login_record
                WHERE device_id = %s
                  AND login_date = CURDATE()
                LIMIT 1
            """

            cursor.execute(check_sql, (device_id,))

            device_record = cursor.fetchone()

            if device_record:

                # --------------------------------------------
                # 今天这个设备已经登录过
                # --------------------------------------------

                if device_record["user_id"] != user["user_id"]:

                    return jsonify({
                        "code": 403,
                        "message": "该设备今天已经登录其他学生账号，每台设备每天只能登录一个学生账号"
                    }), 403

            else:

                # --------------------------------------------
                # 今天第一次登录
                #
                # 写入设备登录记录
                # --------------------------------------------

                insert_sql = """
                    INSERT INTO device_login_record
                    (
                        device_id,
                        user_id,
                        login_date
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        CURDATE()
                    )
                """

                cursor.execute(
                    insert_sql,
                    (
                        device_id,
                        user["user_id"]
                    )
                )

                conn.commit()

        # ====================================================
        # 第三步：创建 JWT
        #
        # 说明：
        # identity 只用 user_id 字符串（flask-jwt-extended 所有版本都兼容）
        # role 等额外信息通过 additional_claims 写入 JWT payload 顶层 claims
        # 解码 get_jwt_identity() 返回 str(user_id)
        # 解码 get_jwt() 返回的 claims 顶层有 "role" 字段
        # ====================================================

        access_token = create_access_token(
            identity=str(user["user_id"]),
            additional_claims={
                "role": int(user["role"])
            }
        )

        # ====================================================
        # 第四步：根据角色返回数据
        # ====================================================

        result = {
            "code": 200,
            "message": "登录成功",
            "access_token": access_token,

            "user_id": str(user["user_id"]),
            "username": user["username"],
            "role": int(user["role"])
        }

        # ====================================================
        # 学生
        # ====================================================

        if user["role"] == 1:

            result.update({
                "student_id": str(user["student_id"])
                if user["student_id"]
                else None,

                "student_no": user["student_no"],

                "student_name": user["student_name"],

                "class_name": user["class_name"]
            })

        # ====================================================
        # 教师
        # ====================================================

        elif user["role"] == 2:

            result.update({
                "teacher_id": str(user["teacher_id"])
                if user["teacher_id"]
                else None,

                "teacher_name": user["teacher_name"],

                "department": user["department"]
            })

        # ====================================================
        # 管理员
        # ====================================================

        elif user["role"] == 3:

            result.update({
                "admin_name": user["username"]
            })

        return jsonify(result), 200

    except Exception as e:

        # 如果发生异常，回滚事务
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass

        print("登录接口错误：", e)

        return jsonify({
            "code": 500,
            "message": "服务器内部错误",
            "error": str(e)
        }), 500

    finally:

        if conn:
            try:
                conn.close()
            except Exception:
                pass