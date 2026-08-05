# AUTHORITY MAP — 每类事实的唯一最高权威来源

> 用途：禁止未来模型自行猜测哪个文档更权威。本表为每类事实指定唯一最高权威（CURRENT），并标注
> HISTORICAL（历史事实，不再代表现状）与 SUPERSEDED（已被取代）。
> 本表路径均相对仓库根 `D:\Research`；本地完整资料范围见 LOCAL-VS-PUBLIC-ASSETS.md。

| 信息类别 | CURRENT 权威 | HISTORICAL / SUPERSEDED | 备注 |
|---|---|---|---|
| 仓库当前状态总入口 | `docs/project-governance/CURRENT-SNAPSHOT.md` | 各项目旧 `01-CURRENT-STATE.md` 中过时行 | 新会话先读本入口 |
| 事实裁决顺序 | 代码/raw/冻结索引 > 冻结证据 > 正式报告 > 治理文件 > 蓝图 > README | — | 见 CURRENT-SNAPSHOT §13 |
| RC1 最终方法 | `crypto_thesis/time-policy/第四章正式修订稿V1.2.md` + `src/time_policy/` 源码 | 第四章 V1.0/V1.1 草稿（HISTORICAL） | `I*` 主表示、`C(P)` 派生 IR |
| RC1 正式实验数据 | `crypto_thesis/time-policy/experiments/runs/e1_20260727_ec8b193_r3/`（168 配置/15,120 记录）+ `研究内容一E1正式实验报告V1.0.md` | pilot_20260727_*（PILOT_ONLY） | E1-C 补充在 `e1c_power2_supplement_20260727_87d0010/`（540 记录） |
| RC1 验收/负结果 | `E1_experiment_acceptance.md`、`E1-C补充实验验收报告.md`、`研究内容一最终关闭报告.md` | 早期“C(P) 压缩优势”表述（SUPERSEDED） | 负结果必须保留 |
| RC2 最终协议/接口 | `crypto_thesis/epoch-authorization/docs/reviews/research-content-2/v13-final/rc2-interface-manifest.json` + `rc2-claim-manifest.json` | 研究内容二技术设计 V1.0（SUPERSEDED 于 V1.1/v13） | CAP2 绑定字段以其为准 |
| RC2 正式实验（有效） | `crypto_thesis/epoch-authorization/experiments/runs/formal_auth_multihost_rerun_v13_20260729T073007Z_8a3d795/`（manifest + analysis + raw） | 首轮 `formal_auth_multihost_20260729_34af4ff`（103,680 记录，SUPERSEDED/INVALIDATED） | 唯一可引用正式性能证据 |
| RC2 环境/链 | `infra/besu-qbft-multihost/formal-authorization-chain/`（chainId 2026072901）、genesis SHA `7d431f01…` | chainId 2026072801 基础设施链（HISTORICAL，验收保留） | 不得混用两条链 |
| RC2 负结果 | V13 `analysis/independent-analysis-summary.json`（链读占比、paired 比较） | 早期缓存/C(P) 有利表述（SUPERSEDED） | 缓存无稳定收益、C(P) 无优势 |
| RC2 论文章节 | `crypto_thesis/epoch-authorization/docs/thesis-drafts/第5章_链上状态驱动的可信授权执行机制_最终定稿.md` | 早期第五章草稿（HISTORICAL） | 基于 V13 有效证据 |
| RC3 协议/设计 | `crypto_thesis/epoch-authorization-r3-prep/docs/research-content-3-implementation/`（i0–i8 设计迭代 + i10 预注册） | 早期自研 ABE/门限解封装路线（SUPERSEDED，见 SUPERSEDED-DESIGNS.md） | 以 HPKE/RFC 9180 标准组件为准 |
| RC3 Pilot（非正式） | `experiments/r3/i9-pilot/final-analysis/i9-run-index.json`（93/93，PILOT_ONLY） | — | 不构成正式结论 |
| RC3 正式预注册 | `docs/research-content-3-implementation/i10/`（29 配置/145 planned；digest `5c957cdf…`） | — | 冻结，不可改 |
| RC3 正式 raw | `experiments/r3/formal/raw/`（180 sealed RUNs） | — | 只读冻结 |
| RC3 正式结果 | `docs/research-content-3-implementation/i12/`（formal-run-index、claim/负结果/限制 JSON、thesis-ready-result-dataset.json） | — | 145/145 有效、C-07 FORBIDDEN |
| RC3 论文章节 | `docs/research-content-3-implementation/i13/THESIS-RC3-WRITEBACK-FINAL.md` | — | 已并入集成母本 |
| 全论文集成母本 | `docs/thesis-integration/THESIS-INTEGRATED-MASTER-DRAFT-V1.md` + `INTEGRATED-THESIS-SOURCE-MAP.json`（I14） | 旧“论文实施蓝图”等（HISTORICAL/PLAN） | 正文权威以冻结章节源为准 |
| 主稿/源文件 | `docs/final-manuscript/MASTER-SOURCE.md`（I17 source of truth；SHA `FBB24BFF…`） | I16 V1 候选（SUPERSEDED by V2） | 格式化状态见 `i17-state.json` |
| 文献核验 | `docs/final-literature-verification/`（I15：16 篇核验、2 DOI 更正） | `thesis_literature_verified_2026-07-30/`（07-30 旧包，HISTORICAL） | 论文以 I15 为准 |
| 格式/排版状态 | `docs/final-manuscript/i17/i17-state.json`（OFFICIAL_TEMPLATE_APPLIED；NOT SUBMISSION_READY） | `final-manuscript-state.json`（I16 AWAITING_OFFICIAL_TEMPLATE，SUPERSEDED） | 用户确认封面/致谢/成果后定稿 |
| 中期报告 | `docs/midterm-report/final/FINAL-MIDTERM-SOURCE.md` + `final-midterm-state.json`（FINAL-CLEAN，37 页） | docs/midterm-report/m1..m7（HISTORICAL） | 唯一 CURRENT 中期版本 |
| 小论文/传播计划 | 无仓库内权威（NOT_STARTED_AS_REPO_WORK）；中期表“阶段性成果”声明拟投《软件学报》+ 2 专利 | — | 不得把计划当产物 |
| 正式实验索引/完整性 | 各正式运行目录内 `formal-*-sha256.json` / `manifest` / `analysis` 文件 | — | 本地完整清单见 EXPERIMENT-DATA-MANIFEST.md |
| Git 历史 | `docs/project-governance/COMMIT-LINEAGE.md` + `D:\Research\.git-backups\` | — | 外层仓库仅含单次归档提交 |
| 密钥/敏感材料 | 不版本化：`SECRET_MATERIAL_NOT_VERSIONED`（见 LOCAL-VS-PUBLIC-ASSETS.md） | — | 禁止写入清单正文 |

## 裁决规则

1. 同一事实出现冲突时，按 CURRENT-SNAPSHOT §13 的优先级裁决。
2. 只有带 `source` 的结论可进入 `current-project-state.json` 的 CURRENT 字段。
3. HISTORICAL/SUPERSEDED 文件保留原样（审计价值），通过本表与 SUPERSEDED-DESIGNS.md 外部标记。
4. 正式实验 raw、预注册、结果包为冻结资产：发现内部错误时登记 `FROZEN_ASSET_ISSUE`，不得直接修改。
