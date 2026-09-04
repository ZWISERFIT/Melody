"""
Melody handler: 营销活动
170号施工令 · Phase 2 · 2026-09-04

4个函数：活动/优惠券/推荐/复购
"""
import hashlib
import json
from datetime import datetime
from melody_client import get_client, MELODY_SCOPE


def handle_campaign(member_id: str, campaign_id: str, action: str = "join") -> dict:
    """营销活动（加入/退出/查询）"""
    if not member_id or not campaign_id:
        return {"status": "error", "message": "缺少必填参数: member_id, campaign_id"}

    if action not in ["join", "leave", "query"]:
        return {"status": "error", "message": "action 必须为 join/leave/query"}

    client = get_client()

    if action == "query":
        results = client.retrieve_memory(
            subject_id=f"user:{member_id}",
            scope=MELODY_SCOPE,
            query=f"campaign {campaign_id}",
            budget=10
        )
        return {
            "status": "success",
            "action": "query",
            "member_id": member_id,
            "campaign_id": campaign_id,
            "records": results,
            "count": len(results) if results else 0
        }

    # join or leave
    card_metadata = {
        "subject_id": f"user:{member_id}",
        "library": "personal",
        "title": f"营销活动{('加入' if action == 'join' else '退出')} - {member_id}",
        "content": json.dumps({
            "member_id": member_id,
            "campaign_id": campaign_id,
            "action": action,
            "operated_at": datetime.now().isoformat(),
            "type": "campaign"
        }, ensure_ascii=False),
        "tags": ["member", "campaign", campaign_id, action],
        "origin_path": f"melody/marketing/campaign/{member_id}",
        "origin_sha256": hashlib.sha256(f"{member_id}:{campaign_id}:{action}".encode()).hexdigest()
    }

    card_id = client.register_memory(card_metadata)
    return {
        "status": "success",
        "action": action,
        "member_id": member_id,
        "campaign_id": campaign_id,
        "card_id": card_id,
        "message": f"活动{'加入' if action == 'join' else '退出'}成功"
    }


def handle_coupon(member_id: str, coupon_id: str, action: str = "claim") -> dict:
    """优惠券（领取/使用/查询）"""
    if not member_id or not coupon_id:
        return {"status": "error", "message": "缺少必填参数: member_id, coupon_id"}

    if action not in ["claim", "use", "query"]:
        return {"status": "error", "message": "action 必须为 claim/use/query"}

    client = get_client()

    if action == "query":
        results = client.retrieve_memory(
            subject_id=f"user:{member_id}",
            scope=MELODY_SCOPE,
            query=f"coupon {coupon_id}",
            budget=10
        )
        return {
            "status": "success",
            "action": "query",
            "member_id": member_id,
            "coupon_id": coupon_id,
            "records": results,
            "count": len(results) if results else 0
        }

    # claim or use
    card_metadata = {
        "subject_id": f"user:{member_id}",
        "library": "personal",
        "title": f"优惠券{('领取' if action == 'claim' else '使用')} - {member_id}",
        "content": json.dumps({
            "member_id": member_id,
            "coupon_id": coupon_id,
            "action": action,
            "operated_at": datetime.now().isoformat(),
            "type": "coupon"
        }, ensure_ascii=False),
        "tags": ["member", "coupon", coupon_id, action],
        "origin_path": f"melody/marketing/coupon/{member_id}",
        "origin_sha256": hashlib.sha256(f"{member_id}:{coupon_id}:{action}".encode()).hexdigest()
    }

    card_id = client.register_memory(card_metadata)
    return {
        "status": "success",
        "action": action,
        "member_id": member_id,
        "coupon_id": coupon_id,
        "card_id": card_id,
        "message": f"优惠券{'领取' if action == 'claim' else '使用'}成功"
    }


def handle_recommend(member_id: str, target_member_id: str, reason: str = "") -> dict:
    """会员推荐"""
    if not member_id or not target_member_id:
        return {"status": "error", "message": "缺少必填参数: member_id, target_member_id"}

    client = get_client()

    card_metadata = {
        "subject_id": f"user:{member_id}",
        "library": "personal",
        "title": f"会员推荐 - {member_id}",
        "content": json.dumps({
            "member_id": member_id,
            "target_member_id": target_member_id,
            "reason": reason,
            "recommended_at": datetime.now().isoformat(),
            "type": "recommendation"
        }, ensure_ascii=False),
        "tags": ["member", "recommendation", target_member_id],
        "origin_path": f"melody/marketing/recommend/{member_id}",
        "origin_sha256": hashlib.sha256(f"{member_id}:{target_member_id}".encode()).hexdigest()
    }

    card_id = client.register_memory(card_metadata)
    return {
        "status": "success",
        "action": "recommend",
        "member_id": member_id,
        "target_member_id": target_member_id,
        "card_id": card_id,
        "message": "推荐已记录"
    }


def handle_repurchase(member_id: str, product_id: str, interval_days: int = 0) -> dict:
    """复购记录"""
    if not member_id or not product_id:
        return {"status": "error", "message": "缺少必填参数: member_id, product_id"}

    client = get_client()

    card_metadata = {
        "subject_id": f"user:{member_id}",
        "library": "personal",
        "title": f"复购记录 - {member_id}",
        "content": json.dumps({
            "member_id": member_id,
            "product_id": product_id,
            "interval_days": interval_days,
            "purchased_at": datetime.now().isoformat(),
            "type": "repurchase"
        }, ensure_ascii=False),
        "tags": ["member", "repurchase", product_id],
        "origin_path": f"melody/marketing/repurchase/{member_id}",
        "origin_sha256": hashlib.sha256(f"{member_id}:{product_id}".encode()).hexdigest()
    }

    card_id = client.register_memory(card_metadata)
    return {
        "status": "success",
        "action": "repurchase",
        "member_id": member_id,
        "product_id": product_id,
        "interval_days": interval_days,
        "card_id": card_id,
        "message": "复购已记录"
    }
