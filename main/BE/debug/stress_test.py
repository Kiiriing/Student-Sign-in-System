# -*- coding: utf-8 -*-
"""
接口压力测试工具（仅用于测试本系统后端的最大承受压力）

功能：
    1. 固定并发压测：模拟 N 个并发用户循环发请求，输出 QPS、延迟分位、错误率
    2. 阶梯加压压测：并发用户数逐级翻倍，自动找出接口性能拐点（错误率/延迟突增点）
    3. 自动登录获取 JWT，后续请求自动携带 Authorization
    4. 支持 GET / POST / PUT，可自定义请求体

依赖：
    仅使用 Python 标准库，Python 3.8+ 即可运行

用法示例：
    # 1) 固定并发：50 个并发用户，共 2000 个请求，打 /api/student/records
    python stress_test.py --target records -c 50 -n 2000

    # 2) 阶梯加压（默认 5 -> 10 -> 20 -> 50 -> 100 -> 200 -> 400）
    python stress_test.py --target records --step

    # 3) 模拟真实用户：每个用户请求之间停 300ms（更像人在点页面）
    python stress_test.py --target records -c 50 -n 2000 --think 300

    # 4) 对照实验：关掉连接复用，回到"每次请求新建 TCP"的旧行为
    python stress_test.py --target records -c 50 -n 2000 --no-keep-alive

    # 5) 压测登录接口（无需 token）
    python stress_test.py --target login -c 10 -n 200

    # 6) 完全自定义目标
    python stress_test.py --method GET --path /api/student/courses -c 10 -n 200

真实性说明（与旧版的关键差异，都是为了"测出后端能力"而不是"测出压测机能力"）：
    1. 连接复用：浏览器 / Axios 走 HTTP/1.1 keep-alive 复用 TCP 连接，
       旧版每个请求都新建 TCP，测出来的是"短连接洪水"。本版默认复用。
    2. 真实请求头：带浏览器 User-Agent 与 Accept / Accept-Language / Referer / Origin，
       与后端 detect_crawler() 中"正常用户"的判定路径一致。
       旧版 UA 只有 14 个字符（StressTest/1.0），会被判为 EMPTY-UA 爬虫，
       走的是后端另一条分支，测的并不是真实用户路径。
    3. 并发语义：-c 是"并发用户数"，每人独占一条连接循环发请求。
       旧版是一次性提交 total 个任务给线程池，total 越大调度开销越大。
       注意 2000 个并发用户是不现实的（一个班也就几十人同时签到）——
       并发开太高时先饱和的是压测机本身。
    4. 统计不抢锁：延迟数据在各自线程内记录，压测结束后合并。
       旧版每个请求都要在全局锁里 append + 记状态码，高并发下锁竞争本身
       就吃掉了可观的时间。
    5. 预热 + 客户端自检：正式统计前先打一轮预热请求（不计入结果）；
       同时统计压测进程自身的 CPU 占用，客户端先跑满时会明确告诉你
       这组 QPS 不可信。

注意：
    - 写接口（如签到 POST /api/student/signin）会真实写入数据库，谨慎使用
    - 默认目标地址为本机 http://127.0.0.1:5000
    - 对非本机地址压测前会要求二次确认
"""

import argparse
import gzip
import http.client
import json
import ssl
import statistics
import sys
import threading
import time
import urllib.parse
from datetime import datetime

# Windows UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


# ============================================================
# 默认配置（可被命令行参数覆盖）
# ============================================================

DEFAULT_BASE_URL = "http://127.0.0.1:5000"

# 前端地址：用于构造 Origin / Referer（前后端分离时浏览器跨域请求会带这两个头）
DEFAULT_ORIGIN = "http://127.0.0.1:5173"

# 压测用账号（学生账号）
LOGIN_USERNAME = "253201323"
LOGIN_PASSWORD = "123456"

# 教师账号（压测教师端接口时使用，按需修改）
TEACHER_USERNAME = "tea"
TEACHER_PASSWORD = "123456"

# ============================================================
# 压测规模（直接修改这两个变量即可，命令行 -c / -n 可临时覆盖）
# ============================================================
# 并发用户数：同时有多少个用户在自己的连接上循环发请求
#
# 注意这是"用户数"，不是"线程数上限"。
# 真实场景是一个班几十人同时签到，50~200 已经远超实际负载；
# 再往上加，先饱和的是压测机自己，测不出后端上限。
CONCURRENCY = 50

# 总请求数：本次压测总共发送多少个请求
TOTAL_REQUESTS = 5000

# 阶梯加压配置：(并发用户数, 每级请求数)
STEP_LEVELS = [5, 10, 20, 50, 100, 200, 400]
REQUESTS_PER_LEVEL = 200
# 错误率超过该阈值时自动停止继续加压
STOP_ERROR_RATE = 0.5

# 请求超时（秒）
REQUEST_TIMEOUT = 15

# 正式统计前的预热请求数（每档预热，不计入结果）
# 至少会保证每个并发用户各打 1 个请求，把连接建立起来
WARMUP_REQUESTS = 50

# 模拟浏览器 / Axios 的请求头
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
}


# ============================================================
# 预置接口目标
# ============================================================
# 说明：
#   need_login=True 时先登录拿 JWT
#   body 为 None 表示不带请求体；写接口请通过 --body 自行传入
# ============================================================

TARGETS = {
    # ---- 免登录 ----
    "login": {
        "method": "POST",
        "path": "/api/auth/login",
        "need_login": False,
        # 压测登录接口时每个请求都用这份 body
        #
        # device_id=None 表示"每个模拟用户各自生成独立设备号"：
        # 真实场景里不同学生用的是不同手机。如果所有并发用户共用一个
        # device_id，会被后端的"每台设备每天只能登录一个学生账号"规则拦下，
        # 测出来的就不是登录接口本身的性能了。
        "body": {
            "username": LOGIN_USERNAME,
            "password": LOGIN_PASSWORD,
            "device_id": None
        },
        "desc": "登录接口（POST，含数据库查询+密码校验）"
    },

    # ---- 学生端 ----
    "courses": {
        "method": "GET",
        "path": "/api/student/courses",
        "need_login": True,
        "as_teacher": False,
        "body": None,
        "desc": "学生-今日课程（GET）"
    },
    "records": {
        "method": "GET",
        "path": "/api/student/records",
        "need_login": True,
        "as_teacher": False,
        "body": None,
        "desc": "学生-签到记录（GET，典型读接口）"
    },
    "class-attendance": {
        "method": "GET",
        "path": "/api/student/class-attendance",
        "need_login": True,
        "as_teacher": False,
        "body": None,
        "desc": "学生-班级考勤（GET）"
    },
    # 写接口：会真实产生签到记录，默认不提供 task_id，避免误写
    "signin": {
        "method": "POST",
        "path": "/api/student/signin",
        "need_login": True,
        "as_teacher": False,
        "body": None,  # 需通过 --body '{"task_id":"xxx"}' 指定
        "desc": "学生-签到（POST，写接口，会写入数据库！）"
    },

    # ---- 教师端 ----
    "teacher-courses": {
        "method": "GET",
        "path": "/api/teacher/courses",
        "need_login": True,
        "as_teacher": True,
        "body": None,
        "desc": "教师-课程列表（GET）"
    },
    "tasks": {
        "method": "GET",
        "path": "/api/teacher/tasks",
        "need_login": True,
        "as_teacher": True,
        "body": None,
        "desc": "教师-签到任务列表（GET）"
    },
    "roster": {
        "method": "GET",
        "path": "/api/teacher/attendance/roster",
        "need_login": True,
        "as_teacher": True,
        # 按需通过 --query task_id=xxx 指定
        "body": None,
        "desc": "教师-签到名册（GET，重查询）"
    },
    "statistics": {
        "method": "GET",
        "path": "/api/teacher/statistics",
        "need_login": True,
        "as_teacher": True,
        "body": None,
        "desc": "教师-统计分析（GET，聚合查询）"
    },
}


# ============================================================
# 工具函数
# ============================================================

def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")


def build_url(base_url: str, path: str, query: str = "") -> str:
    url = base_url.rstrip("/") + path
    if query:
        url += ("&" if "?" in url else "?") + query.lstrip("?")
    return url


def split_base_url(base_url: str):
    """把 http://host:port 拆成 (scheme, host, port)"""
    parsed = urllib.parse.urlsplit(base_url)
    scheme = parsed.scheme or "http"
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or (443 if scheme == "https" else 80)
    return scheme, host, port


def build_user_bodies(body, concurrency):
    """给每个并发用户准备一份请求体

    body 里的 device_id 为 None 时，按用户序号生成独立设备号。
    否则所有用户共用一个 device_id，会被后端"每台设备每天只能登录一个
    学生账号"的规则挡掉（并发下还会因为唯一索引冲突报 500），
    测出来的就不是接口真实的处理能力了。
    """
    if not isinstance(body, dict) or body.get("device_id") is not None:
        return [body] * concurrency

    bodies = []
    for i in range(concurrency):
        one = dict(body)
        one["device_id"] = f"stress-device-{i}"
        bodies.append(one)
    return bodies


def percentile(sorted_data, p):
    """计算分位数 p: 0~100"""
    if not sorted_data:
        return 0.0
    k = (len(sorted_data) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(sorted_data) - 1)
    if f == c:
        return sorted_data[f]
    return sorted_data[f] + (sorted_data[c] - sorted_data[f]) * (k - f)


# ============================================================
# 模拟用户：一个用户独占一条（默认复用的）连接
# ============================================================

class HttpClient:
    """模拟一个浏览器用户

    默认复用 TCP 连接（keep-alive），与浏览器 / Axios 的行为一致；
    keep_alive=False 时每个请求都新建连接（旧版行为，用于对照实验）。
    """

    def __init__(self, scheme, host, port, origin, keep_alive=True):
        self.scheme = scheme
        self.host = host
        self.port = port
        self.origin = origin
        self.keep_alive = keep_alive
        self._conn = None
        # 实际新建过多少条 TCP 连接（用来确认连接是否真的被复用）
        self.connects = 0

    def _new_conn(self):
        self.connects += 1
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            return http.client.HTTPSConnection(
                self.host, self.port, timeout=REQUEST_TIMEOUT, context=ctx
            )
        return http.client.HTTPConnection(self.host, self.port, timeout=REQUEST_TIMEOUT)

    def close(self):
        if self._conn is not None:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None

    def request(self, method, path, token="", body=None):
        """
        发一个请求

        返回: (status_code, latency_seconds, error_str, payload_bytes)
        没有响应时 status 为 0
        """
        headers = dict(BROWSER_HEADERS)
        headers["Origin"] = self.origin
        headers["Referer"] = self.origin + "/"

        data = None
        if body is not None:
            data = json.dumps(body, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"
        if token:
            headers["Authorization"] = f"Bearer {token}"

        # 短连接模式：用完就断，下一个请求重新建连
        if not self.keep_alive:
            self.close()

        if self._conn is None:
            self._conn = self._new_conn()

        start = time.perf_counter()
        try:
            self._conn.request(method, path, body=data, headers=headers)
            resp = self._conn.getresponse()
            payload = resp.read()   # 必须读完，连接才能继续复用
            latency = time.perf_counter() - start
            if not self.keep_alive:
                self.close()
            return resp.status, latency, "", payload
        except Exception as e:
            # 连接可能已被服务端关掉（超时/重启），销毁掉，下个请求会自动重建
            self.close()
            latency = time.perf_counter() - start
            return 0, latency, f"{type(e).__name__}: {e}", b""


def login(base_url: str, username: str, password: str, origin: str = DEFAULT_ORIGIN) -> str:
    """登录并返回 access_token（只发一次请求，复用连接）"""
    scheme, host, port = split_base_url(base_url)
    client = HttpClient(scheme, host, port, origin, keep_alive=True)

    body = {
        "username": username,
        "password": password,
        "device_id": f"stress-{int(time.time())}"
    }
    status, latency, err, payload = client.request("POST", "/api/auth/login", body=body)
    client.close()

    if status != 200:
        raise RuntimeError(f"登录失败: status={status} {err} (耗时 {latency:.3f}s)")

    # 万一后端后续加了 gzip 压缩中间件
    if payload[:2] == b"\x1f\x8b":
        payload = gzip.decompress(payload)

    parsed = json.loads(payload.decode("utf-8"))

    # 兼容两种返回结构：{code,data:{access_token}} 或 {access_token}
    data = parsed.get("data", parsed)
    token = data.get("access_token") or data.get("token")
    if not token:
        raise ValueError(
            f"登录响应中未找到 token: {json.dumps(parsed, ensure_ascii=False)[:300]}"
        )
    return token


# ============================================================
# 压测核心
# ============================================================

class StageResult:
    """一次压测的统计结果

    延迟数据由各线程本地收集、结束后合并，
    避免旧版"每个请求都抢一把全局锁"带来的额外开销。
    """

    def __init__(self):
        self.latencies = []
        self.status_count = {}
        self.errors = []
        self.total = 0
        self.success = 0
        self.fail = 0
        self.new_connections = 0   # 统计期间新建的 TCP 连接数
        self.cpu_seconds = 0.0     # 压测进程自身消耗的 CPU 时间
        self.start_at = 0.0
        self.end_at = 0.0

    def merge(self, local_results):
        """合并各线程的本地统计"""
        for latencies, status_count, errors in local_results:
            if latencies is None:
                continue
            self.latencies.extend(latencies)
            for key, cnt in status_count.items():
                self.status_count[key] = self.status_count.get(key, 0) + cnt
            if len(self.errors) < 10:
                self.errors.extend(errors[: 10 - len(self.errors)])
            self.total += len(latencies)

        for key, cnt in self.status_count.items():
            if key.startswith("2"):
                self.success += cnt
        self.fail = self.total - self.success


def _drive(clients, method, path, token, bodies, counts, think_ms, stage_name):
    """
    让每个客户端按分配到的请求数循环发请求

    bodies : 与 clients 一一对应的请求体
    counts : 每个客户端要发的请求数（预先切分，压测过程中无需抢任务队列）
    返回: 每个线程的本地统计 [(latencies, status_count, errors), ...]
    """
    total = sum(counts)
    step = max(total // 10, 1)
    progress_lock = threading.Lock()
    done = [0]
    local_results = [None] * len(clients)

    def worker(idx, client, count):
        latencies = []
        status_count = {}
        errors = []
        for _ in range(count):
            status, latency, err, _payload = client.request(
                method, path, token=token, body=bodies[idx]
            )
            latencies.append(latency)
            key = str(status) if status else "NO_RESPONSE"
            status_count[key] = status_count.get(key, 0) + 1
            if not (200 <= status < 300) and len(errors) < 3:
                errors.append(err or key)

            if think_ms:
                time.sleep(think_ms / 1000.0)

            # 进度只在计数时抢锁（一次整数自增），成本可忽略
            with progress_lock:
                done[0] += 1
                n = done[0]
            if n % step == 0 or n == total:
                print(f"\r    {stage_name} 进度: {n}/{total} ({n * 100 // total}%)",
                      end="", flush=True)

        local_results[idx] = (latencies, status_count, errors)

    threads = [
        threading.Thread(target=worker, args=(i, c, n), daemon=True)
        for i, (c, n) in enumerate(zip(clients, counts))
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print()
    return local_results


def run_stage(base_url, method, path, query, token, body,
              concurrency, total, stage_name="",
              warmup=WARMUP_REQUESTS, think_ms=0,
              keep_alive=True, origin=DEFAULT_ORIGIN):
    """
    跑一级压测

    concurrency: 并发用户数（每人一条连接）
    total      : 总请求数
    warmup     : 预热请求数（不计入统计）
    think_ms   : 每个请求后的思考时间（毫秒）
    """
    url_path = path
    if query:
        url_path += ("&" if "?" in url_path else "?") + query.lstrip("?")

    scheme, host, port = split_base_url(base_url)

    # 并发用户不能多于总请求数
    concurrency = max(1, min(concurrency, total))
    base, extra = divmod(total, concurrency)
    counts = [base + (1 if i < extra else 0) for i in range(concurrency)]

    clients = [HttpClient(scheme, host, port, origin, keep_alive)
               for _ in range(concurrency)]
    bodies = build_user_bodies(body, concurrency)

    # ---------- 预热：把连接、连接池、缓存都拉起来 ----------
    if warmup > 0:
        w_total = max(warmup, concurrency)   # 保证每个用户至少打 1 个请求
        w_base, w_extra = divmod(w_total, concurrency)
        w_counts = [w_base + (1 if i < w_extra else 0) for i in range(concurrency)]
        _drive(clients, method, url_path, token, bodies, w_counts, 0, "[预热]")

    # ---------- 正式统计 ----------
    result = StageResult()
    connects_before = sum(c.connects for c in clients)

    result.start_at = time.perf_counter()
    cpu_before = time.process_time()
    local_results = _drive(clients, method, url_path, token, bodies,
                           counts, think_ms, stage_name)
    result.cpu_seconds = time.process_time() - cpu_before
    result.end_at = time.perf_counter()

    result.new_connections = sum(c.connects for c in clients) - connects_before
    result.merge(local_results)

    for c in clients:
        c.close()

    return result


def print_stage_report(concurrency, result: StageResult, keep_alive=True):
    wall = result.end_at - result.start_at
    qps = result.total / wall if wall > 0 else 0
    lat = sorted(result.latencies)
    avg = statistics.fmean(lat) if lat else 0
    err_rate = result.fail / result.total if result.total else 0
    cpu_ratio = result.cpu_seconds / wall if wall > 0 else 0

    print(f"  并发用户数     : {concurrency}")
    print(f"  总请求 / 成功 / 失败 : {result.total} / {result.success} / {result.fail}")
    print(f"  错误率         : {err_rate * 100:.2f}%")
    print(f"  实际 QPS       : {qps:.1f} req/s   (耗时 {wall:.2f}s)")

    if lat:
        print(f"  延迟(ms)       : avg={avg * 1000:.1f}  "
              f"p50={percentile(lat, 50) * 1000:.1f}  "
              f"p90={percentile(lat, 90) * 1000:.1f}  "
              f"p95={percentile(lat, 95) * 1000:.1f}  "
              f"p99={percentile(lat, 99) * 1000:.1f}  "
              f"max={lat[-1] * 1000:.1f}")
    else:
        print("  延迟(ms)       : 无数据")

    print(f"  状态码分布     : {json.dumps(dict(sorted(result.status_count.items())), ensure_ascii=False)}")
    print(f"  连接复用       : 新建 TCP {result.new_connections} 条 / {result.total} 个请求"
          + ("（短连接模式）" if not keep_alive else ""))

    if result.total:
        print(f"  客户端开销     : CPU {result.cpu_seconds:.2f}s（占墙钟 {cpu_ratio * 100:.0f}%），"
              f"每请求 {result.cpu_seconds / result.total * 1000:.2f}ms")

    if result.errors:
        uniq = {}
        for e in result.errors:
            uniq[e] = uniq.get(e, 0) + 1
        print(f"  错误样本       : {json.dumps(uniq, ensure_ascii=False)}")

    # ---------------- 数据可信度 ----------------
    notes = []
    if cpu_ratio > 0.85:
        notes.append("压测客户端 CPU 已打满，这个 QPS 反映的是压测机而不是后端上限，"
                     "请降低并发或换一台机器施压")
    if not keep_alive:
        notes.append("短连接模式（--no-keep-alive），每次请求都新建 TCP，不代表浏览器真实行为")
    elif result.new_connections >= result.total and result.total > 0:
        notes.append("连接没有被复用（服务端可能主动关闭了连接）")

    print("  数据可信度     : " + ("⚠ " + "；".join(notes) if notes
                                   else "OK（连接复用正常、客户端未饱和）"))
    return qps, err_rate, avg


# ============================================================
# 主流程
# ============================================================

def confirm_non_localhost(base_url: str):
    if "127.0.0.1" in base_url or "localhost" in base_url:
        return
    print()
    print("!" * 60)
    print(f"  警告：目标不是本机地址：{base_url}")
    print("  压测会对该服务器产生较大负载，请确认你已获得授权！")
    print("!" * 60)
    ans = input("  确认继续？输入 yes 回车：").strip().lower()
    if ans != "yes":
        log("已取消")
        sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        description="接口压力测试工具（仅限测试本系统）",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help=f"后端地址，默认 {DEFAULT_BASE_URL}")
    parser.add_argument("--origin", default=DEFAULT_ORIGIN,
                        help=f"模拟前端地址，用于构造 Origin/Referer，默认 {DEFAULT_ORIGIN}")
    parser.add_argument("--target", choices=sorted(TARGETS.keys()), default="records",
                        help="预置接口目标名（见脚本顶部 TARGETS），默认 records")
    parser.add_argument("--method", default="GET", choices=["GET", "POST", "PUT"], help="自定义请求方法")
    parser.add_argument("--path", help="自定义请求路径，如 /api/student/records")
    parser.add_argument("--query", default="", help="QueryString，如 task_id=abc&status=1")
    parser.add_argument("--body", default="", help='JSON 请求体，如 \'{"task_id":"xxx"}\'')
    parser.add_argument("-c", "--concurrency", type=int, default=CONCURRENCY,
                        help=f"并发用户数（每人一条连接），默认 {CONCURRENCY}")
    parser.add_argument("-n", "--total", type=int, default=TOTAL_REQUESTS,
                        help=f"总请求数，默认 {TOTAL_REQUESTS}")
    parser.add_argument("--warmup", type=int, default=WARMUP_REQUESTS,
                        help=f"预热请求数（不计入统计），默认 {WARMUP_REQUESTS}")
    parser.add_argument("--think", type=int, default=0, metavar="MS",
                        help="每个请求后的思考时间（毫秒），模拟真实用户操作间隔，默认 0")
    parser.add_argument("--no-keep-alive", action="store_true",
                        help="关闭连接复用（旧版行为：每个请求新建 TCP，用于对照）")
    parser.add_argument("--step", action="store_true", help="阶梯加压模式，自动寻找性能拐点")
    parser.add_argument("--teacher", action="store_true", help="使用教师账号登录")
    parser.add_argument("--token", default="", help="直接指定 JWT，跳过登录")
    args = parser.parse_args()

    # 解析目标
    if args.target:
        t = TARGETS[args.target]
        method, path = t["method"], t["path"]
        need_login = t["need_login"]
        body = t.get("body")
        use_teacher = bool(t.get("as_teacher"))
        desc = t["desc"]
    elif args.path:
        method, path = args.method, args.path
        need_login = True
        body = None
        use_teacher = args.teacher
        desc = "自定义目标"
    else:
        parser.error("请用 --target 指定预置接口，或用 --path 自定义路径")

    if args.body:
        try:
            body = json.loads(args.body)
        except json.JSONDecodeError as e:
            parser.error(f"--body 不是合法 JSON: {e}")

    base_url = args.base_url.rstrip("/")
    confirm_non_localhost(base_url)

    keep_alive = not args.no_keep_alive

    print("=" * 64)
    print(" 接口压力测试")
    print("=" * 64)
    log(f"目标接口   : {method} {build_url(base_url, path, args.query)}")
    log(f"接口说明   : {desc}")
    if body is not None:
        log(f"请求体     : {json.dumps(body, ensure_ascii=False)}")
    log(f"模拟方式   : {'连接复用(keep-alive)' if keep_alive else '短连接(每请求新建TCP)'}"
        f" / 浏览器请求头 / 预热 {args.warmup} 个请求"
        + (f" / 思考时间 {args.think}ms" if args.think else ""))
    if method in ("POST", "PUT") and args.target == "signin":
        log("⚠ 注意：该接口为写接口，会真实写入数据库！")
        ans = input("  确认继续？输入 yes 回车：").strip().lower()
        if ans != "yes":
            log("已取消")
            return

    if args.concurrency > 200:
        log(f"提示：并发用户数 {args.concurrency} 偏高。真实场景一个班也就几十人同时签到，"
            f"并发开太高时先饱和的是压测机本身，结果里会给出客户端 CPU 占用用于判断。")

    # 获取 token
    token = args.token
    if need_login and not token:
        uname = TEACHER_USERNAME if use_teacher else LOGIN_USERNAME
        pwd = TEACHER_PASSWORD if use_teacher else LOGIN_PASSWORD
        log(f"正在登录获取 token（账号 {uname}）...")
        token = login(base_url, uname, pwd, origin=args.origin)
        log(f"登录成功，token 前 20 字符: {token[:20]}...")

    # ---------------- 固定并发压测 ----------------
    if not args.step:
        print()
        log(f"开始固定并发压测：{args.concurrency} 并发用户 / 共 {args.total} 请求")
        t0 = time.time()
        result = run_stage(base_url, method, path, args.query, token, body,
                           args.concurrency, args.total, stage_name="[固定压测]",
                           warmup=args.warmup, think_ms=args.think,
                           keep_alive=keep_alive, origin=args.origin)
        print()
        print("-" * 64)
        print(" 压测结果")
        print("-" * 64)
        print_stage_report(args.concurrency, result, keep_alive=keep_alive)
        print("=" * 64)
        log(f"总耗时 {time.time() - t0:.2f}s")
        return

    # ---------------- 阶梯加压压测 ----------------
    print()
    log("开始阶梯加压，自动寻找性能拐点")
    print(f"{'并发':>6} | {'QPS':>8} | {'错误率':>7} | {'avg(ms)':>8} | {'p95(ms)':>8} | 结论")
    print("-" * 72)

    best_qps = 0.0
    break_point = None
    for c in STEP_LEVELS:
        result = run_stage(base_url, method, path, args.query, token, body,
                           c, REQUESTS_PER_LEVEL, stage_name=f"[并发 {c}]",
                           warmup=args.warmup, think_ms=args.think,
                           keep_alive=keep_alive, origin=args.origin)
        qps, err_rate, avg = print_stage_report(c, result, keep_alive=keep_alive)
        lat = sorted(result.latencies)
        p95 = percentile(lat, 95) * 1000

        verdict = "OK"
        if err_rate >= STOP_ERROR_RATE:
            verdict = "✗ 错误率过高，停止加压"
            if break_point is None:
                break_point = c
        elif p95 > 1000:
            verdict = "△ p95 延迟 > 1s"
        if qps > best_qps:
            best_qps = qps

        print(f"{c:>6} | {qps:>8.1f} | {err_rate * 100:>6.2f}% | {avg * 1000:>8.1f} | {p95:>8.1f} | {verdict}")
        print()

        if err_rate >= STOP_ERROR_RATE:
            break

    print("=" * 72)
    if break_point is not None:
        log(f"性能拐点出现在并发 {break_point}（错误率 ≥ {STOP_ERROR_RATE * 100:.0f}%）")
    else:
        log(f"所有档位均通过，峰值稳定 QPS 约 {best_qps:.1f}")
    log("阶梯压测结束")


if __name__ == "__main__":
    main()