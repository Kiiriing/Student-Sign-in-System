# -*- coding: utf-8 -*-
# sync/client.py
# 跨站同步 · 出站 HTTP 客户端
#
# 项目没有 requirements.txt，这里只用标准库 urllib，不引入新依赖。

import json
import socket
import http.client

from urllib import request as urlrequest
from urllib.error import HTTPError, URLError


class SyncHttpError(Exception):
    """出站请求失败：网络不可达 / 超时 / 非 2xx / 响应不是合法 JSON"""


def _clean_text(value):
    """
    清理文本里夹带的原始响应字节 / 控制字符，避免出现乱码

    对端端口不是 HTTP 服务时（如误填成数据库端口），urllib 会把对方
    拉回来的二进制按 latin-1 解码，产生一堆不可打印字符，这里统一剔除。
    """

    if value is None:
        return ""

    kept = [
        ch for ch in str(value)
        if ch in "\r\n\t" or 0x20 <= ord(ch) <= 0x7E or ord(ch) >= 0x2E80
    ]

    return "".join(kept).strip()


def request_json(method, url, token=None, payload=None, timeout=3):
    """发起一次 JSON 请求并解析响应"""

    data = None
    headers = {"Accept": "application/json"}

    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"

    if token:
        headers["X-Sync-Token"] = token

    req = urlrequest.Request(url, data=data, headers=headers, method=method)

    try:
        with urlrequest.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
    except HTTPError as e:
        # 4xx / 5xx 也走这里；尽量把服务端返回体带出来，便于排查
        detail = ""
        try:
            detail = _clean_text(e.read().decode("utf-8", errors="replace"))
        except Exception:
            detail = ""

        raise SyncHttpError("HTTP %s %s" % (e.code, detail[:200]))
    except (URLError, socket.timeout, TimeoutError) as e:
        raise SyncHttpError("网络不可达或超时：%s" % _clean_text(e))
    except http.client.BadStatusLine:
        # 对端端口不是 HTTP 服务（例如误填成数据库端口），响应首行解析不出状态码。
        # 这里不回带原始报文，避免把对方二进制内容解码成乱码展示给用户。
        raise SyncHttpError(
            "对端返回的不是合法 HTTP 响应，请确认 base_url 是 Web 服务端口（而非数据库端口）"
        )
    except http.client.HTTPException as e:
        raise SyncHttpError("对端 HTTP 响应异常：%s" % _clean_text(e))
    except Exception as e:
        raise SyncHttpError("请求异常：%s" % _clean_text(e))

    if not body.strip():
        return {}

    try:
        return json.loads(body)
    except ValueError:
        raise SyncHttpError("响应不是合法 JSON：%s" % body[:200])


def post_json(url, payload, token=None, timeout=3):
    return request_json("POST", url, token=token, payload=payload, timeout=timeout)


def get_json(url, token=None, timeout=3):
    return request_json("GET", url, token=token, timeout=timeout)


def join_url(base_url, path):
    """拼接对端地址，容忍 base_url 结尾多写斜杠"""

    return base_url.rstrip("/") + path
