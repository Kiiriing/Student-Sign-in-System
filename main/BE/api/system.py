# -*- coding: utf-8 -*-
# api/system.py
# 系统公共模块（无需登录即可访问）
#
# 当前提供：系统更新日志 /api/system/updates

from flask import Blueprint, request, jsonify

from core.database import get_db


# ============================================================
# Blueprint
# ============================================================

system_bp = Blueprint("system", __name__)


# ============================================================
# 建表 + 初始数据
# ============================================================

# 更新日志首次部署时写入的初始内容（仅在表为空时写入一次）
_INITIAL_UPDATES = [
    ("新增", "创建课程支持「重复课程」：可在日期区间内，同教师 / 同班级 / 同时间段连续多天创建。"),
    ("新增", "账户管理 · 学生列表新增学号筛选，支持姓名 / 学号 / 用户名 / 班级 / 手机号 / 状态的模糊匹配。"),
    ("新增", "学生列表与已排课程列表加入前端分页（每页 20 条）与搜索，大数据量下更流畅。"),
    ("优化", "全部下拉菜单改为自绘组件：选项样式美化，展开 / 收起带过渡动画与箭头旋转。"),
    ("优化", "筛选栏的下拉框与日期框统一为定长宽度，排列更整齐。"),
    ("优化", "上课时间段改为自定义时 / 分选择，个位数字自动补 0。"),
    ("修复", "修复下拉框滚轮滚动时面板意外消失的问题。"),
    ("修复", "日期选择框支持点击整框弹出原生选择器。"),
    ("修复", "修复筛选后滚动条消失导致页面盒子被拉伸的抖动问题。"),
    ("修复", "修复课堂点名「音色」文字与下拉挤在同一列、学生姓名被迫换行的问题。"),
]


def ensure_update_table():
    """
    创建更新日志表（不存在时），并在表为空时写入初始数据

    项目没有迁移框架，这里用幂等的 CREATE TABLE IF NOT EXISTS 保证表一定存在。
    """
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS `update_log` (
              `update_id` bigint NOT NULL AUTO_INCREMENT COMMENT '更新记录ID',
              `tag` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '类型：新增/优化/修复',
              `content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '更新内容',
              `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
              PRIMARY KEY (`update_id`),
              INDEX `idx_update_created` (`created_at`)
            ) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '系统更新日志表'
            """
        )

        cursor.execute("SELECT COUNT(*) AS cnt FROM `update_log`")
        row = cursor.fetchone()
        if row and row["cnt"] == 0:
            cursor.executemany(
                "INSERT INTO `update_log` (`tag`, `content`) VALUES (%s, %s)",
                _INITIAL_UPDATES
            )
    finally:
        cursor.close()
        db.close()


# 模块导入时尝试建表；数据库暂时不可用时不阻塞服务启动
try:
    ensure_update_table()
except Exception as e:  # pragma: no cover - 仅用于启动兜底
    print(f"[更新日志] 初始化表失败：{e}")


# ============================================================
# 更新日志分页查询
# GET /api/system/updates?page=1
# ============================================================

@system_bp.route("/api/system/updates", methods=["GET"])
def list_updates():
    """
    按日期分页获取系统更新日志（一天一页，日期倒序）

    请求参数：

        page  页码（对应第几天，从 1 开始），默认 1

    说明：

        同一天的所有更新记录始终在同一页返回，
        不会被拆分到不同页；翻页即翻到更早的日期。
    """
    try:
        page = max(int(request.args.get("page", 1)), 1)
    except (TypeError, ValueError):
        page = 1

    db = None
    cursor = None
    try:
        db = get_db()
        cursor = db.cursor()

        # 更新总条数（用于「共 x 次更新」）
        cursor.execute("SELECT COUNT(*) AS cnt FROM `update_log`")
        total = cursor.fetchone()["cnt"]

        # 日期列表（倒序）：一天一页
        # 注意：这条查询没有参数，pymysql 不做 % 转义，这里用单个 % 即可
        cursor.execute(
            """
            SELECT DATE_FORMAT(`created_at`, '%Y-%m-%d') AS date
            FROM `update_log`
            GROUP BY date
            ORDER BY date DESC
            """
        )
        dates = [row["date"] for row in cursor.fetchall()]

        total_pages = len(dates) if dates else 1
        page = min(page, total_pages)
        page_date = dates[page - 1] if dates else None

        rows = []
        if page_date:
            cursor.execute(
                """
                SELECT `update_id`, `tag`, `content`,
                       DATE_FORMAT(`created_at`, '%%Y-%%m-%%d') AS date,
                       DATE_FORMAT(`created_at`, '%%Y-%%m-%%d %%H:%%i') AS created_at
                FROM `update_log`
                WHERE DATE_FORMAT(`created_at`, '%%Y-%%m-%%d') = %s
                ORDER BY FIELD(`tag`, '新增', '优化', '修复'),
                         `created_at` DESC, `update_id` DESC
                """,
                (page_date,)
            )
            rows = cursor.fetchall()

        return jsonify({
            "code": 200,
            "message": "ok",
            "data": {
                "list": rows,
                "total": total,              # 更新总条数
                "page": page,                # 当前第几页（第几天）
                "total_pages": total_pages   # 总天数（一天一页）
            }
        })

    except Exception as e:
        return jsonify({
            "code": 500,
            "message": "获取更新日志失败",
            "error": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()