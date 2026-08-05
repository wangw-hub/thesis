# R3 I11 Context Recovery

任务：`R3_I11_CONTEXT_RECOVERY`

恢复时间：2026-08-02（Asia/Shanghai）

本文件仅从 Git 仓库、I9 冻结证据与 I10 冻结资产重建会话上下文。未执行 I11，未创建任何 Formal attempt/run/raw，未修改任何冻结文件，未 push。

## 1. Git 上下文

| 项 | 值 |
|---|---|
| Repo root | `D:\Research\crypto_thesis\epoch-authorization-r3-prep` |
| Branch | `research-content-3-preparation` |
| Current HEAD | `2bf56d2de4245707a2db837cc4846ac63afd9904` |
| HEAD 与 I10 冻结提交 | 一致（`2bf56d2 docs(r3): freeze i10 formal design and preregistration`） |
| Working tree | 干净（无未提交改动） |
| 主仓库 | `D:\Research\crypto_thesis\epoch-authorization` @ `dac2234`（master），未修改 |
| Worktree 关系 | 主仓库 master `dac2234`；r3-prep worktree 独立于 `research-content-3-preparation` |

## 2. RC1 / RC2 / RC3 状态

- RC1（研究内容一，非连续时间约束策略的确定性表示与编译）：冻结，`I*` 为主语义表示，`C(P)` 为可再生成派生 IR，不主张普适压缩优势。
- RC2（研究内容二，基于许可联盟链的可信授权执行）：冻结，不得为 I11 修改 `AuthorizationState`、CAP2、正式 Besu 网络、PostgreSQL 或合约资产。
- RC3（研究内容三，版本化密文头部与前瞻性撤销闭环）：当前推进内容；只主张 `FORWARD_LOOKING_REVOCATION_ONLY`，Fail-Closed，不主张追溯撤销/收回明文/删除历史数据。

## 3. I9 冻结基线

- 状态：`I9_COMPLETED_AWAITING_I10_APPROVAL`（I10 已执行，I9 为不可变 Pilot 基线）。
- Accepted：P9-A 8/8、P9-B 45/45、P9-C 16/16、P9-D 24/24，总计 **93/93**（`i9-run-index.json`：`actualTotal=93`、`uniqueRunIds=93`、`validTotal=93`、`strictEvidenceErrors=0`、`rawShaErrors=0`）。
- 结果索引：`experiments/r3/i9-pilot/final-analysis/i9-run-index.json`（实际读取，逐行 valid=true）。
- Pairing Smoke：PASS；Statistical Smoke：PASS（unit=RUN）。
- I9 baseline digest：`6de936e9d7ef8357530b7361e0b06a862c0474212e1147b69f5dd67fc4779d8a`（在 `01-I9-FROZEN-BASELINE.md`、`formal-preregistration.json`、`i10-state.json`、`00-I10-ENTRY.md` 中一致）。
- 边界：所有 I9 统计仅为 `PILOT_STATISTICAL_SMOKE_ONLY` / `NOT_FOR_FORMAL_THESIS_RESULTS` / `NOT_FOR_PERFORMANCE_CLAIMS`；Pilot timing 不得写成正式结果。
- 安全证据：`strict-review.json` 显示 trueSecret=0、unclassified=0、fatal=0、major=0、minor=0、formalChainAccess=0、validatorAccess=0、postgres16MainAccess=0。

## 4. I10 冻结资产核验

- 目录：`docs/research-content-3-implementation/i10/`，37 份 Markdown + 11 份 JSON，全部存在。
- 完整性：`artifact-sha256.json` 共 47 项，逐项 SHA-256 实算比对 **0 mismatch**。
- `i10-state.json`：`I10_COMPLETED_AWAITING_I11_APPROVAL`；`formalAttemptCreated=false`、`formalDataCollected=false`、`formalPerformanceConclusion=false`、`formalDatabaseCreated=false`、`formalKuboCreated=false`、`rc3MultiNodeFormalRequired=false`、`formalTopology=DESIGNED_NOT_DEPLOYED`、`i11=READY_AWAITING_USER_APPROVAL`；fatal/major/minor=0，pseudoreplication=0。
- 预注册：`formal-preregistration.json` 状态 `DESIGN_FROZEN_AWAITING_I11_APPROVAL`；文件 SHA-256 = `1bd568be1c4ac382aac6ef178920e853f63ba89c50abb424737c3d1dd0417b47`（与清单一致）；文件内声明 canonical `preregistrationDigest = 5c957cdf7f4269cec58842c4536ad1f4fc73424da01c5a3a1ab1461fbe8fc45f`。
- 审计：`34-I10-STRICT-REVIEW.md` 全项通过；`35-I10-FINAL-DECISION.md` 确认唯一下一步为用户批准 I11。
- 额外 JSON：`formal-besu-topology.json`（DESIGNED_NOT_DEPLOYED）、`formal-environment-fingerprint-template.json`（TEMPLATE_NOT_COLLECTED）均与摘要一致。
- 只读审计说明：`experiments/runs/formal_auth_multihost_20260729_34af4ff/` 为 2026-07-29 的历史运行目录（RC2 时期资产，含自身 manifest/reports），不是 I10 analysis code skeleton，未将其当作 Formal raw。`experiments/r3/` 下无任何 Formal attempt/run/raw 目录。

## 5. Formal 设计要点（从冻结资产恢复）

- Formal RQ：6 个（RQ-1～RQ-6），文本与 `formal-rq-matrix.json` 一致。
- Formal Claim：7 个（C-01～C-07）；**C-07 明确 FORBIDDEN**（不声称 QBFT 共识吞吐/延迟/多验证节点可扩展性），无对应实验。
- Baseline：保留 **Baseline-R**（LOCAL_ONLY 匹配块）；Baseline-H 已删除（不公平）；Baseline-U 未冻结。
- Factors：8 类冻结（recipient_count 2/8/32、affected_count 1/4、body_bytes 65536/1048576/8388608、update_kind HEADER_ONLY/BODY_ROTATION、replica_state LOCAL_ONLY/KUBO_REPLICA、fault_class NONE/CORRUPT_RESTORE/CID_MISMATCH/BOTH_MISSING、workload_type 4 类、concurrency 1/4），分块设计非全笛卡尔积。
- Metrics：12 个（M-01～M-12），不得自行增删。
- 实验单位：**RUN**（phase/transaction/request/recipient/chunk/event 均非独立样本）。
- 样本量：29 configs × 5 reps = 145 measured + 35 warmups（29 per-config + 6 environment）= 180 总计划 RUN；预计 4 小时（2～8 小时工程估计）；`POWER_ANALYSIS_NOT_JUSTIFIED`。
- 随机化：分块确定性随机化，seed `20260802`，block keys = semantic_class/experimentId/configuration_digest。
- Pairing：key = `generatorVersion|semanticClass|inputDigest|seed|configurationDigest`；仅同语义配对；禁止 HEADER_ONLY vs BODY_ROTATION 等价比较；禁止 timing-neighbor pairing。
- 统计：RUN 单位；bootstrap 10000 次（RUN 重采样）；95% percentile CI；median difference / ratio(log transform) / Cliff's delta；Holm correction（每个 RQ family 内）。
- 策略：failure 分类（protocol/security/infrastructure/workload/measurement）；exclusion 必须记录、禁止静默删除、禁止 timing-based 删除；replacement 仅限预注册基础设施规则且保留原失败记录并新建 RUN identity；stop rules 含 10 类立即停止条件。
- RC3 多节点：`RC3_MULTI_NODE_FORMAL_REQUIRED=false`；F3 拓扑（4 Validator + 1 RPC/client）仅 DESIGNED_NOT_DEPLOYED，未来也需独立 genesis/chainId/keys/端口/证据根，禁止复用 r3_i5 Pilot 链（2026073005）与 RC2 链。
- Formal 环境：F1 隔离功能验证、F2 单 RPC 端到端（未来独立 Formal 链）、F3 多节点 QBFT（不为 RC3 主张）、F4 受控故障/恢复；每个环境需完整 `R3FormalEnvironmentFingerprintV1`。
- Formal PostgreSQL / Kubo / Identity：均已设计、尚未创建；禁止复用 Pilot DB/Kubo/attemptId/runId/RC2 身份；`Formal != Pilot`。
- Optional Enhanced：未启用，禁止自动执行；启用需书面 Protocol Amendment + 用户批准。

## 6. I11FormalExecutionPlanV1（从 I10 冻结资产恢复）

计划 ID：`I11FormalExecutionPlanV1`（仅恢复，不改设计）。

| Experiment | RQ | 覆盖 | Configs | Measured runs |
|---|---|---|---|---|
| E1 | RQ-1 | 正确性/状态闭合（各语义类内嵌入），F1/F2，Baseline=same-task replay control | 4 | 20 |
| E2 | RQ-2 | HEADER_ONLY：recipient_count 2/8/32 × affected_count 1/4，F2，within-class fixed-size control | 6 | 30 |
| E3 | RQ-3 | BODY_ROTATION：body_bytes 64KiB/1MiB/8MiB × recipient_count 2/8/32，F2，within-class fixed-body control | 9 | 45 |
| E4 | RQ-4 | 预先撤销：current-header + post-event controls，F1/F2，no-revocation control | 2 | 10 |
| E5 | RQ-5/RQ-6 | 恢复：LOCAL_ONLY/KUBO_REPLICA × NONE/CORRUPT_RESTORE/CID_MISMATCH/BOTH_MISSING，F4，Baseline-R | 8 | 40 |

合计：29 configs / 145 measured / 35 warmups / 180 total；metrics M-01～M-12；执行顺序由 seed 20260802 分块确定性随机化生成并在采集前冻结。

批准后建议执行阶段（与冻结文档一致）：

- Phase 0：I11 entry audit（批准核验、prereg digest 复核、readiness gate）。
- Phase 1：Formal 环境供给（独立 PostgreSQL 按 20、独立 Kubo 按 21、最小 F2 链按 18/19；F3 不部署）。
- Phase 2：Formal 环境证明（`R3FormalEnvironmentFingerprintV1`、字节码/依赖锁 digest）。
- Phase 3：Formal 代码/分析冻结（新 Git SHA、依赖锁、合约字节码、generator digest、analysis-code digest、快照清单；本地合成测试）。
- Phase 4：Formal preflight（身份新鲜度、独立环境、工厂来源、chainId、无公共 peers、secret 边界、确定性 generator、时钟、evidence-writer 就绪；fail-closed）。
- Phase 5：warm-up（35 runs，WARMUP_ONLY，不计统计）。
- Phase 6：measured E1-E5（145 runs，RUN 级严格证据）。
- Phase 7：raw 密封/镜像（远端权威 + 本地只读镜像 + 逐文件 SHA-256 清单）。
- Phase 8：严格验收（execution → seal → SHA → strict evidence → invariant/material-release review；按预注册 exclusion/failure/replacement 规则）。
- Phase 9：Formal 统计（RUN 单位、bootstrap 10000、95% percentile CI、median diff/ratio/Cliff's delta、Holm）。
- Phase 10：Formal 图表（仅描述性；禁止跨语义合并；环境指纹表）。

## 7. 结论

- I10 设计缺陷：无（当前未发现）。
- Protocol Amendment：不需要。
- 唯一缺失：`USER_I11_APPROVAL`。
- 状态停在：`I10_COMPLETED_AWAITING_I11_APPROVAL`。
