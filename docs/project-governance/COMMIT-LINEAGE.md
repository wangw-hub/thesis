# COMMIT LINEAGE — 重要 Git 提交谱系

> 说明：本表登记外层归档仓库的治理里程碑与三个子项目的重要提交谱系。
> 三个子项目的完整历史仅保存在本地 `D:\Research\.git-backups\`（LOCAL_ONLY），
> 可通过 `git --git-dir=... log` 解析；可解析的标记 `VERIFIED_LOCAL_HISTORY`，
> 仅来自文档的标记 `DOCUMENTED_ONLY`。
>
> **本表不声明任何 SHA 为“当前 HEAD”**。实时仓库 HEAD 应从 GitHub `main` 分支或本地 git
> 动态读取；静态治理文件只保留 `snapshotBasisHead`（生成快照时的已确认提交）。

## RC1 — time-policy（`D:\Research\.git-backups\time-policy.git`）

| 阶段 | commit SHA | 日期 | 含义 | 对应证据 | 可解析 | 状态 |
|---|---|---|---|---|---|---|
| 实现 | 4103b4f | 2026-07-27 | 实现 time-policy 编译器与 E1 实验框架 | `src/time_policy/` | VERIFIED_LOCAL_HISTORY | SUPERSEDED（早期） |
| E1 测量 | ec8b193 | 2026-07-27 | E1 正式实验峰值内存测量（报告冻结提交） | E1 正式实验报告 | VERIFIED_LOCAL_HISTORY | CURRENT |
| E1 报告/验收 | d42be29 | 2026-07-27 | 可复现 E1 报告与验收产物 | E1_experiment_acceptance.md | VERIFIED_LOCAL_HISTORY | CURRENT |
| 第四章草稿/审稿 | fc0c840 | 2026-07-27 | 第四章草稿与审稿 | 第四章修订系列 | VERIFIED_LOCAL_HISTORY | HISTORICAL |
| E1-C 补充 | 87d0010 | 2026-07-27 | 二次幂边界工作量（E1-C） | E1-C 补充实验报告（540 记录） | VERIFIED_LOCAL_HISTORY | CURRENT |
| 第四章收口 | 7bd3c68 | 2026-07-27 | 补充实验与引用后关闭第四章技术工作 | 第四章 V1.2 | VERIFIED_LOCAL_HISTORY | CURRENT |
| 导师确认 | 9fcdf30 | 2026-07-28 | 纳入导师条件性批准（I* 主表示） | 研究内容一最终关闭报告 | VERIFIED_LOCAL_HISTORY | CURRENT |

## RC2 — epoch-authorization（`D:\Research\.git-backups\epoch-authorization.git`）

| 阶段 | commit SHA | 日期 | 含义 | 对应证据 | 可解析 | 状态 |
|---|---|---|---|---|---|---|
| 协议修复 | 9b07fff | 2026-07-29 | 修正正式授权采集协议 | 严格审稿报告 | VERIFIED_LOCAL_HISTORY | CURRENT（修复基线） |
| V2–V13 预注册 | 462b6c9..8a3d795 | 2026-07-29 | 逐版修正预注册（v13 为 `8a3d795`） | v13 preregistration | VERIFIED_LOCAL_HISTORY | CURRENT |
| V13 采集 | 47ed183 | 2026-07-29 | 采集修正后正式基准 V13 | v13 raw | VERIFIED_LOCAL_HISTORY | CURRENT |
| V13 分析 | 8513e84 | 2026-07-29 | run-level paired 分析 | `analysis/independent-analysis-summary.json` | VERIFIED_LOCAL_HISTORY | CURRENT |
| V13 证据冻结 | 8138e4d | 2026-07-29 | 冻结 v13 证据 | formal-artifact-sha256.json | VERIFIED_LOCAL_HISTORY | CURRENT |
| V13 终审基线 | 26ef5bc | 2026-07-29 | 保留修正后 dry-run 审计轨迹（V13 审计源 HEAD） | project-state git.head | VERIFIED_LOCAL_HISTORY | CURRENT |
| 接口基线冻结 | d49d94e | 2026-07-30 | 冻结 RC2 接口基线 | rc2-interface-manifest.json | VERIFIED_LOCAL_HISTORY | CURRENT |
| 第五章定稿 | 52ee912/9388ed0/8616aea/dac2234 | 2026-07-30 | 第五章基于 V13 定稿、盲审、措辞冻结 | 第5章_…最终定稿.md | VERIFIED_LOCAL_HISTORY | CURRENT |
| 首轮正式运行 | 34af4ff（文档） | 2026-07-29 | 103,680 记录首轮运行（协议偏差） | 严格审稿报告 | DOCUMENTED_ONLY | SUPERSEDED/INVALIDATED |
| 安全整改/基础设施 | 8f06b695、4b75d6d3（文档） | 2026-07 | 安全整改提交与五节点基础设施冻结 | 总验收报告 | DOCUMENTED_ONLY | HISTORICAL |

## RC3 — r3-prep（linked worktree，gitdir 位于 `D:\Research\.git-backups\epoch-authorization.git\worktrees\epoch-authorization-r3-prep`）

| 阶段 | commit SHA | 日期 | 含义 | 对应证据 | 可解析 | 状态 |
|---|---|---|---|---|---|---|
| I9 Pilot 收口 | 95b8b60 | 2026-08-02 | 最终 I9 B/C/D 接受（93/93） | `i9-run-index.json` | VERIFIED_LOCAL_HISTORY | CURRENT（PILOT 冻结） |
| I10 预注册 | 2bf56d2 | 2026-08-02 | 冻结 I10 正式设计与预注册 | `i10/formal-claim-matrix.json` | VERIFIED_LOCAL_HISTORY | CURRENT |
| I11 执行 | a423bb0..4d12daf | 2026-08-02 | Formal runner 实现、配置统一、故障契约、最终执行修正 | `i11/formal-run-index.json`（attempt `FORMAL_20260802T095534Z_4d12daf`） | VERIFIED_LOCAL_HISTORY | CURRENT |
| I11 证据冻结 | 044c2bc / eb62900 | 2026-08-02 | 冻结 I11 证据并更新治理状态 | `i11/`、`experiments/r3/formal/` | VERIFIED_LOCAL_HISTORY | CURRENT |
| I12 结果评审 | a17d73b / 354c21b | 2026-08-02 | 冻结 I12 结果评审与 thesis-ready 数据集；修正负结果措辞 | `i12/` | VERIFIED_LOCAL_HISTORY | CURRENT |
| I13 章节写回 | 26870c1 | 2026-08-02 | RC3 章节写回与审计 | `i13/THESIS-RC3-WRITEBACK-FINAL.md` | VERIFIED_LOCAL_HISTORY | CURRENT |
| I14 全论文终审 | 807f788 | 2026-08-02 | 全论文终审 + 集成母本 | `thesis-integration/` | VERIFIED_LOCAL_HISTORY | CURRENT |
| I15 文献核验 | 26cd2f3 | 2026-08-02 | 最终文献核验冻结 | `final-literature-verification/` | VERIFIED_LOCAL_HISTORY | CURRENT |
| I16 格式候选 | 6940b68 | 2026-08-02 | V1 格式候选组装 | `final-manuscript/` | VERIFIED_LOCAL_HISTORY | SUPERSEDED（被 V2 取代） |
| I17 学术散文+模板 | 852979d | 2026-08-02 | 学术散文重构 + UESTC 官方模板 | `final-manuscript/i17/`（V2） | VERIFIED_LOCAL_HISTORY | CURRENT |
| M1 中期稿 | 7a36a4a | 2026-08-03 | M1 中期考评表 | `midterm-report/` | VERIFIED_LOCAL_HISTORY | HISTORICAL |
| M2 官方模板重建 | b4953e3 | 2026-08-03 | 基于官方空白模板重建中期考评表 | `midterm-report/m2/` | VERIFIED_LOCAL_HISTORY | HISTORICAL |
| M3–M7 迭代 | b250398..dce0df5 | 2026-08-03/04 | 中期稿 M3–M7 逐步收敛 | `midterm-report/m3..m7/` | VERIFIED_LOCAL_HISTORY | HISTORICAL |
| FINAL-CLEAN | 4807a4e / 2c24ef4 / 29d822f | 2026-08-04 | 中期最终固化（37 页）并记录 end head | `midterm-report/final/` | VERIFIED_LOCAL_HISTORY | CURRENT |

## 外层归档仓库（wangw-hub/thesis，公开）

| commit SHA | 日期 | 含义 | 标记 |
|---|---|---|---|
| ded7b32 | 2026-08-05 | 初始归档基线（代码+文档，排除 raw/密钥/运行时） | MILESTONE（历史基线） |
| bbb04cc | 2026-08-05 | docs(governance): synchronize thesis repository current state | MILESTONE |
| 483fc87 | 2026-08-05 | docs(governance): set small-paper P0 as current research action | SNAPSHOT_BASIS（本快照生成时所基于的已确认提交） |
| （本轮新提交） | 2026-08-05 | docs(governance): add public GitHub recovery mode | 本轮完成后在最终报告登记，不写回静态文件 |

外层提交均为 PUBLIC（Git 跟踪）；子项目历史（RC1/RC2/RC3 原子仓库）为 LOCAL_ONLY，
`VERIFIED_LOCAL_HISTORY` 仅表示可在本地 `.git-backups` 解析，不代表 GitHub 公开历史。

## 校验方式

```powershell
git --git-dir='D:\Research\.git-backups\time-policy.git' log --pretty=format:'%h|%ad|%s' --date=short
git --git-dir='D:\Research\.git-backups\epoch-authorization.git' log --pretty=format:'%h|%ad|%s' --date=short
git --git-dir='D:\Research\.git-backups\epoch-authorization.git\worktrees\epoch-authorization-r3-prep' log --pretty=format:'%h|%ad|%s' --date=short
```
