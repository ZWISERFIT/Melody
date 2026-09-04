"""
Melody RAL 连接适配器
170号施工令 · Phase 2 · 2026-09-04

封装 RAL memory API 供 handlers 调用
"""
import sys
sys.path.insert(0, '/home/agentuser/ral-core')

from ral.locator import db
from ral.memory.api import Memory
from ral.identity.api import Identity
from ral.identity import store as identity_store

# Melody 身份常量
MELODY_SUBJECT_ID = 'runtime:melody-member-ops'
MELODY_RUNTIME_ID = 'melody'
MELODY_SCOPE = 'member-operations'


class MelodyRALClient:
    """Melody RAL 客户端"""

    def __init__(self):
        self.conn = db.open_index()
        self.memory = Memory(self.conn, actor=MELODY_SUBJECT_ID, runtime=MELODY_RUNTIME_ID)
        self.identity = Identity(self.conn, actor=MELODY_SUBJECT_ID, runtime=MELODY_RUNTIME_ID)

    def resolve_identity(self, alias: str) -> str:
        """解析身份别名"""
        return self.identity.resolve_identity(alias, MELODY_RUNTIME_ID)

    def register_memory(self, card_metadata: dict, readers: list = None) -> str:
        """注册记忆卡到 RAL"""
        return self.memory.register_memory(card_metadata, readers)

    def retrieve_memory(self, subject_id: str, scope: str, query: str, budget: int = 10) -> list:
        """检索记忆卡"""
        return self.memory.retrieve_memory(subject_id, scope, query, budget)

    def ratify(self, card_id: str, approval: str, version: str = None, actor: str = None) -> bool:
        """确权记忆卡"""
        return self.memory.ratify(card_id, approval, version, actor)

    def withdraw(self, card_id: str, founder_approval: str, version: str = None) -> bool:
        """撤回记忆卡"""
        return self.memory.withdraw(card_id, founder_approval, version)

    def close(self):
        """关闭连接"""
        if self.conn:
            self.conn.close()


# 全局单例
_client = None


def get_client() -> MelodyRALClient:
    """获取 Melody RAL 客户端单例"""
    global _client
    if _client is None:
        _client = MelodyRALClient()
    return _client


if __name__ == '__main__':
    # 测试连接
    client = get_client()
    print(f"Melody RAL client initialized: subject_id={MELODY_SUBJECT_ID}")
    client.close()
