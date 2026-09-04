"""
Melody handler: 会员生命周期管理
170号施工令 · Phase 2 · 2026-09-04

5个函数：注册/续费/降级/注销/查询
"""
import hashlib
import json
from datetime import datetime
from melody_client import get_client, MELODY_SUBJECT_ID, MELODY_SCOPE


def handle_register(member_id: str, name: str, phone: str, card_type: str = "standard") -> dict:
    """会员注册"""
    if not member_id or not name or not phone:
        return {"status": "error", "message": "缺少必填参数: member_id, name, phone"}

    client = get_client()

    # 构建记忆卡
    card_metadata = {
        "subject_id": f"user:{member_id}",
        "library": "personal",
        "title": f"会员注册 - {name}",
        "content": json.dumps({
            "member_id": member_id,
            "name": name,
            "phone": phone,
            "card_type": card_type,
            "registered_at": datetime.now().isoformat(),
            "status": "active"
        }, ensure_ascii=False),
        "tags": ["member", "registration", card_type],
        "origin_path": f"melody/member_lifecycle/register/{member_id}",
        "origin_sha256": hashlib.sha256(f"{member_id}:{name}:{phone}".encode()).hexdigest()
    }

    card_id = client.register_memory(card_metadata)
    return {
        "status": "success",
        "action": "register",
        "member_id": member_id,
        "card_id": card_id,
        "message": "会员注册成功"
    }


def handle_renew(member_id: str, period: str = "1year") -> dict:
    """会员续费"""
    if not member_id:
        return {"status": "error", "message": "缺少必填参数: member_id"}

    client = get_client()

    card_metadata = {
        "subject_id": f"user:{member_id}",
        "library": "personal",
        "title": f"会员续费 - {member_id}",
        "content": json.dumps({
            "member_id": member_id,
            "period": period,
            "renewed_at": datetime.now().isoformat(),
            "status": "renewed"
        }, ensure_ascii=False),
        "tags": ["member", "renewal", period],
        "origin_path": f"melody/member_lifecycle/renew/{member_id}",
        "origin_sha256": hashlib.sha256(f"{member_id}:{period}".encode()).hexdigest()
    }

    card_id = client.register_memory(card_metadata)
    return {
        "status": "success",
        "action": "renew",
        "member_id": member_id,
        "period": period,
        "card_id": card_id,
        "message": "续费成功"
    }


def handle_downgrade(member_id: str, from_card_type: str, to_card_type: str) -> dict:
    """会员降级"""
    if not member_id or not from_card_type or not to_card_type:
        return {"status": "error", "message": "缺少必填参数"}

    client = get_client()

    card_metadata = {
        "subject_id": f"user:{member_id}",
        "library": "personal",
        "title": f"会员降级 - {member_id}",
        "content": json.dumps({
            "member_id": member_id,
            "from_card_type": from_card_type,
            "to_card_type": to_card_type,
            "downgraded_at": datetime.now().isoformat(),
            "status": "downgraded"
        }, ensure_ascii=False),
        "tags": ["member", "downgrade", from_card_type, to_card_type],
        "origin_path": f"melody/member_lifecycle/downgrade/{member_id}",
        "origin_sha256": hashlib.sha256(f"{member_id}:{from_card_type}:{to_card_type}".encode()).hexdigest()
    }

    card_id = client.register_memory(card_metadata)
    return {
        "status": "success",
        "action": "downgrade",
        "member_id": member_id,
        "from": from_card_type,
        "to": to_card_type,
        "card_id": card_id,
        "message": "降级成功"
    }


def handle_cancel(member_id: str, reason: str = "") -> dict:
    """会员注销"""
    if not member_id:
        return {"status": "error", "message": "缺少必填参数: member_id"}

    client = get_client()

    card_metadata = {
        "subject_id": f"user:{member_id}",
        "library": "personal",
        "title": f"会员注销 - {member_id}",
        "content": json.dumps({
            "member_id": member_id,
            "reason": reason,
            "cancelled_at": datetime.now().isoformat(),
            "status": "cancelled"
        }, ensure_ascii=False),
        "tags": ["member", "cancellation"],
        "origin_path": f"melody/member_lifecycle/cancel/{member_id}",
        "origin_sha256": hashlib.sha256(f"{member_id}:{reason}".encode()).hexdigest()
    }

    card_id = client.register_memory(card_metadata)
    return {
        "status": "success",
        "action": "cancel",
        "member_id": member_id,
        "card_id": card_id,
        "message": "注销成功"
    }


def handle_query(member_id: str) -> dict:
    """会员查询"""
    if not member_id:
        return {"status": "error", "message": "缺少必填参数: member_id"}

    client = get_client()

    # 检索会员相关记忆
    results = client.retrieve_memory(
        subject_id=f"user:{member_id}",
        scope=MELODY_SCOPE,
        query="member registration renewal",
        budget=10
    )

    return {
        "status": "success",
        "action": "query",
        "member_id": member_id,
        "records": results,
        "count": len(results) if results else 0
    }
