# auth_utils.py
# JWT 身份解析与角色校验
#
# student.py / teacher.py / admin.py 三个模块共用同一套逻辑，
# 原先各自复制了一份（还带着调试 print），这里统一维护。

import json

from flask import jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity


def get_current_user():
    """
    从 JWT 中解析当前登录用户

    返回：
    {
        "user_id": "...",
        "role": 1
    }

    兼容两种身份格式：

      1. identity 是 dict（旧登录格式）
         → user_id / role 都在 identity 里

      2. identity 是 user_id 字符串（当前 login.py 的格式）
         → user_id 取 identity，role 取 claims 顶层
    """

    identity = get_jwt_identity()
    claims = get_jwt()

    user_id = None
    role = None

    # ========== 格式1：identity 是 dict（旧登录格式）==========
    if isinstance(identity, dict):
        user_id = identity.get("user_id")
        role = identity.get("role")

    # ========== 格式2：identity 是字符串 user_id（新登录格式）==========
    elif isinstance(identity, (str, int)):
        user_id = str(identity)
        role = claims.get("role")

        # 兼容 role 被 JSON 字符串化进 sub 的极端情况
        if role is None and isinstance(claims.get("sub"), str) and claims["sub"].startswith("{"):
            try:
                sub_dict = json.loads(claims["sub"])
            except Exception:
                sub_dict = None

            if isinstance(sub_dict, dict):
                user_id = sub_dict.get("user_id", user_id)
                role = sub_dict.get("role")

    return {"user_id": user_id, "role": role}


def require_role(role, message):
    """
    校验当前登录用户的角色

    参数：
        role    要求的角色（1=学生 / 2=教师 / 3=管理员）
        message 角色不匹配时的提示语

    返回：
        校验通过 → (user, None)
        校验失败 → (None, (jsonify(...), HTTP 状态码))
    """

    user = get_current_user()

    if not user["user_id"]:
        return None, (
            jsonify({
                "code": 401,
                "message": "登录信息无效"
            }),
            401
        )

    try:
        current_role = int(user["role"])
    except (TypeError, ValueError):
        current_role = 0

    if current_role != role:
        return None, (
            jsonify({
                "code": 403,
                "message": message
            }),
            403
        )

    return user, None