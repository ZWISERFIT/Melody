"""
Melody handlers package
170号施工令 · Phase 2 · 2026-09-04
"""
from .member_lifecycle import (
    handle_register,
    handle_renew,
    handle_downgrade,
    handle_cancel,
    handle_query
)
from .behavior_ops import (
    handle_checkin,
    handle_points,
    handle_notification,
    handle_tag
)
from .marketing import (
    handle_campaign,
    handle_coupon,
    handle_recommend,
    handle_repurchase
)

__all__ = [
    # member_lifecycle
    'handle_register',
    'handle_renew',
    'handle_downgrade',
    'handle_cancel',
    'handle_query',
    # behavior_ops
    'handle_checkin',
    'handle_points',
    'handle_notification',
    'handle_tag',
    # marketing
    'handle_campaign',
    'handle_coupon',
    'handle_recommend',
    'handle_repurchase',
]
