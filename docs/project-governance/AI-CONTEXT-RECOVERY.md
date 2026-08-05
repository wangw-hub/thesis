# AI CONTEXT RECOVERY — 新会话上下文恢复指南

> 给未来的 Codex / GPT / 其他智能体：当你接到与本论文仓库相关的任务时，先按本指南恢复上下文。
> 恢复顺序是强制性的；恢复后你应能回答 CURRENT-SNAPSHOT.md 覆盖的全部 20 个核验问题。

## Step 1 — 读 CURRENT SNAPSHOT

先读 `docs/project-governance/CURRENT-SNAPSHOT.md`（当前状态唯一入口）与 `current-snapshot.json`。

## Step 2 — 读 AUTHORITY MAP

读 `docs/project-governance/AUTHORITY-MAP.md`，确定每类事实的权威来源，禁止自行猜测。

## Step 3 — 检查 Git HEAD

```powershell
git -C D:\Research status
git -C D:\Research log --oneline -3
```

确认当前 HEAD 与 `current-project-state.json` 的 `git.head` 一致；如不一致，以更新的提交为准并更新状态文件。

## Step 4 — 按任务读取对应权威源

研究内容相关任务 → 按 AUTHORITY-MAP 读取对应项目源码/正式实验/报告；
写作相关任务 → 读集成母本/文献/格式化状态 JSON；
中期/小论文 → 读 midterm final 与 small paper 状态。

## Step 5 — 冲突按权威排序裁决

冲突时使用 CURRENT-SNAPSHOT §13 的优先级：代码/raw/冻结索引 > 冻结证据 > 正式报告 > 治理文件 > 历史方案 > README/摘要。
旧结论若与 CURRENT 冲突：标记 SUPERSEDED/HISTORICAL，**不删除**。

## Step 6 — 禁止从 SUPERSEDED-DESIGNS 恢复旧方案

读 `SUPERSEDED-DESIGNS.md`；不得把 S-01..S-14 中的设计重新引入论文/技术方案。

## Step 7 — 禁止把 Pilot 当 Formal

Pilot/预实验（I9 Pilot、RC2 PILOT_ONLY、E1 pilot）不构成正式结论；只允许引用三组正式实验（RC1 E1、RC2 V13、RC3 I11）。

## Step 8 — 禁止修改 raw

任何正式实验 raw、预注册、结果包为冻结资产：只读。发现内部错误 → 登记 `FROZEN_ASSET_ISSUE`，不得直接修改。

## Step 9 — 记录所有新决策

新决策写入 `docs/project-governance/02-DECISION-LOG.md`（或子项目对应 DECISION-LOG），并同步更新状态 JSON。

## 最小新会话提示词（可复制）

```
你是本研究仓库的新 AI 会话，没有聊天历史。
1) 先读 D:\Research\docs\project-governance\CURRENT-SNAPSHOT.md；
2) 再读 AUTHORITY-MAP.md 与 AI-CONTEXT-RECOVERY.md；
3) 按任务类型读取对应权威来源（第 4 步）；
4) 不修改正式实验 raw/预注册/结果包；
5) 不恢复 SUPERSEDED-DESIGNS.md 中的废弃方案；
6) 不把 Pilot 当 Formal；
7) 遇到冲突按权威排序裁决并保留历史。
```
