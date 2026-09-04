"""
Melody handler: 行为运营
170号施工令 · Phase 2 · 2026-09-04

4个函数：签到/积分/通知/标签
"""
import hashlib
import json
from datetime import datetime
from melody_client import get_client, MELODY_SCOPE


def handle_checkin(member_id: str, location: str = "") -> dict:
    """会员签到"""
    if not member_id:
        return {"status": "error", "message": "缺少必填参数: member_id"}

    client = get_client()

    card_metadata = {
        "subject_id": f"user:{member_id}",
        "library": "personal",
        "title": f"会员签到 - {member_id}",
        "content": json.dumps({
            "member_id": member_id,
            "location": location,
            "checked_in_at": datetime.now().isoformat(),
            "type": "checkin"
        }, ensure_ascii=False),
        "tags": ["member", "checkin", location] if location else ["member", "checkin"],
        "origin_path": f"melody/behavior_ops/checkin/{member_id}",
        "origin_sha256": hashlib.sha256(f"{member_id}:{location}".encode()).hexdigest()
    }

    card_id = client.register_memory(card_metadata)
    return {
        "status": "success",
        "action": "checkin",
        "member_id": member_id,
        "card_id": card_id,
        "message": "签到成功"
    }


def handle_points(member_id: str, action: str, amount: int, reason: str = "") -> dict:
    """积分操作（增加/扣除/查询）"""
    if not member_id or not action:
        return {"status": "error", "message": "缺少必填参数: member_id, action"}

    if action not in ["add", "deduct", "query"]:
        return {"status": "error", "message": "action 必须为 add/deduct/query"}

    client = get_client()

    if action == "query":
        results = client.retrieve_memory(
            subject_id=f"user:{member_id}",
            scope=MELODY_SCOPE,
            query="points",
            budget=20
        )
        return {
            "status": "success",
            "action": "query",
            "member_id": member_id,
            "records": results,
            "count": len(results) if results else 0
        }

    # add or deduct
    card_metadata = {
        "subject_id": f"user:{member_id}",
        "library": "personal",
        "title": f"积分{('增加' if action == 'add' else '扣除')} - {member_id}",
        "content": json.dumps({
            "member_id": member_id,
            "action": action,
            "amount": amount,
            "reason": reason,
            "operated_at": datetime.now().isoformat(),
            "type": "points"
        }, ensure_ascii=False),
        "tags": ["member", "points", action, str(amount)],
        "origin_path": f"melody/behavior_ops/points/{member_id}",
        "origin_sha256": hashlib.sha256(f"{member_id}:{action}:{amount}".encode()).hexdigest()
    }

    card_id = client.register_memory(card_metadata)
    return {
        "status": "success",
        "action": action,
        "member_id": member_id,
        "amount": amount,
        "card_id": card_id,
        "message": f"积分{'增加' if action == 'add' else '扣除'}成功"
    }


def handle_notification(member_id: str, message: str, channel: str = "app") -> dict:
    """发送通知"""
    if not member_id or not message:
        return {"status": "error", "message": "缺少必填参数: member_id, message"}

    client = get_client()

    card_metadata = {
        "subject_id": f"user:{member_id}",
        "library": "personal",
        "title": f"通知发送 - {member_id}",
        "content": json.dumps({
            "member_id": member_id,
            "message": message,
            "channel": channel,
            "sent_at": datetime.now().isoformat(),
            "type": "notification"
        }, ensure_ascii=False),
        "tags": ["member", "notification", channel],
        "origin_path": f"melody/behavior_ops/notification/{member_id}",
        "origin_sha256": hashlib.sha256(f"{member_id}:{message}".encode()).hexdigest()
    }

    card_id = client.register_memory(card_metadata)
    return {
        "status": "success",
        "action": "notification",
        "member_id": member_id,
        "channel": channel,
        "card_id": card_id,
        "message": "通知已记录"
    }


def handle_tag(member_id: str, tag: str, action: str = "add") -> dict:
    """标签操作（添加/移除）"""
    if not member_id or not tag:
        return {"status": "error", "message": "缺少必填参数: member_id, tag"}

    if action not in ["add", "remove"]:
        return {"status": "error", "message": "action 必须为 add/remove"}

    client = get_client()

    card_metadata = {
        "subject_id": f"user:{member_id}",
        "library": "personal",
        "title": f"标签{('添加' if action == 'add' else '移除')} - {member_id}",
        "content": json.dumps({
            "member_id": member_id,
            "tag": tag,
            "action": action,
            "operated_at": datetime.now().isoformat(),
            "type": "tag"
        }, ensure_ascii=False),
        "tags": ["member", "tag", action, tag],
        "origin_path": f"melody/behavior_ops/tag/{member_id}",
        "origin_sha256": hashlib.sha256(f"{member_id}:{tag}:{action}".encode()).hexdigest()
    }

    card_id = client.register_memory(card_metadata)
    return {
        "status": "success",
        "action": action,
        "member_id": member_id,
        "tag": tag,
        "card_id": card_id,
        "message": f"标签{'添加' if action == 'add' else '移除'}成功"
    }
