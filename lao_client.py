"""Melody LAO 客户端 — 接入 LAO router 路由层。

207号件 · 加固四 · Phase 3
职责：封装 LAO router /v1/chat/completions 调用，让 Melody 请求享受
      N1 认知压缩 + 经验直返 + 命中率追踪 + 经验积累。

纪律：
- 所有 LLM 请求必须经 LAO router，禁止直连 LLM
- 保留 x-request-id 贯穿链路
- fail-open: LAO 不可用时回退到本地 RAL 查询
"""

import json
import time
import logging

try:
    import requests as _requests
except ImportError:
    _requests = None

try:
    import urllib.request as _urllib
except ImportError:
    _urllib = None

logger = logging.getLogger("melody.lao_client")

# LAO router端点（同机部署）
LAO_ROUTER_URL = "http://127.0.0.1:8765/v1/chat/completions"
LAO_STATUS_URL = "http://127.0.0.1:8765/v1/loop/status"

# Melody 身份标记
MELODY_AGENT = "melody"
MELODY_RUNTIME_ID = "melody"
MELODY_SCOPE = "member-operations"


def _http_post_json(url: str, data: dict, headers: dict, timeout: int = 30) -> dict:
    """HTTP POST JSON，兼容 requests 和 urllib。"""
    if _requests is not None:
        resp = _requests.post(url, json=data, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    elif _urllib is not None:
        payload = json.dumps(data).encode("utf-8")
        req = _urllib.Request(url, data=payload, method="POST")
        for k, v in headers.items():
            req.add_header(k, v)
        req.add_header("Content-Type", "application/json")
        with _urllib.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    else:
        raise RuntimeError("No HTTP library available (requests or urllib)")


def _http_get_json(url: str, timeout: int = 5) -> dict:
    """HTTP GET JSON。"""
    if _requests is not None:
        resp = _requests.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    elif _urllib is not None:
        req = _urllib.Request(url)
        with _urllib.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    else:
        raise RuntimeError("No HTTP library available")


class MelodyLAOClient:
    """Melody LAO 路由客户端。

    所有 LLM 请求经 LAO router，享受：
    - N1 认知压缩（降本）
    - 经验直返（命中已有经验 → 0 token）
    - 命中率追踪（积累经验）
    - evolution 链路（错误 → 约束 → 规则 → 永久化）
    """

    def __init__(self, router_url: str = None):
        self.router_url = router_url or LAO_ROUTER_URL
        self._request_count = 0
        self._error_count = 0

    def chat(self, messages: list, model: str = "", extra_headers: dict = None,
             timeout: int = 30) -> dict:
        """发送聊天请求到 LAO router。

        Args:
            messages: OpenAI 格式消息列表
            model: 模型提示（可选）
            extra_headers: 额外 HTTP 头
            timeout: 超时秒数

        Returns:
            LAO router 返回的 OpenAI 兼容响应
        """
        self._request_count += 1
        headers = {
            "x-lao-agent": MELODY_AGENT,
            "x-lao-tier": "n1",  # Melody 默认走 N1 层（会员运营）
            "Content-Type": "application/json",
        }
        if extra_headers:
            headers.update(extra_headers)

        body = {
            "model": model,
            "messages": messages,
            "stream": False,
        }

        try:
            result = _http_post_json(self.router_url, body, headers, timeout=timeout)
            return {
                "ok": True,
                "response": result,
                "request_count": self._request_count,
                "source": "lao_router",
            }
        except Exception as e:
            self._error_count += 1
            logger.warning("LAO router request failed: %s", e)
            return {
                "ok": False,
                "error": str(e),
                "request_count": self._request_count,
                "source": "lao_router_fallback",
            }

    def ask(self, question: str, system_prompt: str = "", model: str = "",
            timeout: int = 30) -> dict:
        """简化版聊天接口。"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": question})

        result = self.chat(messages, model=model, timeout=timeout)

        if result["ok"]:
            try:
                content = result["response"]["choices"][0]["message"]["content"]
                return {
                    "ok": True,
                    "content": content,
                    "usage": result["response"].get("usage", {}),
                    "request_count": result["request_count"],
                }
            except (KeyError, IndexError):
                return {
                    "ok": False,
                    "error": "Unexpected LAO response format",
                    "response": result.get("response"),
                }
        return result

    def get_status(self) -> dict:
        """查询 LAO router 状态。"""
        try:
            return _http_get_json(LAO_STATUS_URL)
        except Exception as e:
            return {"error": str(e), "available": False}

    @property
    def stats(self) -> dict:
        """客户端统计。"""
        return {
            "total_requests": self._request_count,
            "errors": self._error_count,
            "success_rate": (
                (self._request_count - self._error_count) / max(self._request_count, 1)
            ),
        }


# ── 全局单例 ──────────────────────────────────────────────
_client = None


def get_lao_client() -> MelodyLAOClient:
    """获取 Melody LAO 客户端单例。"""
    global _client
    if _client is None:
        _client = MelodyLAOClient()
    return _client


def ask_lao(question: str, system_prompt: str = "", **kwargs) -> dict:
    """模块级快捷函数。"""
    return get_lao_client().ask(question, system_prompt=system_prompt, **kwargs)
