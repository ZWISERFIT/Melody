#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Melody Runtime 服务入口 · main.py
217号施工令 · 任务一 #40 · 2026-09-07

架构定位：Melody = Momo 大脑（Hermes 端）上的「会员运营」Runtime 分身。
本服务在 8770 端口对外提供入口：
  客户端 → melody-runtime(8770) → 权限校验/技能路由 → LAO router(8765, x-lao-agent:melody) → Momo
  返回结果统一打 agent: melody 标签。

纪律：
  - 所有 LLM 请求必须经 LAO router（复用 MelodyLAOClient，禁止直连 LLM）
  - melody 已注册进 LAO AGENT_KEYS（Momo 的 key，归因正确），不再是临时请求头旁路
  - fail-open：不因单请求异常拖垮服务
  - 纯标准库实现，无外部依赖，适配 systemd 常驻
"""
import os
import sys
import json
import time
import uuid
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# 确保可 import 同目录的 lao_client
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lao_client import MelodyLAOClient, MELODY_AGENT, MELODY_SCOPE  # noqa: E402

MELODY_PORT = int(os.environ.get("MELODY_PORT", "8770"))
AGENT_LABEL = "melody"
RUNTIME_NAME = "melody-runtime"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [melody-runtime] %(levelname)s %(message)s",
)
logger = logging.getLogger("melody.main")

# LAO 转发客户端（单例）
_lao = MelodyLAOClient()

# 允许经本 runtime 处理的 scope（会员运营域）
ALLOWED_SCOPES = {MELODY_SCOPE, "member-operations", ""}


def _permission_check(body, headers):
    """权限校验：确认请求属会员运营域，拒绝越权。返回 (ok, reason)。"""
    scope = (headers.get("x-melody-scope") or body.get("scope") or "").strip()
    if scope and scope not in ALLOWED_SCOPES:
        return False, "scope=%s 超出会员运营域" % scope
    if not isinstance(body.get("messages"), list) or not body["messages"]:
        return False, "缺少 messages"
    return True, "ok"


def _tag_agent(resp_obj):
    """给 LAO 响应打 agent: melody 标签（顶层 + 每个 choice.message）。"""
    if not isinstance(resp_obj, dict):
        return {"agent": AGENT_LABEL, "runtime": RUNTIME_NAME, "response": resp_obj}
    resp_obj["agent"] = AGENT_LABEL
    resp_obj["runtime"] = RUNTIME_NAME
    return resp_obj


class MelodyHandler(BaseHTTPRequestHandler):
    server_version = "MelodyRuntime/1.0"

    def log_message(self, fmt, *args):  # 收敛默认访问日志
        logger.info("%s - %s", self.address_string(), fmt % args)

    def _send_json(self, code, obj, req_id=None):
        payload = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("x-lao-agent", AGENT_LABEL)
        if req_id:
            self.send_header("x-request-id", req_id)
        self.end_headers()
        self.wfile.write(payload)

    def _read_body(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def do_GET(self):
        if self.path.rstrip("/") in ("/health", "/healthz"):
            self._send_json(200, {
                "status": "ok",
                "agent": AGENT_LABEL,
                "runtime": RUNTIME_NAME,
                "scope": MELODY_SCOPE,
                "lao_upstream": _lao.router_url,
                "ts": time.time(),
            })
            return
        if self.path.rstrip("/") == "/stats":
            self._send_json(200, {"agent": AGENT_LABEL, "stats": _lao.stats})
            return
        self._send_json(404, {"error": "not found", "path": self.path})

    def do_POST(self):
        req_id = self.headers.get("x-request-id") or str(uuid.uuid4())
        path = self.path.rstrip("/")
        if path not in ("/v1/chat/completions", "/chat", "/v1/chat"):
            self._send_json(404, {"error": "not found", "path": self.path}, req_id)
            return
        try:
            body = self._read_body()
        except Exception as e:  # noqa: BLE001
            self._send_json(400, {"error": "bad json: %s" % e, "agent": AGENT_LABEL}, req_id)
            return

        ok, reason = _permission_check(body, self.headers)
        if not ok:
            self._send_json(403, {"error": reason, "agent": AGENT_LABEL}, req_id)
            return

        # 经 LAO router 转发（携带 x-lao-agent:melody，享 N1 认知压缩/经验直返）
        result = _lao.chat(
            messages=body.get("messages", []),
            model=body.get("model", ""),
            extra_headers={"x-request-id": req_id},
            timeout=int(body.get("timeout", 60)),
        )
        if not result.get("ok"):
            self._send_json(502, {
                "error": "LAO 转发失败: %s" % result.get("error"),
                "agent": AGENT_LABEL,
                "source": result.get("source"),
            }, req_id)
            return

        tagged = _tag_agent(result.get("response") or {})
        logger.info("chat ok req_id=%s model=%s", req_id, body.get("model", ""))
        self._send_json(200, tagged, req_id)


def main():
    addr = ("127.0.0.1", MELODY_PORT)
    httpd = ThreadingHTTPServer(addr, MelodyHandler)
    logger.info("Melody runtime 启动: http://%s:%d  (agent=%s upstream=%s)",
                addr[0], MELODY_PORT, AGENT_LABEL, _lao.router_url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Melody runtime 停止")
        httpd.shutdown()


if __name__ == "__main__":
    main()
