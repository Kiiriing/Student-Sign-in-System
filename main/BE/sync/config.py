# -*- coding: utf-8 -*-
# sync/config.py
# 跨站签到数据同步 · 站点配置
#
# 三站各自维护一份本文件：
#   - SITE_CODE 三站必须互不相同
#   - PEERS 指向另外两站，code 必须等于对方的 SITE_CODE
#   - token 是双方约定的同一串字符串（换站即换 token，不要留空）
#
# 修改后需要重启后端才生效。

import os


# ============================================================
# 对端协议形态
# ============================================================
#
# 各对端实现形态不同，用 protocol 字段区分：
#
#   contract  契约式：事件信封 + X-Sync-Token
#             我方 push → POST 对端 /api/sync/inbound/push
#             我方 pull → GET  对端 /api/sync/inbound/pull
#
#   snapshot  快照式：整库 JSON（students / sessions / records），无令牌
#             我方推送 → POST 对端 /api/sync/import
#             我方拉取 → GET  对端 /api/sync/export
#
# ============================================================

PROTOCOL_CONTRACT = "contract"
PROTOCOL_SNAPSHOT = "snapshot"


# ============================================================
# 本站标识
# ============================================================

# 本站唯一标识；会随事件发给对端，并写进同步记录
SITE_CODE = os.environ.get("SYNC_SITE_CODE", "site_local")

# 本站中文名；会作为「来源站点」显示在对端界面上
SITE_NAME = os.environ.get("SYNC_SITE_NAME", "本站签到")


# ============================================================
# 对端站点
# ============================================================
#
# code     对端标识，用于展示来源站点（快照式对端不依赖它做鉴权）
# name     对端中文名，用于前端展示
# protocol 对端协议形态，见上文 PROTOCOL_CONTRACT / PROTOCOL_SNAPSHOT
# base_url 对端后端地址，不带结尾斜杠；必须是 Web 服务端口，不要填数据库端口
# token    共享令牌，优先读环境变量（仅契约式对端需要；快照式对端无鉴权）

PEERS = [
    {
        "code": "site_a",
        "name": "A 站",
        "protocol": PROTOCOL_SNAPSHOT,
        "base_url": os.environ.get("SYNC_BASE_URL_SITE_A", "http://10.32.54.172:8000"),
        "token": os.environ.get("SYNC_TOKEN_SITE_A", "change-me-site-a"),
    },
    {
        "code": "site_b",
        "name": "B 站",
        "protocol": PROTOCOL_CONTRACT,
        "base_url": os.environ.get("SYNC_BASE_URL_SITE_B", "http://10.32.54.194:8080"),
        "token": os.environ.get("SYNC_TOKEN_SITE_B", "change-me-site-b"),
    },
]


# ============================================================
# 超时与调度
# ============================================================

PUSH_TIMEOUT = 3            # 出站 push 单次超时（秒）
PULL_TIMEOUT = 3            # 出站 pull 单次超时（秒）
CHECK_TIMEOUT = 1.2         # 签到实时查重：单站超时（秒）
CHECK_TOTAL_TIMEOUT = 2.0   # 签到实时查重：整体上限（秒）

# 后台同步改为「按需触发」：只有在本站签到、收到对端 push、
# 或管理员点击前端「连接对端」时才会跑一轮，不再做定时间隔轮询。
# 这样对不可达的对端不会每 20 秒反复白超时、也不再刷错误日志。

PULL_LIMIT = 200            # 单次 pull 最多拉取的事件数
PUSH_BATCH_SIZE = 50        # 单次 push 最多携带的事件数
MAX_RETRY = 12              # outbox 最大重试次数，超过则标记失败
CACHE_TTL = 8               # 签到实时查重结果缓存时长（秒）
RECONCILE_DAYS = 30         # 对账回溯的天数范围；快照导出同样只覆盖这段窗口

# 快照式对端（整库快照形态）专用
SNAPSHOT_TIMEOUT = 30       # 快照请求超时（整库 JSON，比契约式事件流大得多）
SNAPSHOT_MIN_INTERVAL = 30  # 两轮快照推送之间的最小间隔（秒），避免频繁推全库
SNAPSHOT_DEFAULT_ORIGIN = "site_a"  # 快照入账时的默认来源站点标识
SNAPSHOT_OPEN = True        # 快照接口是否免令牌开放（A 站调用时不会带 X-Sync-Token）


def get_peer(code):
    """按 code 找对端配置，找不到返回 None"""

    for peer in PEERS:
        if peer["code"] == code:
            return peer

    return None


def peer_protocol(peer):
    """取对端协议形态；未配置时按契约式处理，兼容旧的 PEERS 配置"""

    return (peer or {}).get("protocol") or PROTOCOL_CONTRACT


def contract_peers():
    """契约式对端（事件信封 + X-Sync-Token）"""

    return [peer for peer in PEERS if peer_protocol(peer) == PROTOCOL_CONTRACT]


def snapshot_peers():
    """快照式对端（整库快照 JSON，无令牌）"""

    return [peer for peer in PEERS if peer_protocol(peer) == PROTOCOL_SNAPSHOT]


def get_peer_by_token(token):
    """按共享令牌反查是哪个对端在调用我们；无效令牌返回 None"""

    if not token:
        return None

    for peer in PEERS:
        if peer["token"] and peer["token"] == token:
            return peer

    return None


def peer_names():
    """返回 {code: name}，用于把站点标识翻译成中文名"""

    return {peer["code"]: peer["name"] for peer in PEERS}


def site_name_of(code):
    """把站点标识翻译成中文名；本站返回本站名，未配置的对端退回 code 本身"""

    if code == SITE_CODE:
        return SITE_NAME

    peer = get_peer(code)

    return peer["name"] if peer else code
