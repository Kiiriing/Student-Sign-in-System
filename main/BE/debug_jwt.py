# -*- coding: utf-8 -*-
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import base64
import json

# ========== 在这里粘贴你登录拿到的 access_token（复制eyJ开头的完整字符串）==========
TOKEN = ""  # 示例: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6...太长省略...xxxxxx"


def decode_jwt_payload(token):
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return "[错误] JWT 格式不对，应该有3个 . 分隔的部分"
        payload_b64 = parts[1]
        # base64url 解码补 padding
        padding = 4 - len(payload_b64) % 4
        if padding != 4:
            payload_b64 += "=" * padding
        payload_bytes = base64.urlsafe_b64decode(payload_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))
        return payload
    except Exception as e:
        return f"[解码失败] {type(e).__name__}: {e}"


if __name__ == "__main__":
    if not TOKEN.strip():
        print("=" * 60)
        print("请先用学生账号登录，复制 F12 -> Application -> LocalStorage 里的 access_token")
        print("粘贴到本脚本顶部的 TOKEN = \"...\" 字符串里，然后运行：python debug_jwt.py")
        print("=" * 60)
        # 或者直接在命令行传 token: python debug_jwt.py eyJxxxx....
        if len(sys.argv) > 1:
            token_arg = sys.argv[1]
            print("\n使用命令行传入的 token 进行解码：\n")
            payload = decode_jwt_payload(token_arg)
            print("JWT payload (JSON 格式):")
            print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        payload = decode_jwt_payload(TOKEN)
        print("=" * 60)
        print("JWT payload 内容:")
        print("=" * 60)
        if isinstance(payload, str):
            print(payload)
        else:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            print("\n关键字段分析:")
            print("  - sub (identity 字段):", payload.get("sub"))
            print("  - sub 的类型:", type(payload.get("sub")).__name__)
            print("  - 自定义 claims:", {k: v for k, v in payload.items() if k not in
                                           ["sub", "iat", "exp", "nbf", "jti", "fresh", "type",
                                            "csrf_access_token", "csrf_refresh_token"]})
