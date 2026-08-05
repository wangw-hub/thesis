# Current State

Updated: 2026-08-05（治理同步）

> 本文件是子项目级 CURRENT 状态。仓库级唯一当前状态入口为根目录
> `docs/project-governance/CURRENT-SNAPSHOT.md`；本文件不再包含历史的流水账，
> 历史里程碑见本文件末尾与各迭代文档。

## Git

- 本工作树为 epoch-authorization 的 linked worktree，HEAD `29d822f`。
- I11 正式执行 Git SHA：`4d12daf`；FINAL-CLEAN 中期冻结 head：`4807a4e`。
- 完整历史保留于 `D:\Research\.git-backups\`（未上传，见 COMMIT-LINEAGE.md）。

## Research Content 1

Status: `COMPLETED_WITH_SCOPE_ADJUSTMENT`。`I*` 为唯一语义与 digest 主表示；
`C(P)` 为确定性可选执行 IR / ablation 对象。E1 正式实验 168 配置 / 15,120 记录；
E1-C 补充 540 记录；E2 复验 81 项通过、覆盖率 98.61%。

## Research Content 2

Status: `COMPLETED_WITH_VALID_RERUN_EVIDENCE`（V13 有效复跑；第 5 章已定稿）。

- 正式授权链 chainId `2026072901`（Besu 26.5.0，4 Validator + 1 RPC），Genesis SHA `7d431f01…`。
- AuthorizationState `0x9ef44cf538d0df457ba77c556d8785e48bfc436d`（artifact SHA `b8cd8040…`）。
- V13 复跑：108 因子 / 324 种子 / 9,720 run blocks / 77,760 请求 / 233,280 链读；
  requests SHA `00dbdc62…`；完整性 accepted=true；语义差异/攻击误收/Nonce 重复成功 = 0。
- 首轮 103,680 记录运行 `INVALIDATED_PROTOCOL_DEVIATION`，仅审计保留。

## Research Content 3

Status: `FORMAL_COMPLETED`（I9–I17 全部完成；RC3 章节已写入集成母本）。

- I9 Pilot：93/93 接受（PILOT_ONLY，IMMUTABLE_PILOT_BASELINE）。
- I10 预注册：29 配置 / 145 measured planned（digest `5c957cdf…`）。
- I11 Formal：`FORMAL_20260802T095534Z_4d12daf`（执行 SHA `4d12daf`）；35 warmup +
  145 measured（E1 20 / E2 30 / E3 45 / E4 10 / E5 40）；145/145 有效
  （120 VALID_SUCCESS + 25 VALID_EXPECTED_FAIL_CLOSED）；wrong release=0；
  state-consistency violations=0；raw/mirror SHA errors=0。
- I12 结果评审、I13 章节写回、I14 全论文终审、I15 文献核验、I16/I17 格式化候选均完成。

## Writing / Midterm

- 集成母本：`docs/thesis-integration/THESIS-INTEGRATED-MASTER-DRAFT-V1.md`（I14）。
- 文献：I15 COMPLETED（16 篇核验，2 处 DOI 更正）。
- 格式化：I17 V2 候选（55 页，官方 UESTC 模板已应用）；**NOT SUBMISSION_READY**
  （MINOR 3 + 用户确认封面/致谢/成果）。
- 中期：**FINAL-CLEAN 最终固化版**（37 页、16 式、8 算法、20 图、8 表、34 文献），
  `MIDTERM_REPORT_FINAL_FROZEN_READY_FOR_ADVISOR_REVIEW`；路径
  `docs/midterm-report/final/FINAL-MIDTERM-SOURCE.md`。

## Current Hard Stop

无（RC2 首轮运行偏差已由 V13 复跑解决；`HS-FUNDING-001` 已由独立正式链决议解决）。

## Small Paper / Current Next Action

- smallPaper.status：`P0_APPROVED_NOT_YET_EXECUTED`
- currentTask：`NOVELTY_SEARCH_TOPIC_SCOPING_AND_PUBLICATION_BLUEPRINT`
- **CURRENT NEXT ACTION：小论文 P0 —— 创新性检索、选题切割与投稿蓝图冻结**（尚未生成正式产物）
- parallelAdministrativeActions：中期报告 FINAL-CLEAN 送导师/专家组审核
- deferredActions：学位论文 I17 → submission-ready 最终定稿

## Restrictions

- 不修改正式实验 raw / 预注册 / 结果包；不把 PILOT_ONLY 当 Formal；不 push。
- 新会话必须从根 `docs/project-governance/CURRENT-SNAPSHOT.md` 与 AUTHORITY-MAP.md 开始恢复上下文。

## Historical Milestones（不再代表 CURRENT）

- 2026-07-29：RC3 尚未开始；RC2 首轮运行因协议偏差被判定 INVALIDATED（当时要求完整复跑，后由 V13 完成）。
- 2026-07-29/30：V13 预注册与复跑、RC2 关闭（epoch-authorization 项目）。
- 2026-08-02：I9–I17 完成（RC3）。
- 2026-08-03：M2 中期候选（被 M3–M7 取代）。
- 2026-08-04：M7 → FINAL-CLEAN 中期冻结。
