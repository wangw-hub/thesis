# AUTHORITY MAP — 每类事实的唯一最高权威来源（双权威模式）

> 用途：禁止未来模型自行猜测哪个文档更权威。本表为每类事实指定唯一绝对权威（Absolute Authority）、
> 可用性（Availability）、公开 GitHub 权威/回退（Public GitHub Authority / Fallback）与状态（Status）。
>
> 路径均为 **wangw-hub/thesis 仓库根相对路径**（repository-root-relative）。
> `LOCAL_ONLY` 表示该资源未上传 GitHub，只能在本机 `D:\Research` 访问；
> 公开模式下必须使用 Public fallback，不得臆造 raw 内容。
> 若某结论仅有 local raw 且无公开 summary/report，则登记 `PUBLIC_EVIDENCE_GAP`，不得伪造 fallback。

| Information | Absolute Authority | Availability | Public GitHub Authority / Fallback | Status |
|---|---|---|---|---|
| 仓库当前状态总入口 | `docs/project-governance/CURRENT-SNAPSHOT.md` | PUBLIC | 同左（绝对权威即公开） | CURRENT |
| 事实裁决顺序 | CURRENT-SNAPSHOT §13 优先级 | PUBLIC | 同左 | CURRENT |
| 公开模式恢复步骤 | `docs/project-governance/AI-CONTEXT-RECOVERY.md`（MODE B） | PUBLIC | 同左 | CURRENT |
| RC1 最终方法 | `crypto_thesis/time-policy/第四章正式修订稿V1.2.md` + `crypto_thesis/time-policy/src/time_policy/` 源码 | PUBLIC | 同左（第四章定稿为最终方法权威） | CURRENT |
| RC1 E1 raw | `crypto_thesis/time-policy/experiments/runs/e1_20260727_ec8b193_r3/`（168 配置/15,120 记录） | LOCAL_ONLY | `crypto_thesis/time-policy/研究内容一E1正式实验报告V1.0.md` + `crypto_thesis/time-policy/E1_experiment_acceptance.md`（正式结论/验收摘要） | CURRENT |
| RC1 负结果/验收 | `crypto_thesis/time-policy/E1_experiment_acceptance.md`、`crypto_thesis/time-policy/研究内容一最终关闭报告.md` | PUBLIC | 同左 | CURRENT |
| RC2 最终协议/接口 | `crypto_thesis/epoch-authorization/docs/reviews/research-content-2/v13-final/rc2-interface-manifest.json` + `rc2-claim-manifest.json` | PUBLIC | 同左 | CURRENT |
| RC2 V13 raw | `crypto_thesis/epoch-authorization/experiments/runs/formal_auth_multihost_rerun_v13_20260729T073007Z_8a3d795/` | LOCAL_ONLY | `crypto_thesis/epoch-authorization/docs/reviews/research-content-2/v13-final/`（claim/interface/final decision）+ `crypto_thesis/epoch-authorization/docs/thesis-drafts/第5章_链上状态驱动的可信授权执行机制_最终定稿.md` | CURRENT |
| RC2 负结果（性能） | V13 `analysis/independent-analysis-summary.json`（本地） | LOCAL_ONLY | 第五章定稿 + `crypto_thesis/epoch-authorization/docs/project-governance/04-CLAIM-EVIDENCE-MATRIX.md`（性能边界行） | CURRENT |
| RC2 无效运行 | `crypto_thesis/epoch-authorization/experiments/runs/formal_auth_multihost_20260729_34af4ff/` | LOCAL_ONLY | `crypto_thesis/epoch-authorization/docs/project-governance/05-EXPERIMENT-REGISTRY.md`（INVALIDATED 行） | SUPERSEDED/INVALIDATED |
| RC3 协议/设计 | `crypto_thesis/epoch-authorization-r3-prep/docs/research-content-3-implementation/`（i0–i8 设计 + i10 预注册） | PUBLIC | 同左 | CURRENT |
| RC3 I9 Pilot | `crypto_thesis/epoch-authorization-r3-prep/experiments/r3/i9-pilot/final-analysis/i9-run-index.json` | LOCAL_ONLY | `crypto_thesis/epoch-authorization-r3-prep/docs/research-content-3-implementation/` 中 I9 决策/审计文档 + `crypto_thesis/epoch-authorization-r3-prep/docs/project-governance/05-EXPERIMENT-REGISTRY.md` | CURRENT（PILOT_ONLY） |
| RC3 I10 预注册 | `crypto_thesis/epoch-authorization-r3-prep/docs/research-content-3-implementation/i10/` | PUBLIC | 同左 | CURRENT |
| RC3 I11 Formal raw | `crypto_thesis/epoch-authorization-r3-prep/experiments/r3/formal/raw/`（180 sealed RUNs） | LOCAL_ONLY | `crypto_thesis/epoch-authorization-r3-prep/docs/research-content-3-implementation/i11/formal-run-index.json` + `formal-config-matrix.json` | CURRENT |
| RC3 正式结果 | `crypto_thesis/epoch-authorization-r3-prep/docs/research-content-3-implementation/i12/`（formal-claim-evidence-matrix、formal-negative-results、formal-limitations、i12-state） | PUBLIC | 同左 | CURRENT |
| RC3 论文章节 | `crypto_thesis/epoch-authorization-r3-prep/docs/research-content-3-implementation/i13/THESIS-RC3-WRITEBACK-FINAL.md` | PUBLIC | 同左 | CURRENT |
| 全论文集成母本 | `crypto_thesis/epoch-authorization-r3-prep/docs/thesis-integration/THESIS-INTEGRATED-MASTER-DRAFT-V1.md` + `INTEGRATED-THESIS-SOURCE-MAP.json` | PUBLIC | 同左 | CURRENT |
| 主稿/源文件 | `crypto_thesis/epoch-authorization-r3-prep/docs/final-manuscript/MASTER-SOURCE.md` | PUBLIC | 同左 | CURRENT |
| 文献核验 | `crypto_thesis/epoch-authorization-r3-prep/docs/final-literature-verification/`（I15） | PUBLIC | 同左 | CURRENT |
| 格式/排版状态 | `crypto_thesis/epoch-authorization-r3-prep/docs/final-manuscript/i17/i17-state.json` | PUBLIC | 同左 | CURRENT |
| 中期报告 | `crypto_thesis/epoch-authorization-r3-prep/docs/midterm-report/final/FINAL-MIDTERM-SOURCE.md` + `final-midterm-state.json` | PUBLIC | 同左 | CURRENT |
| 小论文状态 | `docs/project-governance/current-project-state.json`（smallPaper 段） | PUBLIC | 同左 | CURRENT（P0_APPROVED_NOT_YET_EXECUTED） |
| 实验数据清单 | `docs/project-governance/EXPERIMENT-DATA-MANIFEST.md` | PUBLIC（清单本体） | 同左；raw 均为 LOCAL_ONLY | CURRENT |
| Git 提交谱系 | `docs/project-governance/COMMIT-LINEAGE.md`（外层） + `D:\Research\.git-backups\`（子项目历史） | 外层 PUBLIC；子项目历史 LOCAL_ONLY | COMMIT-LINEAGE.md（外层里程碑）；子项目历史仅 VERIFIED_LOCAL_HISTORY | CURRENT |
| 密钥/敏感材料 | 不版本化：`SECRET_MATERIAL_NOT_VERSIONED` | LOCAL_ONLY（禁止上传） | 无（禁止公开） | CURRENT |

## PUBLIC_EVIDENCE_GAP 登记

经核对，三项研究内容的每个核心正式结论均存在至少一个公开 summary/report/index：

- RC1：E1 正式报告 + 验收（公开）覆盖全部结论；raw 图 4-2..4-5 为 LOCAL_ONLY（见 PUBLIC-FIGURE-INDEX.md）。
- RC2：v13-final claim/interface manifest + 第五章定稿（公开）覆盖结论；V13 raw 与独立分析 JSON 为 LOCAL_ONLY。
- RC3：I10 预注册 + I11 run/config index + I12 结果包（公开）覆盖结论；raw 与 i12-final 图为 LOCAL_ONLY。

**PUBLIC_EVIDENCE_GAP = 0**（无“只有 local raw、无公开 summary”的核心结论）。

## 裁决规则

1. 冲突时按 CURRENT-SNAPSHOT §13 优先级裁决；CURRENT 只允许一个。
2. PUBLIC_GITHUB_MODE 遇到 LOCAL_ONLY 证据：用本表 Public fallback，明确说明 raw 未公开，不猜测。
3. HISTORICAL/SUPERSEDED 文件保留原样，通过本表与 SUPERSEDED-DESIGNS.md 外部标记。
4. 正式实验 raw/预注册/结果包为冻结资产：发现内部错误登记 `FROZEN_ASSET_ISSUE`，不直接修改。
