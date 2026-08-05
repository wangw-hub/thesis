# CURRENT SNAPSHOT — 学位论文研究仓库当前状态唯一入口

> 本文件是仓库的 **第一权威入口**。任何新的 AI 会话（Codex/GPT/其他智能体）应先读本文件，再按
> [AUTHORITY-MAP.md](AUTHORITY-MAP.md) 读取对应权威来源。
>
> 快照日期：2026-08-05（本地核验） · 状态：REPOSITORY_CONTEXT_FROZEN_READY_FOR_AI_CONTINUATION

## 1. Thesis Identity

| 项目 | 值 |
|---|---|
| 论文题目 | 面向非连续时间约束的区块链数据共享关键技术研究及实现 |
| 学位类型 | 计算机技术专业硕士（专业学位） |
| 学校 | 电子科技大学（UESTC） |
| 当前分支 | `main` |
| snapshotBasisHead | `483fc87`（生成本快照时所基于的上一个已确认提交；实时仓库 HEAD 应从 GitHub `main` 分支或本地 git 动态读取，不以静态文档中的 SHA 为准） |
| liveHead | `DYNAMIC`（github-main-or-local-git） |
| 快照日期 | 2026-08-05 |
| 仓库根（本地） | `D:\Research`（PUBLIC_GITHUB_MODE 下不可访问） |
| 公开仓库 | https://github.com/wangw-hub/thesis |

> 公开模式说明：新 AI 会话若无本地 `D:\Research` 访问权，必须按
> [AI-CONTEXT-RECOVERY.md](AI-CONTEXT-RECOVERY.md) 的 PUBLIC_GITHUB_MODE 恢复；
> 本文中标记 LOCAL_ONLY 的 raw 路径对应未上传数据，正式结论以 AUTHORITY-MAP.md
> 的 Public fallback 为准。

## 2. Research Architecture

论文围绕三项递进关键技术（研究内容一/二/三，下称 RC1/RC2/RC3）：

```
研究内容一（RC1）  非连续时间策略确定性编译
  → 唯一语义表示 I*（半开区间有序列表）+ NTP1 序列化
  → SHA-256 policyDigest（绑定 I*，不绑定 C(P)）
  → C(P) = 由 I* 确定性派生的 dyadic cover 执行 IR（可选/对照）
        │
        ▼（策略摘要进入授权语义）
研究内容二（RC2）  许可联盟链上的可信授权执行
  → AuthorizationState 合约 + CAP2（链标识/合约/策略摘要/Epoch/状态与用户版本/Nonce 绑定）
  → 共享原子 Nonce（PostgreSQL）防跨实例重放；依赖故障 Fail-Closed
  → 正式实验证明：链上状态锚定与重放控制是核心价值；
     缓存与 C(P) 无稳定端到端收益（负结果保留）
        │
        ▼（授权状态驱动密文对象生命周期）
研究内容三（RC3）  版本化密文头部与前瞻性撤销闭环
  → VersionedHeader / HeaderCore / RecipientEnvelope（HPKE + RFC 9180 + AES-256-GCM + JCS + Ed25519）
  → HeaderRegistry（链上）+ PostgreSQL 任务状态 + 链下对象存储（LocalObjectStore / Kubo）
  → RecoveryCoordinator：对象/服务故障下一致、可解释、Fail-Closed 恢复
  → 正式实验 145 measured RUNs 全部有效；仅前瞻性撤销（不可追回已释放材料）
```

三个研究内容的真实接口：RC1 的 `policyDigest` 是 RC2 CAP2 的语义锚点之一；
RC2 的 `AuthorizationState` 是 RC3 HeaderRegistry 撤销/释放窗口的链上状态来源。
RC3 不依赖 RC2 的 C(P) 或缓存机制。

## 3. Research Content 1 Current State

| 项目 | 当前事实 |
|---|---|
| status | `COMPLETED_WITH_SCOPE_ADJUSTMENT`（导师 2026-07-28 书面意见：原则认可、附条件通过） |
| core method | 时间解析 → 区间规范化 → 唯一语义表示 `I*` → NTP1 规范序列化 → SHA-256 `policyDigest`；`C(P)` 为派生 dyadic cover 执行 IR（可重新生成、不参与 digest） |
| implementation | `crypto_thesis/time-policy/src/time_policy/`（compiler、normalize、cover、digest、matcher、serialize、models） |
| formal experiment | E1：168 配置（108 E1-A + 36 E1-B + 24 E1-C）、15,120 条正式记录；E1-C 二次幂补充 540/540 记录；E2 复验 81 项通过、覆盖率 98.61% |
| supported claims | `I*` 为唯一语义主表示与 digest 输入；`C(P)` 为可选确定性执行 IR；确定性/冗余不变量成立（E1-B） |
| negative results | `C(P)` 对区间列表 0/108 更小、36/108 持平、72/108 更大；对枚举 36/108 更小（集中于连续/高覆盖策略）；中位查询成本 interval≈561ns、dyadic≈1984.7ns、enumeration≈350.4ns（Python 实现常数，非渐进证明） |
| limitations | 不构成普遍压缩/`O(log U)` 结论；实验精度而非形式化证明 |
| authoritative sources | `crypto_thesis/time-policy/研究内容一E1正式实验报告V1.0.md`、`crypto_thesis/time-policy/E1_experiment_acceptance.md`、`crypto_thesis/time-policy/第四章正式修订稿V1.2.md`（均公开可访问） |

## 4. Research Content 2 Current State

| 项目 | 当前事实 |
|---|---|
| status | `COMPLETED_WITH_VALID_RERUN_EVIDENCE`（V13 有效复跑）；第 5 章已定稿 |
| core method | AuthorizationState 合约 + CAP2（绑定 chainId、contractAddress、policyDigest、epoch、stateVersion、userVersion、userKeyId、operation、validity interval、Nonce）；Ed25519 签名；共享 PostgreSQL 原子 Nonce；重放拒绝；Fail-Closed |
| environment | 正式授权链 chainId `2026072901`：Besu 26.5.0、4 Validator + 1 非验证 RPC；PostgreSQL 16.14；AuthorizationState `0x9ef44cf538d0df457ba77c556d8785e48bfc436d`（artifact SHA `b8cd8040e4a7683fb4454ea1cf3c3c4d97647611ad7cb3d616b72a35cf496ad5`） |
| formal experiment | V13 复跑 `formal_auth_multihost_rerun_v13_20260729T073007Z_8a3d795`：108 因子配置 / 324 种子配置 / 9,720 run blocks / 77,760 请求 / 233,280 链读；requests SHA-256 `00dbdc62c21a7c12143394118df5dc00bbe7108d822a4af41bd6a96aa89cc4ce`；完整性 accepted=true |
| supported claims | 状态锚定、重放控制、Fail-Closed；链读主导时延（98.66%–98.80%）；并发为主要时延因素；碎片化仅影响本地匹配成本 |
| negative results | 缓存无稳定端到端收益（B1/C1 命中率 0.75/0.625，paired 差异 ~±2%，improved≈44%、degraded≈47%）；`C(P)` 无可用性能/协议优势（`REFUTED_AS_ADVANTAGE`） |
| limitations | 单次有效复跑边界；不宣称 QBFT 共识性能；不宣称联盟链为可信时间源/秘密执行环境 |
| invalidated assets | 首个 103,680 记录正式运行 `formal_auth_multihost_20260729_34af4ff` 因协议偏差被判定 `INVALIDATED_PROTOCOL_DEVIATION`（保留审计，不得引用为性能证据） |
| authoritative sources | 本地 raw（LOCAL_ONLY）：`crypto_thesis/epoch-authorization/experiments/runs/formal_auth_multihost_rerun_v13_20260729T073007Z_8a3d795/`；公开：`crypto_thesis/epoch-authorization/docs/reviews/research-content-2/v13-final/rc2-interface-manifest.json`、`crypto_thesis/epoch-authorization/docs/thesis-drafts/第5章_链上状态驱动的可信授权执行机制_最终定稿.md` |

> 为什么使用联盟链（RC2 动机）：在真实许可链（Besu QBFT）上锚定授权状态，获得可验证、
> 防重放、依赖故障下 Fail-Closed 的授权执行，并验证其代价（链读主导时延）。
> 联盟链**不是**绝对可信时间源、秘密执行环境、数据机密性来源或自动链下撤销机制。

## 5. Research Content 3 Current State

| 项目 | 当前事实 |
|---|---|
| status | `FORMAL_COMPLETED`（I9 Pilot → I10 预注册 → I11 Formal → I12 结果评审 → I13 章节写回 → I14-I17 全论文整合/文献/格式化）；RC3 论文章节已写入集成母本 |
| core method | 版本化密文头部（keyVersion/bodyVersion/headerVersion）；HEADER_ONLY 与 BODY_ROTATION 两种路径；前瞻性撤销（forward-looking）；RecoveryCoordinator 对象/服务故障恢复；PostgreSQL 任务状态（operationId、SKIP LOCKED、lease/CAS、COMMIT_UNKNOWN）；Kubo 副本；Fail-Closed |
| stack | HPKE provider；pyhpke 0.6.4；RFC 9180；AES-256-GCM；JCS；Ed25519；HeaderRegistry 合约；LocalObjectStore/Kubo |
| formal experiment | I11 Formal `FORMAL_20260802T095534Z_4d12daf`（执行 Git SHA `4d12daf`）：35 warmup + 145 measured RUNs（E1 20 / E2 30 / E3 45 / E4 10 / E5 40）；29 冻结配置；145/145 有效（120 VALID_SUCCESS + 25 VALID_EXPECTED_FAIL_CLOSED）；invalid/replacement/excluded 均为 0 |
| supported claims | C-01..C-06（状态一致与幂等、HEADER_ONLY/BODY_ROTATION 开销描述、撤销窗口 Fail-Closed、恢复一致性与规则化 Fail-Closed、Kubo 影响按正式块报告）均 SUPPORTED |
| negative results | E5：LOCAL vs KUBO 时长差异无清晰效应（median 17.5/-30.9/-48.3 ms，Cliff's delta 0.04）；CORRUPT_RESTORE 下 LOCAL 为 UNRECOVERABLE、KUBO_REPLICA 为 CONSISTENT（trade-off） |
| limitations | L-01..L-08：单节点 Formal 链（C-07 禁止 QBFT 共识性能结论）、29 配置有界精度、受控隔离环境、4 类故障、仅前瞻性撤销、body 64KiB–8MiB、实验验证非形式化证明 |
| forbidden claims | C-07：不产生 QBFT 共识吞吐/延迟/多验证节点可扩展性结论 |
| authoritative sources | 公开：`crypto_thesis/epoch-authorization-r3-prep/docs/research-content-3-implementation/i10/`（预注册）、`i11/`（formal-run-index.json、formal-config-matrix.json）、`i12/`（负结果/限制/claim 矩阵）；本地 raw（LOCAL_ONLY）：`crypto_thesis/epoch-authorization-r3-prep/experiments/r3/formal/` |

> 核心问题：授权状态变化后如何保证链下密文对象的安全释放，且只承诺前瞻性撤销。
> `HEADER_ONLY` = 仅更新密文头部（密钥版本/状态版本/释放窗口），数据体密文不变；
> `BODY_ROTATION` = 数据体密文重新封装（body 密钥轮换）。两者是分离的语义类，
> 不做跨语义“谁更快”的 winner 比较（RQ-2/RQ-3 严格分离）。

## 6. Formal Experiment State

**Pilot ≠ Formal。** 三组正式实验：

| 实验 | 类型 | 关键证据位置 |
|---|---|---|
| RC1 E1 | FORMAL | 本地 raw（LOCAL_ONLY）：`crypto_thesis/time-policy/experiments/runs/e1_20260727_ec8b193_r3/`（168 配置、15,120 记录；E1-C 补充 540 记录）；公开摘要：`crypto_thesis/time-policy/研究内容一E1正式实验报告V1.0.md` |
| RC2 V13 复跑 | FORMAL | 本地 raw（LOCAL_ONLY）：`crypto_thesis/epoch-authorization/experiments/runs/formal_auth_multihost_rerun_v13_20260729T073007Z_8a3d795/`（77,760 请求）；公开摘要：`crypto_thesis/epoch-authorization/docs/reviews/research-content-2/v13-final/` |
| RC3 I11 | FORMAL | 本地 raw（LOCAL_ONLY）：`crypto_thesis/epoch-authorization-r3-prep/experiments/r3/formal/`（180 sealed RUNs = 35 warmup + 145 measured）；公开摘要：`crypto_thesis/epoch-authorization-r3-prep/docs/research-content-3-implementation/i11/` + `i12/` |

明确区分：

- RC2 首个 103,680 记录运行：**INVALIDATED**（协议偏差），仅审计保留。
- RC3 I9 Pilot（93/93）：**PILOT_ONLY**，不构成正式结论。
- RC2 PILOT_ONLY（108 配置/3,780 记录）：**PILOT_ONLY**。

## 7. Frozen Negative Results

以下负结果已冻结，不得被后续模型“优化掉”或删除：

1. `C(P)` 无普遍压缩优势：对 `I*` 区间列表 0/108 更小、72/108 更大（RC1 E1）。
2. 任意碎片化策略无普遍 `O(log U)` 压缩结论（RC1）。
3. 缓存无稳定端到端性能收益（RC2 V13 paired 分析）。
4. `C(P)` 无已证实的 Baseline-I 不可用性能/协议优势（RC2）。
5. 逐请求链读主导端到端时延（98.66%–98.80%），局部优化影响被掩盖（RC2）。
6. E5 LOCAL vs KUBO 恢复时长差异无清晰效应（Cliff's delta 0.04）；Kubo 价值限于恢复来源可用性 trade-off（RC3）。
7. 实验验证不构成形式化安全证明；不变量成立限于所测配置（RC3 L-08）。

## 8. Forbidden Claims

以下主张在任何正式文本/报告中禁止：

- `C(P)` 普遍压缩优于区间列表；
- 缓存带来稳定性能收益；
- QBFT 共识吞吐/延迟/多验证节点可扩展性（C-07）；
- 追溯撤销（retroactive revocation）或追回已释放 CK/明文；
- 联盟链作为绝对可信时间源；
- 联盟链作为秘密执行环境；
- 联盟链自动解决链下密钥撤销；
- 联盟链提供数据机密性；
- 工程实验等价于密码学/形式化证明。

## 9. Thesis Writing State

| 维度 | 状态 | 权威 |
|---|---|---|
| Integrated thesis | I14 集成母本候选稿 `crypto_thesis/epoch-authorization-r3-prep/docs/thesis-integration/THESIS-INTEGRATED-MASTER-DRAFT-V1.md`（含中文摘要、第 1–7 章、参考文献） | I14 冻结（commit 807f788，见 COMMIT-LINEAGE.md） |
| Literature | I15 最终文献核验完成：16 篇参考文献全部核验（11 VERIFIED + 5 VERIFIED_WITH_CORRECTION），2 处 DOI 更正，coverage=MINIMALLY_SUFFICIENT | `crypto_thesis/epoch-authorization-r3-prep/docs/final-literature-verification/` |
| Formatting | I16 V1 格式候选 → I17 学术散文重构 + UESTC 官方封面/扉页与撰写规范应用 → `crypto_thesis/epoch-authorization-r3-prep/docs/final-manuscript/output/THESIS-FORMAT-CANDIDATE-V2.docx/.pdf`（55 页、16 图/16 表/209 公式/5 算法/16 文献）；**NOT SUBMISSION_READY**（MINOR 3 + 用户确认封面/致谢/成果占位） | `crypto_thesis/epoch-authorization-r3-prep/docs/final-manuscript/i17/i17-state.json` |

## 10. Midterm State

当前最终中期报告为 **FINAL-CLEAN 最终固化版**（`MIDTERM_REPORT_FINAL_FROZEN_READY_FOR_ADVISOR_REVIEW`）：

- 路径：`crypto_thesis/epoch-authorization-r3-prep/docs/midterm-report/final/FINAL-MIDTERM-SOURCE.md`（37 页，公开可访问）
- 规格：16 显示公式、8 算法、20 图、8 表、34 篇参考文献；FATAL=0、MAJOR=0、MINOR=1、format_only=2
- 产物：`crypto_thesis/epoch-authorization-r3-prep/docs/midterm-report/final/output/王威-专业学位研究生学位论文中期考评表-最终固化版.docx/.pdf`（docx SHA `E2EB7505…`、pdf SHA `4BF4E543…`）
- 待用户处理：确认“阶段性论文题目”（当前与本地两篇草稿标题不一致）；随后可提交导师/专家组评审

中期历史版本（M1–M7）保留于 `crypto_thesis/epoch-authorization-r3-prep/docs/midterm-report/` 供审计，不代表 CURRENT。

## 11. Small Paper State

状态：`P0_APPROVED_NOT_YET_EXECUTED`

- currentTask：`NOVELTY_SEARCH_TOPIC_SCOPING_AND_PUBLICATION_BLUEPRINT`
- scope：从当前冻结 RC1、RC2、RC3 成果中切割一篇具有独立研究问题和实验闭环的学术期刊论文；
  优先候选为 **RC3 + RC2 必要授权状态机制**，但尚未通过真实文献创新性审查，
  因此**不得提前冻结最终选题**。
- 仓库内尚无 P0 正式产物（不虚构其已执行完成）；中期表“阶段性成果”仍声明拟投《软件学报》+ 2 项专利计划。

## 12. Current Next Action

**唯一 CURRENT NEXT ACTION：小论文 P0 —— 创新性检索、选题切割与投稿蓝图冻结**

执行序列：项目事实恢复 → 2021 年至今真实联网文献检索 → Tier-1 竞争文献识别 →
机制比较矩阵 → 候选 A/B/C/D 比较 → Claim-Evidence 审查 → 实验复用/补实验判断 →
投稿方向评估 → `SMALL-PAPER-BLUEPRINT-V1`。

行政待办与科研动作分离：

- parallelAdministrativeActions：中期报告 FINAL-CLEAN 送导师/专家组审核（非科研动作，不阻塞 P0）
- deferredActions：学位论文 I17 → submission-ready 最终定稿（延后处理，非当前首要科研动作）

不将 M2/M7 修订、I11 等待、RC2 formal rerun、中期送审、论文定稿作为 CURRENT NEXT ACTION。

## 13. Authority Map

完整映射见 [AUTHORITY-MAP.md](AUTHORITY-MAP.md)。最高原则：

真实代码/正式实验 raw/冻结索引 > 最新冻结证据/正式报告 > 最新论文集成稿 > 项目治理文件 > 历史蓝图 > README/聊天摘要。

遇到冲突时，按此顺序裁决，并保留历史文档为 SUPERSEDED/HISTORICAL，不删除。
