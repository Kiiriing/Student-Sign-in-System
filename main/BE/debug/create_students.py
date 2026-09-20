# -*- coding: utf-8 -*-
"""
一键批量创建学生账号

用法：
    python create_students.py

功能：
    - 为学生名单中的每个学生创建 users + students 两条记录
    - 用户名 = 学号，密码 = 123456（Werkzeug 哈希）
    - 班级 ID 固定，手机号留空
    - 已存在的用户名会跳过（幂等）
"""

import sys
import os

# 确保能导入上级目录的 database.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from uuid import uuid4
from werkzeug.security import generate_password_hash
from database import get_db


# ============================================================
# 配置
# ============================================================

CLASS_ID = "abfb5cae-84d4-4aff-b893-40cd42666d18"
DEFAULT_PASSWORD = "123456"
ROLE_STUDENT = 1

# 学生名单：(学号, 姓名)
STUDENTS = [
    ("253201301", "吕嘉兴"),
    ("253201302", "杨承瑞"),
    ("253201303", "刘旭"),
    ("253201304", "冯载轩"),
    ("253201305", "王至轩"),
    ("253201306", "贾澎博"),
    ("253201307", "张浩然"),
    ("253201308", "张铠鹏"),
    ("253201309", "王浩宇"),
    ("253201310", "闫霄同"),
    ("253201311", "高政煜"),
    ("253201312", "肖文宇"),
    ("253201313", "赵亦寒"),
    ("253201314", "宋新宇"),
    ("253201315", "石卓烁"),
    ("253201316", "王鸿儒"),
    ("253201317", "张迦恩"),
    ("253201318", "刘家烨"),
    ("253201319", "刘镕赫"),
    ("253201320", "周语轩"),
    ("253201321", "龙子河"),
    ("253201322", "陈茂杰"),
    ("253201323", "刘佳博"),
    ("253201324", "姬罡"),
    ("253201325", "陈羽泽"),
    ("253201326", "王思源"),
    ("253201327", "邓天成"),
    ("253201328", "刘敬坤"),
    ("253201329", "张鑫睿"),
    ("253201330", "李武斌"),
    ("253201331", "张天烁"),
    ("253201332", "芦睿"),
    ("253201333", "李宗岳"),
    ("253201334", "王鹏宇"),
    ("253201335", "康济恩"),
    ("253201336", "施思年"),
    ("253201337", "雷俊颖"),
    ("253201338", "库锦芸"),
    ("253201339", "高璟怡"),
    ("253201340", "田嘉慧"),
    ("253201341", "李晔霞"),
    ("253201342", "徐嘉嘉"),
]


# ============================================================
# 主逻辑
# ============================================================

def main():
    conn = None
    created = 0
    skipped = 0
    errors = 0

    try:
        conn = get_db()
        cursor = conn.cursor()

        # 预先查一次班级是否存在
        cursor.execute("SELECT id, name FROM classes WHERE id = %s", (CLASS_ID,))
        cls = cursor.fetchone()
        if not cls:
            print(f"[错误] 班级 ID 不存在: {CLASS_ID}")
            return
        print(f"目标班级: {cls['name']} ({cls['id']})")
        print(f"待创建学生数: {len(STUDENTS)}")
        print("-" * 60)

        for student_no, name in STUDENTS:
            try:
                # 检查用户名是否已存在
                cursor.execute(
                    "SELECT id FROM users WHERE username = %s",
                    (student_no,)
                )
                existing = cursor.fetchone()

                if existing:
                    # 用户名已存在，检查姓名是否一致，不一致则更新
                    cursor.execute(
                        "SELECT name FROM students WHERE student_no = %s",
                        (student_no,)
                    )
                    stu = cursor.fetchone()
                    if stu and stu["name"] != name:
                        cursor.execute(
                            "UPDATE students SET name = %s WHERE student_no = %s",
                            (name, student_no)
                        )
                        conn.commit()
                        print(f"[更新] {student_no} {stu['name']} → {name}")
                    else:
                        skipped += 1
                        print(f"[跳过] {student_no} {name} - 已存在")
                    continue

                # 创建用户
                user_id = str(uuid4())
                password_hash = generate_password_hash(DEFAULT_PASSWORD)

                cursor.execute(
                    """
                    INSERT INTO users (id, username, password, role, phone, status)
                    VALUES (%s, %s, %s, %s, NULL, 1)
                    """,
                    (user_id, student_no, password_hash, ROLE_STUDENT)
                )

                # 创建学生
                student_id = str(uuid4())
                cursor.execute(
                    """
                    INSERT INTO students (id, user_id, student_no, name, class_id)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (student_id, user_id, student_no, name, CLASS_ID)
                )

                conn.commit()
                created += 1
                print(f"[成功] {student_no} {name}")

            except Exception as e:
                errors += 1
                print(f"[失败] {student_no} {name} - {e}")
                conn.rollback()
                continue

        print("-" * 60)
        print(f"完成：成功 {created} 个，跳过 {skipped} 个，失败 {errors} 个")
        print(f"默认密码: {DEFAULT_PASSWORD}")

    except Exception as e:
        print(f"[致命错误] {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    main()
