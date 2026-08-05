# Project Constitution（仓库级）

> 仓库级治理宪章，与子项目 `docs/project-governance/00-PROJECT-CONSTITUTION.md` 保持一致。
> 当前状态以 CURRENT-SNAPSHOT.md 为准；本文件定义不可变边界。

## Mission

本仓库支撑专业硕士论文《面向非连续时间约束的区块链数据共享关键技术研究及实现》。
论文是工程与系统研究：结论必须由可实现机制、真实实验、可复现资产与可追溯证据支持；
不寻求未经验证的新密码原语。

## Research Contents（CURRENT）

| ID | 范围 | 状态 |
|---|---|---|
| RC1 | 非连续时间策略的确定性规范化、语义表示（`I*`）、编译与边界实验 | COMPLETED_WITH_SCOPE_ADJUSTMENT |
| RC2 | 许可联盟链（Besu QBFT）上授权状态执行、CAP2 绑定、共享 Nonce 与 Fail-Closed | COMPLETED_WITH_VALID_RERUN_EVIDENCE |
| RC3 | 版本化密文头部、标准混合加密、前瞻性撤销、链上/链下状态闭环与恢复 | FORMAL_COMPLETED |

## Frozen Method Positioning

- `I*` 是唯一语义主表示：规范化半开区间有序列表，NTP1 序列化，SHA-256 `policyDigest` 绑定 `I*`。
- `C(P)` 是确定性派生的 dyadic cover 执行 IR（可选/对照/ablation），不参与 digest。
- RC2 主线路为 Baseline-I（及缓存变体）；Proposed-C 仅为对照与证伪变体。
- RC3 采用标准组件：HPKE（RFC 9180）、AES-256-GCM、JCS、Ed25519；仅前瞻性撤销。

## Explicit Non-Goals / Forbidden Claims

- 不恢复自研 ABE 或链上秘密陷门路线（见 SUPERSEDED-DESIGNS.md）。
- 不主张 `C(P)` 普遍压缩优势或任意策略 `O(log U)`。
- 不主张缓存稳定性能收益。
- 不产生 QBFT 共识性能/延迟/多验证节点可扩展性结论（C-07）。
- 不主张追溯撤销或追回已释放 CK/明文。
- 不把联盟链表述为绝对可信时间源、秘密执行环境、自动链下密钥撤销或数据机密性来源。
- 不把工程实验等同为形式化/密码学证明；不把 Pilot 当 Formal。

## Evidence And Change Rules

事实优先级：代码/raw/冻结索引 > 最新冻结证据 > 最新正式报告 > 治理文件 > 历史方案 > README/摘要。
冲突标记为 CURRENT / SUPERSEDED / HISTORICAL / PARTIALLY_VALID / UNRESOLVED，不删除历史。
正式实验 raw、预注册与结果包为冻结资产：只读；发现错误登记 `FROZEN_ASSET_ISSUE`。
