"""Melody 技能模块 — 行为运营（实装版）。

207号件 · 加固四 · Phase 3

实装策略：
- 通过 LAO router 获取智能行为分析
- 通过 RAL memory 持久化操作记录
- fail-open: LAO 不可用时返回结构化默认响应
"""

import time
import json
import logging

logger = logging.getLogger("melody.skills.behavior_ops")

SYSTEM_PROMPT = """你是 Melody，ZWISERFIT 健身房的会员行为运营 AI 助手。
你的职责：消费频次分析、偏好分析、复购率计算、会员价值评估。
回复要数据驱动、简洁、可操作。"""


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


def _query_member_data(member_id: str, query: str, budget: int = 20) -> list:
    """从 RAL 查询会员相关数据。"""
    ral = _get_ral()
    if ral is None:
        return []
    try:
        result = ral.retrieve_memory(
            subject_id=f"user:{member_id}",
            scope="member-operations",
            query=query,
            budget=budget,
        )
        return result if isinstance(result, list) else []
    except Exception:
        return []


def consumption_frequency(member_id: str, period: str = "month") -> dict:
    """消费频次分析。"""
    records = _query_member_data(member_id, f"consumption purchase payment {period}")

    lao = _get_lao()
    if lao:
        analysis = lao.ask(
            f"分析会员 {member_id} 在 {period} 内的消费频次。数据记录数: {len(records)}。"
            f"给出频次评级(高频/中频/低频)和建议。",
            system_prompt=SYSTEM_PROMPT,
            timeout=10,
        )
        if analysis.get("ok"):
            return {
                "status": "success",
                "action": "consumption_frequency",
                "member_id": member_id,
                "period": period,
                "frequency_analysis": analysis["content"],
                "data_points": len(records),
                "source": "lao_router",
            }

    return {
        "status": "success",
        "action": "consumption_frequency",
        "member_id": member_id,
        "period": period,
        "data_points": len(records),
        "message": "消费频次数据已收集",
        "source": "local",
    }


def preference_analysis(member_id: str) -> dict:
    """偏好分析。"""
    records = _query_member_data(member_id, "preference class booking favorite")

    lao = _get_lao()
    if lao:
        analysis = lao.ask(
            f"分析会员 {member_id} 的偏好。数据记录数: {len(records)}。"
            f"给出偏好画像（课程类型、时间段、消费习惯）。",
            system_prompt=SYSTEM_PROMPT,
            timeout=10,
        )
        if analysis.get("ok"):
            return {
                "status": "success",
                "action": "preference_analysis",
                "member_id": member_id,
                "preference_profile": analysis["content"],
                "data_points": len(records),
                "source": "lao_router",
            }

    return {
        "status": "success",
        "action": "preference_analysis",
        "member_id": member_id,
        "data_points": len(records),
        "message": "偏好数据已收集",
        "source": "local",
    }


def repurchase_rate(member_id: str) -> dict:
    """复购率计算。"""
    records = _query_member_data(member_id, "purchase renewal repurchase card")

    lao = _get_lao()
    if lao:
        analysis = lao.ask(
            f"计算会员 {member_id} 的复购率指标。购买记录数: {len(records)}。"
            f"给出复购率和续费建议。",
            system_prompt=SYSTEM_PROMPT,
            timeout=10,
        )
        if analysis.get("ok"):
            return {
                "status": "success",
                "action": "repurchase_rate",
                "member_id": member_id,
                "repurchase_analysis": analysis["content"],
                "purchase_count": len(records),
                "source": "lao_router",
            }

    return {
        "status": "success",
        "action": "repurchase_rate",
        "member_id": member_id,
        "purchase_count": len(records),
        "message": "复购数据已收集",
        "source": "local",
    }


def lifetime_value(member_id: str) -> dict:
    """会员生命周期价值（LTV）。"""
    records = _query_member_data(member_id, "purchase payment value card renewal")

    lao = _get_lao()
    if lao:
        analysis = lao.ask(
            f"评估会员 {member_id} 的生命周期价值(LTV)。交易记录数: {len(records)}。"
            f"给出 LTV 评级(高/中/低)和增值建议。",
            system_prompt=SYSTEM_PROMPT,
            timeout=10,
        )
        if analysis.get("ok"):
            return {
                "status": "success",
                "action": "lifetime_value",
                "member_id": member_id,
                "ltv_analysis": analysis["content"],
                "transaction_count": len(records),
                "source": "lao_router",
            }

    return {
        "status": "success",
        "action": "lifetime_value",
        "member_id": member_id,
        "transaction_count": len(records),
        "message": "LTV 数据已收集",
        "source": "local",
    }
