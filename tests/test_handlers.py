"""
Melody handlers tests
170号施工令 · Phase 2 · 2026-09-04

测试 13 个 handlers 的参数校验逻辑
"""
import sys
import os
import unittest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from handlers.member_lifecycle import (
    handle_register, handle_renew, handle_downgrade,
    handle_cancel, handle_query
)
from handlers.behavior_ops import (
    handle_checkin, handle_points, handle_notification, handle_tag
)
from handlers.marketing import (
    handle_campaign, handle_coupon, handle_recommend, handle_repurchase
)


class TestMemberLifecycle(unittest.TestCase):
    """测试会员生命周期 handlers"""

    def test_register_missing_params(self):
        result = handle_register("", "张三", "13800138000")
        self.assertEqual(result["status"], "error")

    def test_renew_missing_params(self):
        result = handle_renew("")
        self.assertEqual(result["status"], "error")

    def test_downgrade_missing_params(self):
        result = handle_downgrade("M001", "", "standard")
        self.assertEqual(result["status"], "error")

    def test_cancel_missing_params(self):
        result = handle_cancel("")
        self.assertEqual(result["status"], "error")

    def test_query_missing_params(self):
        result = handle_query("")
        self.assertEqual(result["status"], "error")


class TestBehaviorOps(unittest.TestCase):
    """测试行为运营 handlers"""

    def test_checkin_missing_params(self):
        result = handle_checkin("")
        self.assertEqual(result["status"], "error")

    def test_points_missing_params(self):
        result = handle_points("", "add", 100)
        self.assertEqual(result["status"], "error")

    def test_points_invalid_action(self):
        result = handle_points("M001", "invalid", 100)
        self.assertEqual(result["status"], "error")

    def test_notification_missing_params(self):
        result = handle_notification("", "测试消息")
        self.assertEqual(result["status"], "error")

    def test_tag_missing_params(self):
        result = handle_tag("", "VIP")
        self.assertEqual(result["status"], "error")

    def test_tag_invalid_action(self):
        result = handle_tag("M001", "VIP", "invalid")
        self.assertEqual(result["status"], "error")


class TestMarketing(unittest.TestCase):
    """测试营销活动 handlers"""

    def test_campaign_missing_params(self):
        result = handle_campaign("", "C001")
        self.assertEqual(result["status"], "error")

    def test_campaign_invalid_action(self):
        result = handle_campaign("M001", "C001", "invalid")
        self.assertEqual(result["status"], "error")

    def test_coupon_missing_params(self):
        result = handle_coupon("", "CP001")
        self.assertEqual(result["status"], "error")

    def test_coupon_invalid_action(self):
        result = handle_coupon("M001", "CP001", "invalid")
        self.assertEqual(result["status"], "error")

    def test_recommend_missing_params(self):
        result = handle_recommend("", "M002")
        self.assertEqual(result["status"], "error")

    def test_repurchase_missing_params(self):
        result = handle_repurchase("", "P001")
        self.assertEqual(result["status"], "error")


if __name__ == "__main__":
    unittest.main()
