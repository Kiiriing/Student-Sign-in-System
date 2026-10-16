# core/database.py
# MySQL 数据库连接模块（带连接池）

import queue
import re
import threading
import time

from contextlib import contextmanager

import pymysql


# ============================================================
# MySQL 配置
# ============================================================

MYSQL_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,

    "user": "root",
    "password": "123456",

    "database": "student_signin",

    "charset": "utf8mb4",

    # 返回字典
    # 例如：
    #
    # {
    #     "id": "...",
    #     "username": "student1"
    # }
    #
    "cursorclass": pymysql.cursors.DictCursor,

    # 自动提交
    "autocommit": True,

    # 建连超时（秒），避免数据库无响应时请求长时间挂起
    "connect_timeout": 5,
}


# ============================================================
# 连接池配置
# ============================================================

# 池中保留的空闲连接上限
POOL_SIZE = 10

# 同时在用的物理连接上限
#
# 高并发下一旦放开，每个请求都会去开新连接，
# 很容易撞上 MySQL 的 max_connections（默认 151）；
# 这里用信号量卡住上限：超出的请求短暂排队等连接，
# 而不是把 MySQL 打爆。
MAX_CONNECTIONS = 50

# 等待可用连接的最长时间（秒）
ACQUIRE_TIMEOUT = 10


class DBPoolBusyError(RuntimeError):
    """
    连接池排队超时（池内连接全部在用且等待超过 ACQUIRE_TIMEOUT）

    单独定义一个异常类型，而不是直接抛 RuntimeError，
    是为了让 main.py 能把这个异常映射成 503（服务暂不可用）
    而不是笼统的 500（服务器内部错误）。
    """

    pass


# ============================================================
# 数据库写操作追踪
# ============================================================
#
# core/backup.py 的「空闲自动备份」需要知道「最后一次真正改动数据」的时间。
#
# 为什么在游标上打点，而不是在 conn.commit() 上打点：
# 连接是 autocommit=True，写语句一执行就已经落库，
# commit() 根本不是所有写路径的必经点。
#
# 判定口径（只认「数据被改动」）：
#
#   - 只认 INSERT / UPDATE / DELETE / REPLACE 四类 DML；
#   - 且影响行数 > 0（幂等的空更新不算改动）。
#
# 表结构变更（CREATE / ALTER / DROP）不计入，否则启动时的
# CREATE TABLE IF NOT EXISTS 会凭空刷新一次时间戳。
#
# ============================================================

_last_write_at = None
_write_lock = threading.Lock()

_DML_PATTERN = re.compile(
    r"^\s*(?:/\*.*?\*/\s*|--[^\n]*\n\s*|#[^\n]*\n\s*)*(INSERT|UPDATE|DELETE|REPLACE)\b",
    re.IGNORECASE | re.DOTALL,
)


def mark_db_write():
    """记录一次「数据被改动」的时间（内部使用）"""

    global _last_write_at

    with _write_lock:
        _last_write_at = time.time()


def get_last_write_at():
    """最后一次数据改动的时间戳（秒）；本进程内还没改动过时返回 None"""

    return _last_write_at


class _WriteTrackingCursor:
    """
    包装 pymysql 游标：执行「确实改动了数据」的 DML 时打一次时间戳

    只接管两个执行入口，其余属性原样透传给真实游标，
    因此对调用方完全透明（fetchone / rowcount / close 等照常可用）。
    """

    __slots__ = ("_cursor",)

    def __init__(self, cursor):
        self._cursor = cursor

    def _note(self, query):
        """命中 DML 且影响行数 > 0 时，记录一次改动时间"""

        if not isinstance(query, str) or not _DML_PATTERN.match(query):
            return

        try:
            affected = self._cursor.rowcount
        except Exception:
            affected = 0

        if affected and affected > 0:
            mark_db_write()

    def execute(self, *args, **kwargs):
        result = self._cursor.execute(*args, **kwargs)

        if args:
            self._note(args[0])

        return result

    def executemany(self, *args, **kwargs):
        result = self._cursor.executemany(*args, **kwargs)

        if args:
            self._note(args[0])

        return result

    def __getattr__(self, name):
        return getattr(self._cursor, name)

    def __enter__(self):
        self._cursor.__enter__()
        return self

    def __exit__(self, *exc_info):
        return self._cursor.__exit__(*exc_info)


class _PooledConnection(pymysql.connections.Connection):
    """
    带池化的 MySQL 连接

    与普通连接唯一的区别：

        conn.close()

    不再真正关闭 TCP 连接，而是把连接归还到连接池，供后续请求复用。

    这样每个请求省掉一次 TCP 握手 + 身份认证的开销，
    调用方代码不需要任何改动（依旧 get_db() / conn.close()）。
    """

    def __init__(self, pool, **kwargs):
        self._pool = pool
        super().__init__(**kwargs)

    def close(self):
        pool = getattr(self, "_pool", None)

        # 不属于任何连接池 → 走原生关闭逻辑（真正断开）
        if pool is None:
            return super().close()

        # 只归还一次，防止重复 close 把同一连接放进池中两次
        self._pool = None
        pool.release(self)

    def cursor(self, *args, **kwargs):
        # 所有 SQL 都经这里下发，因此这里是「数据改动」打点的唯一入口
        return _WriteTrackingCursor(super().cursor(*args, **kwargs))


class _ConnectionPool:
    """线程安全的 MySQL 连接池（基于 queue + 信号量，无第三方依赖）"""

    def __init__(self, max_idle, max_total):
        self._idle = queue.Queue(maxsize=max_idle)
        self._slots = threading.BoundedSemaphore(max_total)

    def _create(self):
        """新建一条连接（调用方需已持有 slot）"""
        return _PooledConnection(self, **MYSQL_CONFIG)

    def _create_guarded(self):
        """
        新建连接，失败时归还 slot

        否则 MySQL 不可用期间每次失败都会吞掉一个 slot，
        累计耗尽后池子会被永久卡死（即使数据库已经恢复）。
        """
        try:
            return self._create()
        except Exception:
            self._slots.release()
            raise

    def acquire(self):
        """取出（或新建）一条可用连接"""
        if not self._slots.acquire(timeout=ACQUIRE_TIMEOUT):
            raise DBPoolBusyError("数据库连接繁忙，请稍后重试")

        try:
            conn = self._idle.get_nowait()
        except queue.Empty:
            return self._create_guarded()

        # 关键：重新标记归属，否则这次 close() 会被当成普通连接真正断开，
        # 导致连接只用一次就废掉、池子永远攒不住连接
        conn._pool = self

        # 复用前探活：连接已被 MySQL 断开时直接丢弃重建
        try:
            conn.ping(False)
            return conn
        except Exception:
            conn._pool = None
            self._force_close(conn)
            return self._create_guarded()

    def release(self, conn):
        """归还连接：闲置则入池，池满则真正关闭"""
        # 清理可能残留的事务状态（autocommit=True 时为空操作）
        try:
            conn.rollback()
        except Exception:
            pass

        try:
            self._idle.put_nowait(conn)
        except queue.Full:
            self._force_close(conn)
        finally:
            self._slots.release()

    @staticmethod
    def _force_close(conn):
        """绕过池化逻辑，真正关闭连接"""
        try:
            pymysql.connections.Connection.close(conn)
        except Exception:
            pass


# 全局连接池（进程内共享，Flask 多线程下安全）
_pool = _ConnectionPool(POOL_SIZE, MAX_CONNECTIONS)


# ============================================================
# 获取数据库连接
# ============================================================

def get_db():
    """
    从连接池获取一个 MySQL 数据库连接

    使用方式：

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(...)

        conn.close()   # 归还到连接池，而不是断开连接
    """

    return _pool.acquire()


# ============================================================
# 游标上下文管理器
# ============================================================

@contextmanager
def db_cursor():
    """
    数据库游标上下文管理器（只读场景推荐用法）

    把各接口里重复出现的下面这套模板收敛到一处：

        conn = None
        try:
            conn = get_db()
            cursor = conn.cursor()
            ...
            cursor.execute(...)
        finally:
            cursor.close()
            conn.close()

    改写成：

        with db_cursor() as cursor:
            cursor.execute(...)

    说明：

        - 退出时先关游标再归还连接（conn.close() 走连接池归还，不是断连）。
        - 只适用于「只读」逻辑：连接是 autocommit=True，
          不需要显式 commit / rollback。
          写接口请保留各自的 commit + rollback 显式逻辑。
    """

    conn = get_db()

    try:
        cursor = conn.cursor()

        try:
            yield cursor

        finally:
            cursor.close()

    finally:
        conn.close()