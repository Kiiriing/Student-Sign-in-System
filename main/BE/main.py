# -*- coding: utf-8 -*-

import os
import sys
import time
import json
import logging
import threading
from datetime import datetime

# ============================================================
# Windows UTF-8 编码设置
# ============================================================

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


# ============================================================
# 日志目录
# ============================================================

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# 常驻日志句柄（跨天自动切换），由 _log_lock 保证多线程写入安全
_log_handle = None
_log_date = None
_log_lock = threading.Lock()


from flask import Flask, jsonify, request, g
from flask_cors import CORS
from flask_jwt_extended import JWTManager, verify_jwt_in_request

from api.auth import login_bp
from api.student import student_bp
from api.teacher import teacher_bp
from api.admin import admin_bp
from api.system import system_bp
from sync.api import sync_bp, sync_admin_bp
from sync.store import ensure_sync_tables, retire_outbox_for_snapshot_peers
from sync.worker import start_worker
from core.database import DBPoolBusyError, get_db
from core.backup import start_auto_backup

# ============================================================
# 请求日志工具函数
# ============================================================

def get_client_ip():
    """获取客户端真实 IP（处理反向代理）"""
    xff = request.headers.get("X-Forwarded-For")
    if xff:
        return xff.split(",")[0].strip()
    return request.remote_addr or "unknown"


def write_log(line: str):
    """
    追加写入当天日志文件

    不再每个请求 open/append/close 一次，而是全程复用一个常驻文件句柄：
    按天自动切换文件，写入用行缓冲（buffering=1）保证每条日志实时落盘。
    这样每个请求只多一次 write，不再有 open/close 的系统调用开销。
    """

    global _log_handle, _log_date

    today = datetime.now().strftime("%Y-%m-%d")

    try:
        with _log_lock:

            if _log_handle is None or _log_date != today:

                if _log_handle is not None:
                    try:
                        _log_handle.close()
                    except Exception:
                        pass

                _log_handle = open(
                    os.path.join(LOG_DIR, f"{today}.log"),
                    "a",
                    encoding="utf-8",
                    buffering=1
                )
                _log_date = today

            _log_handle.write(line + "\n")

    except Exception as e:
        # 日志写入失败不影响主流程
        print(f"[日志写入失败] {e}", file=sys.stderr)


# =========================================================
# 控制台颜色
# =========================================================
#
# 只作用于控制台那一条短日志，写文件的完整日志始终是无色纯文本
# （爬虫取证 / 事后分析要能直接读，转义序列会污染正文）。
#
# 染色范围是「整行」，规则：
#
#   INFO     白
#   WARN     黄
#   ERROR    红
#   STATUS=401  粉
#   CRAWLER  洋红
#
# 非交互式输出（重定向到文件、被作业系统捕获）不染色。

_ANSI_RESET = "\033[0m"

_C_WHITE = "\033[97m"
_C_YELLOW = "\033[33m"
_C_PINK = "\033[95m"
_C_RED = "\033[31m"
_C_MAGENTA = "\033[35m"


def _enable_windows_ansi():
    """Windows 控制台默认不解析 ANSI 转义序列，这里手动打开 VT 处理"""

    if os.name != "nt":
        return

    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)     # STD_OUTPUT_HANDLE
        mode = ctypes.c_ulong()

        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            # ENABLE_VIRTUAL_TERMINAL_PROCESSING
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)
    except Exception:
        pass


_COLOR_ENABLED = sys.stdout.isatty()

if _COLOR_ENABLED:
    _enable_windows_ansi()


def console_color(level: str, status: int) -> str:
    """
    按「级别 + 状态码」决定控制台整行的颜色

    返回 ANSI 前缀；未启用染色时返回空串。
    """

    if not _COLOR_ENABLED:
        return ""

    # 5xx 优先，避免被 CRAWLER 等标记抢走红色
    if status >= 500:
        return _C_RED

    if level == "CRAWLER":
        return _C_MAGENTA

    if status == 401:
        return _C_PINK

    if status >= 400:
        return _C_YELLOW

    return _C_WHITE


# =========================================================
# Flask 应用
# =========================================================

app = Flask(__name__)


# =========================================
# Flask 基础配置
# =========================================

app.config['JSON_AS_ASCII'] = False


# =========================================
# 收敛 werkzeug 自带访问日志
# =========================================
#
# werkzeug 默认会把每个请求打到 stderr，而本站已有自研请求日志
# （写 logs/YYYY-MM-DD.log，含耗时、用户、爬虫标记）。
# 两者同时开启等于每个请求写两次盘 / 两次 stdout，
# 高并发下这部分开销很可观。这里只保留 ERROR 以上级别。
#
# =========================================

logging.getLogger("werkzeug").setLevel(logging.ERROR)


# =========================================
# JWT 配置
# =========================================

# JWT 密钥
#
# 正式部署时建议修改成一个复杂随机字符串
#
app.config['JWT_SECRET_KEY'] = 'student-signin-jwt-secret-2026'


# JWT Token 有效时间
#
# 这里设置为 7 天
#
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 60 * 60 * 24 * 7


# =========================================
# 初始化 JWT
# =========================================

jwt = JWTManager(app)


# =========================================
# CORS 跨域
# =========================================
#
# 当前开发环境允许所有前端地址访问
#
# Vue + Vite 默认一般是：
#
# http://localhost:5173
#
# 后续正式部署时可以限制允许的域名
#
# =========================================

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": "*"
        }
    }
)


# ============================================================
# 请求日志中间件
# ============================================================
#
# 每个请求记录：时间、IP、方法、路径、状态码、耗时、用户身份、请求体
# 日志按天写入 BE/logs/YYYY-MM-DD.log
#
# ============================================================

# ============================================================
# 爬虫检测规则
# ============================================================
#
# 检测特征：
#   1. User-Agent 匹配常见爬虫关键字
#   2. User-Agent 为空或过短（非浏览器特征）
#   3. 缺少 Accept-Language / Accept 等 浏览器默认头
#   4. 短时间内大量请求同一接口（基于 IP + 路径的滑动窗口）
#
# 检测到爬虫后只在后台日志中标注，不影响请求处理
#
# ============================================================

import re
from collections import deque, defaultdict

# 常见爬虫关键字（User-Agent 中匹配到即视为爬虫）
CRAWLER_UA_PATTERNS = [
    r"python-requests",
    r"python-urllib",
    r"scrapy",
    r"curl",
    r"wget",
    r"postman",
    r"insomnia",
    r"httpclient",
    r"okhttp",
    r"java/",
    r"go-http-client",
    r"node-fetch",
    r"axios",
    r"bot",
    r"spider",
    r"crawler",
    r"scraper",
    r"headless",
    r"selenium",
    r"phantomjs",
    r"puppeteer",
    r"playwright",
    r"aiohttp",
    r"httpx",
    r"mechanize",
    r"googlehttpclient",
    r"webdriver",
]

CRAWLER_UA_REGEX = re.compile("|".join(CRAWLER_UA_PATTERNS), re.IGNORECASE)

# 浏览器必备请求头（缺失越多越可疑）
# 注意：Cache-Control / Sec-Fetch-* 并非所有浏览器 AJAX 请求都会带
# 只保留真正核心的头
BROWSER_CORE_HEADERS = [
    "Accept",
    "Accept-Language",
    "Accept-Encoding",
]

# 主流浏览器 UA 特征（命中其一即认为是浏览器，跳过头缺失检测）
BROWSER_UA_REGEX = re.compile(
    r"Mozilla|Chrome|Safari|Edge|Firefox|OPR|Opera|MSIE|Trident",
    re.IGNORECASE
)

# 高频请求检测：时间窗口（秒）和阈值
BURST_WINDOW_SECONDS = 10
BURST_THRESHOLD = 20

# 内存中的滑动窗口：{ (ip, path): deque([timestamp, ...]) }
_burst_window = defaultdict(deque)


# 请求体中的爬虫关键字（device_id / username / 备注 等字段值泄露爬虫特征）
CRAWLER_BODY_REGEX = re.compile(
    r"scraper|spider|crawler|scraper|selenium|puppeteer|playwright|"
    r"headless|phantomjs|mechanize|scrapy|aiohttp|httpx",
    re.IGNORECASE
)

# IP 级别爬虫会话追踪
#
# 检测到爬虫特征后，该 IP 的后续请求也标记为爬虫，
# 直到该 IP 通过一次正常登录（无爬虫特征）才清除标记
#
# 结构：{ ip: { "flag": "BODY:scraper", "time": 1234567890.0 } }
_crawler_sessions = {}
SESSION_TTL = 3600  # 会话标记保留时长（秒），超时自动清除

# 跨站同步接口前缀：这些接口供对端程序调用，不参与爬虫检测（见 detect_crawler）
SYNC_API_PREFIX = "/api/sync/"

# 请求日志里 body 的最大长度（超过则截断，避免大请求体把日志撑爆）
LOG_BODY_MAX = 500


def _gc_crawler_sessions():
    """清理过期的爬虫会话标记"""
    now = time.time()
    expired = [ip for ip, info in _crawler_sessions.items()
               if now - info["time"] > SESSION_TTL]
    for ip in expired:
        del _crawler_sessions[ip]


def _is_login_path(path: str) -> bool:
    """判断是否为登录接口"""
    return path == "/api/auth/login"


def detect_crawler(ip: str, path: str, ua: str, body: str = "", parsed=None) -> str:
    """
    爬虫检测

    parsed：请求体已解析出的 Python 对象（可选）。
            调用方（请求日志中间件）已经解析过一次请求体，
            这里直接复用，避免同一份 JSON 被重复 json.loads。

    返回值：
        ""         未检测到爬虫
        "UA:xxx"   命中 User-Agent 关键字
        "EMPTY-UA" User-Agent 为空或过短
        "FP:xxx"   前端浏览器指纹命中（client_fp 字段，如 webdriver/cdc-keys）
        "BODY:xxx" 请求体中泄露爬虫关键字（如 device_id="scraper-xxx"）
        "MISS-HEADERS" 缺少浏览器核心头（仅当 UA 不像浏览器时）
        "BURST"    短时高频请求
        "SESSION:xxx" 命中之前标记的爬虫会话（同 IP 后续请求）

    会话逻辑：
        1. 检测到爬虫特征 → 标记该 IP 为爬虫会话
        2. 该 IP 后续请求 → 直接返回 SESSION 标记
        3. 该 IP 再次登录且无爬虫特征 → 清除会话标记
    """

    # 跨站同步接口是给对端程序调用的（对方用 python-urllib，本来就不带
    # 浏览器请求头），爬虫检测对它没有意义，直接短路，避免对端每次调用
    # 都被打上 CRAWLER 标记、以及大报文走一遍关键字扫描。
    if path.startswith(SYNC_API_PREFIX):
        return ""

    _gc_crawler_sessions()
    now = time.time()
    is_login = _is_login_path(path)

    # ------------------------------------------------------------
    # 1. 本次请求的实时爬虫特征检测
    # ------------------------------------------------------------
    current_flag = ""

    # 1.1 User-Agent 关键字（爬虫库特征）
    if ua and CRAWLER_UA_REGEX.search(ua):
        current_flag = f"UA:{CRAWLER_UA_REGEX.search(ua).group(0).lower()}"

    # 1.2 User-Agent 为空或过短
    if not current_flag and (not ua or len(ua) < 20):
        current_flag = "EMPTY-UA"

    # 1.3 前端浏览器指纹命中（client_fp 字段）
    #
    # 前端 utils/fingerprint.ts 会检测 navigator.webdriver、
    # chromedriver 注入的 cdc_ 变量、headless WebGL renderer 等
    # HTTP 层无法伪造的自动化特征，命中后把 key 列表（逗号分隔）
    # 放到请求体 client_fp 字段。
    # 与 api/student.py 的 _is_script_signin_request() 检测思路保持一致，
    # 能抓到伪造了正常 UA 的 selenium。
    if not current_flag and body and body != "-":
        try:
            body_json = parsed if parsed is not None else json.loads(body)
            if isinstance(body_json, dict):
                client_fp = str(body_json.get("client_fp") or "").strip()
                if client_fp:
                    current_flag = f"FP:{client_fp}"
        except Exception:
            pass

    # 1.4 请求体爬虫关键字（device_id 等字段值泄露）
    if not current_flag and body and body != "-":
        m = CRAWLER_BODY_REGEX.search(body)
        if m:
            current_flag = f"BODY:{m.group(0).lower()}"

    # 1.5 缺少浏览器核心头（仅当 UA 不像浏览器时）
    if not current_flag and not BROWSER_UA_REGEX.search(ua):
        missing = [
            h for h in BROWSER_CORE_HEADERS
            if not request.headers.get(h)
        ]
        if len(missing) >= 2:
            current_flag = f"MISS-HEADERS({','.join(missing)})"

    # 1.6 短时高频请求（同一 IP + 路径）
    if not current_flag:
        key = (ip, path)
        window = _burst_window[key]
        window.append(now)
        while window and window[0] < now - BURST_WINDOW_SECONDS:
            window.popleft()
        if len(window) >= BURST_THRESHOLD:
            current_flag = f"BURST({len(window)}/{BURST_WINDOW_SECONDS}s)"

    # ------------------------------------------------------------
    # 2. 会话追踪
    # ------------------------------------------------------------
    if current_flag:
        # 命中爬虫特征 → 标记该 IP
        _crawler_sessions[ip] = {
            "flag": current_flag,
            "time": now
        }
        return current_flag

    # 没有命中爬虫特征，检查会话
    if ip in _crawler_sessions:
        # 登录接口且无爬虫特征 → 清除会话标记
        if is_login:
            del _crawler_sessions[ip]
            return ""
        # 非登录接口 → 沿用会话标记
        session_flag = _crawler_sessions[ip]["flag"]
        _crawler_sessions[ip]["time"] = now  # 续期
        return f"SESSION:{session_flag}"

    return ""


@app.before_request
def log_request_start():
    """记录请求开始时间"""
    g._start_time = time.time()


@app.after_request
def log_request_end(response):
    """请求结束后写入日志"""
    try:
        elapsed = int((time.time() - getattr(g, "_start_time", time.time())) * 1000)

        method = request.method
        path = request.path

        # 只记录 API 请求，忽略静态资源和 OPTIONS 预检
        #
        # 这个判断必须放在最前面：非 API 请求直接返回，
        # 连 JWT 解析、请求体解析、爬虫检测都省掉。
        if not path.startswith("/api") or method == "OPTIONS":
            return response

        # 获取当前用户身份
        #
        # 视图函数上的 @jwt_required() 已经把 Token 解码并校验过一次，
        # flask_jwt_extended 会把结果缓存在请求上下文 g._jwt_extended_jwt 上。
        # 这里直接复用这份结果，避免同一个 Token 在本请求里被解码/验签两次
        # （PyJWT 解码是当前最大的单请求 CPU 开销，重复一次等于白烧一半）。
        #
        # 只有「没走到视图」的请求（例如被 @jwt_required() 提前拦下的 401）
        # g 上才没有缓存，此时才补解一次。
        user_id = "-"
        try:
            claims = getattr(g, "_jwt_extended_jwt", None)

            if not claims:
                verify_jwt_in_request(optional=True)
                claims = getattr(g, "_jwt_extended_jwt", None)

            if claims:
                user_id = claims.get("sub") or "-"
        except Exception:
            pass

        ip = get_client_ip()
        ua = request.headers.get("User-Agent", "-")
        status = response.status_code

        # 截取请求体（仅记录文本，限制长度）
        #
        # 解析结果 parsed_body 会一并交给 detect_crawler 复用，
        # 避免同一份 JSON 被 json.loads 解析两次。
        body = "-"
        parsed_body = None
        if method in ("POST", "PUT", "PATCH"):

            # 快照入账的请求体是整库 JSON（几十到几百 KB），
            # 解析和落日志都没有意义，直接跳过
            if path == "/api/sync/import":
                body = "-"
            else:
                try:
                    raw = request.get_data(as_text=True)
                    if raw:
                        # 尝试解析为 JSON 重新序列化，避免含敏感信息原文
                        try:
                            data = json.loads(raw)
                            parsed_body = data
                            # 脱敏密码字段
                            if isinstance(data, dict):
                                masked = dict(data)
                                for k in list(masked.keys()):
                                    if "password" in k.lower() or "pwd" in k.lower():
                                        masked[k] = "***"
                                body = json.dumps(masked, ensure_ascii=False)
                            else:
                                body = raw
                        except Exception:
                            body = raw
                except Exception:
                    body = "-"

            # 统一截断，避免大请求体把日志撑爆
            if len(body) > LOG_BODY_MAX:
                body = body[:LOG_BODY_MAX] + "...(截断)"

        # 状态级别标记
        level = "INFO"
        if status >= 500:
            level = "ERROR"
        elif status >= 400:
            level = "WARN"

        # 爬虫检测：命中则在日志中标注，不影响请求处理
        crawler_flag = detect_crawler(ip, path, ua, body, parsed_body)
        crawler_tag = f" CRAWLER={crawler_flag}" if crawler_flag else ""
        if crawler_flag:
            level = "CRAWLER"

        log_line = (
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
            f"[{level}] "
            f"IP={ip} "
            f"USER={user_id} "
            f"{method} {path} "
            f"STATUS={status} "
            f"TIME={elapsed}ms "
            f"UA={ua[:120]} "
            f"BODY={body}"
            f"{crawler_tag}"
        )

        write_log(log_line)

        # 控制台短行
        #
        # 与写文件的完整行是刻意分离的两种格式：
        #   文件：完整字段（USER / UA / BODY / CRAWLER），爬虫取证和事后分析需要
        #   控制台：只留时间、级别、IP、方法、路径、状态码、耗时，方便开发时快速扫读
        #
        print(
            f"{console_color(level, status)}"
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
            f"[{level}] "
            f"{ip} {method} {path} "
            f"STATUS={status} "
            f"TIME={elapsed}ms"
            f"{_ANSI_RESET if _COLOR_ENABLED else ''}",
            flush=True
        )

    except Exception as e:
        # 日志记录失败不影响响应
        print(f"[日志记录异常] {e}", file=sys.stderr)

    return response

# =========================================
# 全局 JWT 错误处理
# =========================================

@jwt.unauthorized_loader
def unauthorized_callback(error):
    """
    请求没有携带 JWT Token
    """

    return jsonify({
        "code": 401,
        "message": "未登录或缺少访问令牌"
    }), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    """
    JWT Token 无效
    """

    return jsonify({
        "code": 401,
        "message": "登录令牌无效"
    }), 401


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    """
    JWT Token 已过期
    """

    return jsonify({
        "code": 401,
        "message": "登录已过期，请重新登录"
    }), 401


# =========================================
# 注册 Blueprint
# =========================================

# -----------------------------------------
# 登录模块
# -----------------------------------------
#
# api/auth.py
#
# /api/auth/login
#
# -----------------------------------------

app.register_blueprint(login_bp)


# -----------------------------------------
# 学生模块
# -----------------------------------------
#
# api/student.py
#
# /api/student/...
#
# -----------------------------------------

app.register_blueprint(student_bp)


# -----------------------------------------
# 教师模块
# -----------------------------------------
#
# api/teacher.py
#
# /api/teacher/...
#
# -----------------------------------------

app.register_blueprint(teacher_bp)


# -----------------------------------------
# 管理员模块
# -----------------------------------------
#
# api/admin.py
#
# /api/admin/...
#
# -----------------------------------------

app.register_blueprint(admin_bp)


# -----------------------------------------
# 系统公共模块
# -----------------------------------------
#
# api/system.py
#
# /api/system/...
#
# -----------------------------------------

app.register_blueprint(system_bp)


# -----------------------------------------
# 跨站同步模块
# -----------------------------------------
#
# sync/api.py
#
# /api/sync/...        对端接口（X-Sync-Token 鉴权）
# /api/admin/sync/...  管理接口（JWT）
#
# -----------------------------------------

app.register_blueprint(sync_bp)

app.register_blueprint(sync_admin_bp)


# =========================================
# 跨站同步初始化
# =========================================
#
# 1. 幂等建 4 张同步表
# 2. 启动后台同步线程（推送 / 拉取 / 对账）
#
# 同步能力属于增强项，初始化失败不能影响本站正常签到，
# 因此这里都用 try/except 兜住，只打印告警。
#
# =========================================

try:

    ensure_sync_tables()
    print("[跨站同步] 同步表已就绪")

    # 目标站点切成快照式协议后，它名下按契约式入队的历史待发行发不出去，
    # 启动时一次性转成失败态，避免每轮同步白试（幂等，没有待发行时返回 0）
    retired = retire_outbox_for_snapshot_peers()

    if retired:
        print("[跨站同步] 已退役 %s 条指向快照式对端的待发行" % retired)

except Exception as e:

    print("[跨站同步] 建表失败，跨站同步将不可用：%s" % e)


try:

    if start_worker():
        print("[跨站同步] 后台同步线程已启动（按需触发，无定时轮询）")

except Exception as e:

    print("[跨站同步] 后台线程启动失败，跨站同步将不可用：%s" % e)


# =========================================
# 数据库空闲自动备份
# =========================================
#
# 改造详见 core/backup.py：
#
#   距最后一次数据改动满 30 分钟后，自动把整库导出到 main/sql，
#   文件名 student_signin{MMDD}_{HHMM}.sql，每天只保留一份。
#
# 备份不是核心链路，启动失败不能影响正常签到，因此同样兜住异常。
#
# =========================================

try:

    if start_auto_backup():
        print("[自动备份] 空闲自动备份线程已启动（改动数据后空闲满 30 分钟导出一次）")

except Exception as e:

    print("[自动备份] 线程启动失败，自动备份将不可用：%s" % e)


# =========================================
# 系统测试接口
# =========================================

@app.route("/", methods=["GET"])
def index():
    """
    判断 Flask 后端是否正常运行
    """

    return jsonify({
        "code": 200,
        "message": "学生签到系统后端运行正常",
        "service": "student-signin-backend"
    })


# =========================================
# MySQL 连接测试接口
# =========================================

@app.route("/api/test/mysql", methods=["GET"])
def test_mysql():
    """
    测试 MySQL 是否能够正常连接。

    浏览器访问：

    http://127.0.0.1:5000/api/test/mysql
    """

    db = None
    cursor = None

    try:

        # 创建数据库连接
        db = get_db()

        # 创建游标
        cursor = db.cursor()

        # 查询数据库当前时间
        # 注意：current_time 是 MySQL 保留字，直接当别名会导致语法错误
        cursor.execute("SELECT NOW() AS now_time")

        result = cursor.fetchone()

        return jsonify({
            "code": 200,
            "message": "MySQL 连接成功",
            "data": result
        })

    except Exception as e:

        return jsonify({
            "code": 500,
            "message": "MySQL 连接失败",
            "error": str(e)
        }), 500

    finally:

        # 关闭游标
        if cursor:
            cursor.close()

        # 关闭数据库连接
        if db:
            db.close()


# =========================================
# 503 处理：数据库连接池排队超时
# =========================================

@app.errorhandler(DBPoolBusyError)
def db_pool_busy(error):
    """
    连接池排队超时 → 503（服务暂不可用），而不是 500（服务器内部错误）

    说明：视图函数若自行用 `except Exception` 兜住了异常，
    这个处理器不会生效（那种情况仍返回 500）。
    """

    return jsonify({
        "code": 503,
        "message": "服务繁忙，请稍后重试"
    }), 503


# =========================================
# 404 处理
# =========================================

@app.errorhandler(404)
def not_found(error):

    return jsonify({
        "code": 404,
        "message": "请求接口不存在"
    }), 404


# =========================================
# 500 错误处理
# =========================================

@app.errorhandler(500)
def internal_error(error):

    return jsonify({
        "code": 500,
        "message": "服务器内部错误"
    }), 500


# =========================================
# 启动 Flask
# =========================================

if __name__ == "__main__":

    print("=" * 60)
    print("学生签到系统后端")
    print("=" * 60)
    print("服务地址：http://127.0.0.1:5000")
    print("MySQL：127.0.0.1:3306")
    print("数据库：student_signin")
    print("=" * 60)

    app.run(
        host="0.0.0.0",
        port=5000,
        threaded=True,
        debug=True
    )
