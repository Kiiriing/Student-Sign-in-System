# -*- coding: utf-8 -*-
# core/backup.py
# 数据库空闲自动备份
#
# 约定：
#
#   1. 距最后一次「数据改动」满 30 分钟 → 自动把整库（表结构 + 数据）导出成 .sql
#   2. 导出文件统一放在 main/sql 目录，命名 student_signin{MMDD}_{HHMM}.sql
#   3. 每天只保留一份：新文件写成功之后，再删掉当天的旧文件
#      （顺序不能反：中途失败时至少还留着上一份，不会新旧两空）
#
# 说明：
#
#   - 「数据改动」由 core/database.py 的游标包装打时间戳，
#     只认真正改到行的 INSERT / UPDATE / DELETE / REPLACE；
#   - 导出用 mysqldump 的 --single-transaction，是快照读，不锁表、不影响正常读写；
#   - 守护线程，任何异常只打日志，不中断服务。

import glob
import os
import re
import shutil
import subprocess
import threading
import time

from datetime import datetime

from core.database import MYSQL_CONFIG, get_last_write_at


# ============================================================
# 配置
# ============================================================

# 导出目录：main/sql（本文件是 main/BE/core/backup.py，上溯三层到 main）
SQL_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "sql",
)

# 空闲多久没改动数据就导出一次（秒）
IDLE_SECONDS = 30 * 60

# 守护线程多久检查一次（秒）
POLL_SECONDS = 60

# 导出文件名前缀
DUMP_PREFIX = "student_signin"

# 只匹配本功能生成的文件名：student_signin{MMDD}_{HHMM}.sql
# 历史基线文件（student_signin0921.sql 等）不带 MMDD_HHMM，不会被匹配到
_DUMP_NAME_PATTERN = re.compile(
    "^" + DUMP_PREFIX + r"(\d{4})_(\d{4})\.sql$"
)

# PATH 里找不到 mysqldump 时，按这些位置再找一遍
_MYSQLDUMP_CANDIDATES = (
    r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe",
    r"C:\Program Files (x86)\MySQL\MySQL Server 8.0\bin\mysqldump.exe",
    r"C:\Program Files\MySQL\MySQL Workbench 8.0\mysqldump.exe",
    r"C:\xampp\mysql\bin\mysqldump.exe",
)

# 版本号带在路径里的安装目录
_MYSQLDUMP_GLOBS = (
    r"C:\Program Files\MySQL\MySQL Server *\bin\mysqldump.exe",
    r"C:\Program Files (x86)\MySQL\MySQL Server *\bin\mysqldump.exe",
)


_started = False
_start_lock = threading.Lock()

# 上次导出对应的「改动时间」，用于判断这之后有没有新改动
_last_dump_write_at = None


# ============================================================
# 基础工具
# ============================================================

def _log(message):
    print("[自动备份] %s" % message)


def find_mysqldump():
    """定位 mysqldump：先查 PATH，再查常见安装目录；找不到返回 None"""

    found = shutil.which("mysqldump")

    if found:
        return found

    for path in _MYSQLDUMP_CANDIDATES:

        if os.path.isfile(path):
            return path

    for pattern in _MYSQLDUMP_GLOBS:

        # 反向排序：MySQL Server 8.0 优先于 5.7
        for path in sorted(glob.glob(pattern), reverse=True):

            if os.path.isfile(path):
                return path

    return None


def dump_file_name(now=None):
    """按 student_signin{MMDD}_{HHMM}.sql 拼出本次导出文件名"""

    now = now or datetime.now()

    return "%s%s_%s.sql" % (
        DUMP_PREFIX,
        now.strftime("%m%d"),
        now.strftime("%H%M"),
    )


# ============================================================
# 导出
# ============================================================

def _run_mysqldump(target):
    """把整库（结构 + 数据）导出到 target；失败抛异常"""

    exe = find_mysqldump()

    if not exe:
        raise RuntimeError("找不到 mysqldump.exe，无法导出（请把它所在目录加入 PATH）")

    command = [
        exe,
        "-h", str(MYSQL_CONFIG["host"]),
        "-P", str(MYSQL_CONFIG["port"]),
        "-u", str(MYSQL_CONFIG["user"]),
        "--password=%s" % MYSQL_CONFIG["password"],
        "--single-transaction",
        "--default-character-set=%s" % MYSQL_CONFIG.get("charset", "utf8mb4"),
        "--routines",
        "--triggers",
        "--events",
        "--hex-blob",
        "--databases", str(MYSQL_CONFIG["database"]),
    ]

    with open(target, "wb") as fp:
        result = subprocess.run(command, stdout=fp, stderr=subprocess.PIPE)

    if result.returncode != 0:

        detail = (result.stderr or b"").decode("utf-8", "ignore")

        raise RuntimeError(
            "mysqldump 退出码 %s：%s" % (result.returncode, detail[-300:])
        )

    if os.path.getsize(target) == 0:
        raise RuntimeError("mysqldump 输出为空文件")


def _cleanup_same_day(keep_path, now):
    """删掉当天的旧导出，返回被删掉的文件名列表"""

    day = now.strftime("%m%d")
    keep_path = os.path.abspath(keep_path)
    removed = []

    for name in os.listdir(SQL_DIR):

        matched = _DUMP_NAME_PATTERN.match(name)

        if not matched or matched.group(1) != day:
            continue

        path = os.path.join(SQL_DIR, name)

        if os.path.abspath(path) == keep_path:
            continue

        try:
            os.remove(path)
            removed.append(name)
        except OSError as e:
            _log("删除旧备份失败 %s：%s" % (name, e))

    return removed


def backup_now():
    """
    立刻导出一次（写成功后才删当天旧文件），返回最终文件名

    失败时抛异常，调用方决定如何记录。
    """

    global _last_dump_write_at

    os.makedirs(SQL_DIR, exist_ok=True)

    now = datetime.now()
    final_path = os.path.join(SQL_DIR, dump_file_name(now))

    # 先写进程独占的临时文件，成功后再原子改名：
    # 既避免导出到一半被当成有效备份，也避免多个进程同分钟导出互相覆盖
    tmp_path = "%s.%s.tmp" % (final_path, os.getpid())

    try:

        _run_mysqldump(tmp_path)
        os.replace(tmp_path, final_path)

    except Exception:

        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except OSError:
            pass

        raise

    removed = _cleanup_same_day(final_path, now)

    _last_dump_write_at = get_last_write_at()

    suffix = ""

    if removed:
        suffix = "，已清理旧文件 " + "、".join(removed)

    _log("已导出 %s（%.0f KB）%s" % (
        os.path.basename(final_path),
        os.path.getsize(final_path) / 1024,
        suffix,
    ))

    return os.path.basename(final_path)


# ============================================================
# 触发与线程
# ============================================================

def _maybe_backup():
    """空闲满阈值、且这期间确实有新改动时才导出"""

    last_write = get_last_write_at()

    # 本进程启动后还没改动过数据 → 没有可备份的新变化
    if last_write is None:
        return

    if time.time() - last_write < IDLE_SECONDS:
        return

    # 上次导出已经把这次改动包含进去了 → 不重复导出
    if _last_dump_write_at is not None and last_write <= _last_dump_write_at:
        return

    backup_now()


def _loop():
    while True:

        time.sleep(POLL_SECONDS)

        try:
            _maybe_backup()
        except Exception as e:
            _log("导出失败：%s" % e)


def start_auto_backup():
    """启动空闲自动备份线程（重复调用只生效一次）"""

    global _started

    with _start_lock:

        if _started:
            return False

        _started = True

    thread = threading.Thread(target=_loop, name="db-auto-backup", daemon=True)
    thread.start()

    return True
