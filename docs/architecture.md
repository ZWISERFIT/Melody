# Melody 架构文档

> Phase 3 骨架 · 2026-09-04

---

## 1. 定位

Melody 是 Momo 大脑在**会员运营**领域的业务应用人格。

| 维度 | 定义 |
|:--|:--|
| **全称** | Momo 大脑上的会员运营 runtime 分身 |
| **subject_id** | `runtime:melody-member-ops` |
| **runtime_id** | `melody` |
| **brain** | Momo RAL |
| **scope** | member-lifecycle, behavior-operations, marketing |

---

## 2. 与 Saros 的关系

```
┌─────────────────────────────────────────────────────────┐
│                    Momo RAL (大脑)                       │
│              共享长期记忆 + 核心智能                        │
└─────────────────────────────────────────────────────────┘
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
┌─────────────────────┐       ┌─────────────────────┐
│       Saros         │       │       Melody        │
│   门店经营分身       │       │   会员运营分身       │
├─────────────────────┤       ├─────────────────────┤
│ • store-operations  │       │ • member-lifecycle  │
│ • member-service    │       │ • behavior-ops      │
│ • report-generation │       │ • marketing         │
│ • hardware-bridge   │       │                     │
│ • kintwin-backend   │       │                     │
├─────────────────────┤       ├─────────────────────┤
│ 服务: 惠鑫(门店)    │       │ 服务: 惠众(甲方)    │
└─────────────────────┘       └─────────────────────┘
```

---

## 3. Scope 边界

### Melody scope（可访问）

| Scope | 说明 |
|:--|:--|
| member-lifecycle | 会员生命周期（注册、活跃、沉默、流失） |
| behavior-operations | 行为运营（消费频次、偏好、复购率） |
| marketing | 营销运营（拉新、促活、召回） |

### Saros scope（禁止访问）

| Scope | 说明 |
|:--|:--|
| store-operations | 门店运营（开关门、设备状态） |
| member-service | 会员服务（签到、约课） |
| report-generation | 报告生成（日报、周报） |
| hardware-bridge | 硬件桥接（RV1109、HTTP BS） |
| kintwin-backend | KinTwin 小程序后端 |

---

## 4. 宪法级纪律

1. 不新建独立 RAL
2. 不独立长期记忆 — 长期记忆归 Momo RAL
3. 不宣称独立自治
4. 不绕过件④ ACL
5. 不直写 $RAL_HOME/var/
6. 数据不放 runtime
7. 不越界访问 Saros scope

---

## 5. 目录结构

```
melody-runtime/
├── SOUL.md              # 人格定义
├── README.md            # 项目说明
├── config/
│   ├── scope.yaml       # scope 定义
│   ├── permissions.yaml # 权限清单
│   └── workset.yaml     # 工作集配置
├── skills/
│   ├── member_lifecycle.py  # 会员生命周期
│   ├── behavior_ops.py      # 行为运营
│   └── marketing.py         # 营销活动
├── handlers/
│   └── (待 Phase 4 定义)
├── tests/
│   └── test_skeleton.py
├── scripts/
│   └── register_melody_subject.py
└── docs/
    └── architecture.md
```

---

## 6. 阶段规划

| Phase | 内容 | 状态 |
|:--|:--|:--|
| Phase 3 | 骨架创建 | ✅ 完成 |
| Phase 4 | RAL memory API 接入 + handlers 实装 | 待启动 |
| Phase 5 | 生产数据接入 | 待规划 |

---

*Melody · 东莞 · 广东 · 中国*
*Momo 大脑上的会员运营 runtime 分身*
