"""
Melody RAL 身份注册脚本
Phase 3 · 2026-09-04

注册 runtime:melody-member-ops 到 RAL 身份层
"""
import sys
sys.path.insert(0, '/home/agentuser/ral-core')

from ral.identity.api import Identity
from ral.db.connection import get_connection


def register_melody_subject():
    """注册 Melody 身份到 RAL"""
    conn = get_connection()
    actor = 'founder-approval-phase3'
    runtime = 'melody'

    identity = Identity(conn, actor, runtime)

    # 注册 subject
    result = identity.register_subject(
        kind='runtime',
        name='melody-member-ops',
        display_name='Melody - Momo大脑上的会员运营runtime分身',
        authorized_by='founder-approval-phase3'
    )

    print(f"注册结果: {result}")
    return result


if __name__ == '__main__':
    register_melody_subject()
