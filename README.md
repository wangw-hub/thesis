# Thesis Repository

## 论文题目

**面向非连续时间约束的区块链数据共享关键技术研究及实现**

学位类型：计算机技术专业硕士（电子科技大学）

本仓库是论文全部研究工作的存档，目标是让**任何没有聊天历史的新 AI 会话**只读本仓库即可准确恢复研究状态、成果、证据边界与下一步。

## Current Status（2026-08-05）

| 项目 | 状态 |
|---|---|
| RC1 非连续时间策略编译 | COMPLETED_WITH_SCOPE_ADJUSTMENT（`I*` 主表示，`C(P)` 派生 IR；E1 正式实验 168 配置/15,120 记录） |
| RC2 许可联盟链授权执行 | COMPLETED_WITH_VALID_RERUN_EVIDENCE（V13：77,760 请求/233,280 链读；第 5 章定稿） |
| RC3 版本化密文头部/前瞻撤销 | FORMAL_COMPLETED（I11：145/145 有效 RUNs；章节已写入集成母本） |
| Thesis | I14 集成母本 + I15 文献核验完成；I17 V2 格式候选（官方模板已应用），**NOT SUBMISSION_READY** |
| Midterm | FINAL-CLEAN 最终固化版（37 页），待导师评审 |
| Small Paper | 计划拟投《软件学报》（未开始仓库内工作） |

## Start Here（强制阅读顺序）

1. [docs/project-governance/CURRENT-SNAPSHOT.md](docs/project-governance/CURRENT-SNAPSHOT.md) — 当前状态唯一入口
2. [docs/project-governance/AUTHORITY-MAP.md](docs/project-governance/AUTHORITY-MAP.md) — 每类事实的唯一权威来源
3. [docs/project-governance/00-PROJECT-CONSTITUTION.md](docs/project-governance/00-PROJECT-CONSTITUTION.md) — 项目宪法与禁止主张
4. 具体研究内容（见 Repository Structure）
5. 历史材料仅在需要审计时按需读取

> **Any new AI session must read CURRENT-SNAPSHOT.md first.**

## Repository Structure

```
crypto_thesis/
├── time-policy/                    # RC1：时间策略编译（第四章）
├── epoch-authorization/            # RC2：授权状态执行（第五章）
├── epoch-authorization-r3-prep/    # RC3：密文头部/撤销 + 中期报告 + 论文母本（第六章等）
├── artifacts/                      # 开题报告等文档
├── 论文实施蓝图V1.0.md              # 历史蓝图（PLAN，不代表 CURRENT）
└── 开题报告系统级审查与重构报告.md
docs/project-governance/            # 治理层：状态快照、权威映射、索引、清单（本仓库第一入口）
thesis_literature_verified_2026-07-30/  # 早期文献包（HISTORICAL，论文以 I15 为准）
academic-research-suite-usage-guide.md  # ARS 研究流水线使用说明
```

各子项目内先读 `README.md` 与 `AGENTS.md`，再按 AUTHORITY-MAP 读取报告/证据。

## Formal Evidence

| 正式实验 | 位置（本地） | 规模 |
|---|---|---|
| RC1 E1 | `crypto_thesis/time-policy/experiments/runs/e1_20260727_ec8b193_r3/` | 168 配置 / 15,120 记录 |
| RC2 V13 | `crypto_thesis/epoch-authorization/experiments/runs/formal_auth_multihost_rerun_v13_20260729T073007Z_8a3d795/` | 77,760 请求 / 233,280 链读 |
| RC3 I11 | `crypto_thesis/epoch-authorization-r3-prep/experiments/r3/formal/` | 35 warmup + 145 measured（145/145 有效） |

Pilot（I9、RC2 pilot）不是 Formal。RC2 首轮 103,680 记录运行已 INVALIDATED，禁止引用为性能证据。

## Large Data

正式实验 raw 未进入公开 GitHub（单文件超限/体积考虑）。本地完整位置见
[EXPERIMENT-DATA-MANIFEST.md](docs/project-governance/EXPERIMENT-DATA-MANIFEST.md)；
本地 vs 公开资产区别见 [LOCAL-VS-PUBLIC-ASSETS.md](docs/project-governance/LOCAL-VS-PUBLIC-ASSETS.md)。
区块链运行时（Besu/JDK）与依赖、虚拟环境、密钥目录均不版本化。

## Historical Materials

旧文档（早期蓝图、技术设计 V1.0、审稿前版本、M1–M7 中期稿等）保留用于**审计与方案演变**，
不代表 CURRENT。废弃方案清单见 [SUPERSEDED-DESIGNS.md](docs/project-governance/SUPERSEDED-DESIGNS.md)。

## AI Continuation

任何新 AI 会话必须：

1. 先读 `docs/project-governance/CURRENT-SNAPSHOT.md`；
2. 按 `AUTHORITY-MAP.md` 定位权威源（详细步骤见 `AI-CONTEXT-RECOVERY.md`）；
3. 不修改正式实验 raw/预注册/结果包；
4. 不恢复 SUPERSEDED-DESIGNS 中的废弃方案；
5. 不把 Pilot 当 Formal；不产生 Forbidden Claims。
