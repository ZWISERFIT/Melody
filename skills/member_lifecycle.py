"""Melody 技能模块 — 会员生命周期管理（实装版）。

207号件 · 加固四 · Phase 3

实装策略：
- 通过 LAO router 获取智能会员分析
- 通过 RAL memory 持久化操作记录
- fail-open: LAO 不可用时返回结构化默认响应
"""

import time
import json
import logging

logger = logging.getLogger("melody.skills.member_lifecycle")

SYSTEM_PROMPT = """你是 Melody，ZWISERFIT 健身房的会员运营 AI 助手。
你的职责：会员注册、激活、活跃度追踪、沉默召回、流失分析。
回复要简洁、数据驱动、可操作。"""


def _get_lao():
    try:
        from lao_client import get_lao_client
        return get_lao_client()
    except ImportError:
        return None


def _get_ral():
    try:
        from melody_client import get_client
        return get_client()
    except ImportError:
        return None


def _persist(action: str, member_id: str, extra: dict):
    """持久化操作到 RAL。"""
    ral = _get_ral()
    if ral is None:
        return
    try:
        card_metadata = {
            "subject_id": f"user:{member_id}",
            "library": "personal",
            "title": f"会员操作-{action}",
            "content": json.dumps({
                "action": action,
                "member_id": member_id,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                **extra,
            }, ensure_ascii=False),
            "tags": ["member_lifecycle", action, member_id],
            "origin_path": f"melody/lifecycle/{action}/{member_id}",
            "origin_sha256": f"melody-{action}-{member_id}-{int(time.time())}",
        }
        ral.register_memory(card_metadata)
    except Exception as e:
        logger.warning("RAL persist failed: %s", e)


def register_new_member(member_id: str, name: str, phone: str) -> dict:
    """新会员注册。"""
    _persist("register", member_id, {"name": name, "phone": phone})

    lao = _get_lao()
    if lao:
        analysis = lao.ask(
            f"新会员 {name}({member_id}) 注册成功。给出新人引导建议（3条以内）。",
            system_prompt=SYSTEM_PROMPT,
            timeout=10,
        )
        if analysis.get("ok"):
            return {
                "status": "success",
                "action": "register_new_member",
                "member_id": member_id,
                "name": name,
                "onboarding_tips": analysis["content"],
                "source": "lao_router",
            }

    return {
        "status": "success",
        "action": "register_new_member",
        "member_id": member_id,
        "name": name,
        "message": "注册成功",
        "source": "local",
    }


def activate_member(member_id: str) -> dict:
    """会员激活。"""
    _persist("activate", member_id, {})

    return {
        "status": "success",
        "action": "activate_member",
        "member_id": member_id,
        "message": "会员已激活",
        "source": "local",
    }


def track_engagement(member_id: str) -> dict:
    """活跃度追踪（LAO 智能分析）。"""
    ral = _get_ral()
    history = []
    if ral:
        try:
            history = ral.retrieve_memory(
                subject_id=f"user:{member_id}",
                scope="member-operations",
                query="member checkin visit engagement",
                budget=20,
            )
        except Exception:
            pass

    records = history if isinstance(history, list) else []

    lao = _get_lao()
    if lao:
        analysis = lao.ask(
            f"分析会员 {member_id} 的活跃度。历史记录数: {len(records)}。给出活跃度评级和建议。",
            system_prompt=SYSTEM_PROMPT,
            timeout=10,
        )
        if analysis.get("ok"):
            return {
                "status": "success",
                "action": "track_engagement",
                "member_id": member_id,
                "engagement_analysis": analysis["content"],
                "record_count": len(records),
                "source": "lao_router",
            }

    return {
        "status": "success",
        "action": "track_engagement",
        "member_id": member_id,
        "record_count": len(records),
        "message": "活跃度数据已收集",
        "source": "local",
    }


def reengage_silent_member(member_id: str, silent_days: int) -> dict:
    """沉默会员召回。"""
    _persist("reengage", member_id, {"silent_days": silent_days})

    lao = _get_lao()
    if lao:
        analysis = lao.ask(
            f"会员 {member_id} 已 {silent_days} 天未到店。设计一条召回消息（50字以内，友好不施压）。",
            system_prompt=SYSTEM_PROMPT,
            timeout=10,
        )
        if analysis.get("ok"):
            return {
                "status": "success",
                "action": "reengage_silent_member",
                "member_id": member_id,
                "silent_days": silent_days,
                "recall_message": analysis["content"],
                "source": "lao_router",
            }

    return {
        "status": "success",
        "action": "reengage_silent_member",
        "member_id": member_id,
        "silent_days": silent_days,
        "message": "召回方案已生成",
        "source": "local",
    }


def churn_analysis(member_id: str) -> dict:
    """流失分析。"""
    ral = _get_ral()
    history = []
    if ral:
        try:
            history = ral.retrieve_memory(
                subject_id=f"user:{member_id}",
                scope="member-operations",
                query="member visit checkin churn",
                budget=20,
            )
        except Exception:
            pass

    records = history if isinstance(history, list) else []

    lao = _get_lao()
    if lao:
        analysis = lao.ask(
            f"对会员 {member_id} 进行流失风险分析。历史互动记录数: {len(records)}。"
            f"给出风险等级(高/中/低)和挽留建议。",
            system_prompt=SYSTEM_PROMPT,
            timeout=10,
        )
        if analysis.get("ok"):
            return {
                "status": "success",
                "action": "churn_analysis",
                "member_id": member_id,
                "churn_analysis": analysis["content"],
                "record_count": len(records),
                "source": "lao_router",
            }

    return {
        "status": "success",
        "action": "churn_analysis",
        "member_id": member_id,
        "record_count": len(records),
        "message": "流失分析数据已收集",
        "source": "local",
    }
