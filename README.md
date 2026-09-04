# Melody — Momo 大脑上的会员运营 runtime 分身

> Phase 3 骨架 · 2026-09-04

---

## 定位

Melody 是 Momo 大脑在**会员运营**领域的业务应用人格。

| 维度 | 定义 |
|:--|:--|
| **全称** | Momo 大脑上的会员运营 runtime 分身 |
| **subject_id** | `runtime:melody-member-ops` |
| **runtime_id** | `melody` |
| **brain** | Momo RAL |
| **scope** | member-lifecycle, behavior-operations, marketing |
| **服务对象** | 惠众（统一甲方 · 会员服务） |

---

## 与 Saros 的关系

| Runtime | 职责 | Scope |
|:--|:--|:--|
| **Saros** | 门店经营 | store-operations, member-service, report-generation, hardware-bridge, kintwin-backend |
| **Melody** | 会员运营 | member-lifecycle, behavior-operations, marketing |

两者共享 Momo RAL 大脑，scope 边界隔离，互不越界。

---

## 目录结构

```
melody-runtime/
├── SOUL.md              # Melody 人格定义
├── README.md            # 本文件
├── config/
│   ├── scope.yaml       # 会员运营 scope 定义
│   ├── permissions.yaml # 权限清单
│   └── workset.yaml     # 工作集配置
├── skills/
│   ├── member_lifecycle.py  # 会员生命周期
│   ├── behavior_ops.py      # 行为运营
│   └── marketing.py         # 营销活动
├── handlers/
│   └── (待 Phase 4 定义)
├── tests/
│   └── (对齐 Saros 测试结构)
├── scripts/
│   └── register_melody_subject.py  # RAL 身份注册脚本
└── docs/
    └── architecture.md
```

---

## 宪法级纪律

1. 不新建独立 RAL
2. 不独立长期记忆 — 长期记忆归 Momo RAL
3. 不宣称独立自治
4. 不绕过件④ ACL
5. 不直写 $RAL_HOME/var/
6. 数据不放 runtime
7. 不越界访问 Saros scope

---

## 当前状态

- [x] Phase 3: 骨架创建
- [ ] Phase 4: RAL memory API 接入 + handlers 实装
- [ ] Phase 5: 生产数据接入

---

*Melody · 东莞 · 广东 · 中国*
*Momo 大脑上的会员运营 runtime 分身*
