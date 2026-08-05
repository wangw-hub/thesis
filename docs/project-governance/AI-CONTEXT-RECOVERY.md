# AI CONTEXT RECOVERY — 新会话上下文恢复指南

> 给未来的 Codex / GPT / 其他智能体：接到与本论文仓库相关的任务时，先判断你所在模式，
> 再按对应模式的强制顺序恢复上下文。
> 恢复完成后，你应能回答 CURRENT-SNAPSHOT.md 覆盖的全部核验问题
> （本地 20 问见 GOVERNANCE-CONSISTENCY-AUDIT.md；公开 30 问见 PUBLIC-GITHUB-CONTEXT-RECOVERY-TEST.md）。

## 模式选择

| 条件 | 模式 |
|---|---|
| 本机可访问 `D:\Research`，raw / `.git-backups` / 实验目录可访问 | **MODE A — LOCAL_FULL_MODE** |
| 只有公开仓库 https://github.com/wangw-hub/thesis，无本地路径 | **MODE B — PUBLIC_GITHUB_MODE** |

---

## MODE A — LOCAL_FULL_MODE

适用于本地 Codex / 有 `D:\Research` 访问权限的会话。允许使用 git、本地 raw、`.git-backups`、
本地实验目录与完整子项目历史。

1. 读 `docs/project-governance/CURRENT-SNAPSHOT.md`（当前状态唯一入口）。
2. 读 `docs/project-governance/AUTHORITY-MAP.md`。
3. 检查 Git：`git -C D:\Research status` + `git -C D:\Research log --oneline -3`；实时 HEAD 动态读取。
4. 按任务类型读取对应绝对权威（AUTHORITY-MAP 的 Absolute Authority）。
5. 冲突按 CURRENT-SNAPSHOT §13 排序裁决；旧结论标记 SUPERSEDED/HISTORICAL，不删除。
6. 禁止从 SUPERSEDED-DESIGNS.md 恢复旧方案。
7. 禁止把 Pilot 当 Formal；禁止修改 raw/预注册/结果包。
8. 新决策记录到 DECISION-LOG 并同步状态 JSON。

---

## MODE B — PUBLIC_GITHUB_MODE

适用于普通 GPT：只有 https://github.com/wangw-hub/thesis，**没有任何本地路径访问**。

### 强制读取顺序

1. `README.md`
2. `docs/project-governance/CURRENT-SNAPSHOT.md`
3. `docs/project-governance/AUTHORITY-MAP.md`
4. `docs/project-governance/current-project-state.json`
5. `docs/project-governance/SUPERSEDED-DESIGNS.md`
6. `docs/project-governance/EXPERIMENT-DATA-MANIFEST.md`
7. 根据具体任务进入相应 RC 权威材料（按 AUTHORITY-MAP 的 Public GitHub Authority 列）。

### 明确禁止

- 假设 `D:\Research` 可访问；
- 假设 local raw 可访问；
- 假设 `.git-backups` 可访问；
- 因为 raw 不公开就认定实验不存在；
- 根据历史文件覆盖 CURRENT-SNAPSHOT；
- 把 PILOT 当 FORMAL；
- 将 SUPERSEDED 方案恢复为当前方案。

### 遇到 LOCAL_ONLY 证据时的规则

1. 查找 AUTHORITY-MAP 的 Public fallback（公开 summary / manifest / final report / index）；
2. 使用公开冻结摘要得出正式结论；
3. 明确说明原始 raw 未公开（LOCAL_ONLY）；
4. 不猜测 raw 内容、不重算未公开数据。

### 实时 HEAD

不要以任何静态治理文件中的 SHA 作为“当前 HEAD”。实时 HEAD 从 GitHub `main` 分支
（或本地 git）动态读取；静态文件只保留 `snapshotBasisHead`（生成快照时的已确认提交）。

---

## Public GitHub minimal bootstrap prompt

可复制给无本地权限的新会话：

```
请恢复以下硕士论文研究项目的当前上下文：

https://github.com/wangw-hub/thesis

你没有本地 D:\Research 访问权限，因此必须使用仓库定义的 PUBLIC_GITHUB_MODE。

依次读取：

1. README.md
2. docs/project-governance/CURRENT-SNAPSHOT.md
3. docs/project-governance/AUTHORITY-MAP.md
4. docs/project-governance/current-project-state.json
5. docs/project-governance/SUPERSEDED-DESIGNS.md

恢复以下信息：

- 论文题目与研究问题；
- RC1/RC2/RC3 当前最终状态；
- 各研究内容的正式实验；
- 负结果；
- Forbidden Claims；
- Thesis / Midterm / Small Paper 状态；
- 唯一 CURRENT NEXT ACTION。

若某权威 raw 为 LOCAL_ONLY，
使用 AUTHORITY-MAP 定义的 PUBLIC_GITHUB_FALLBACK，
不得臆造未公开数据。

历史文档不能覆盖 CURRENT-SNAPSHOT。

恢复完成后再处理当前任务。
```

## 通用纪律（两种模式共同）

1. 不修改正式实验 raw / 预注册 / 结果包（冻结资产；错误登记 `FROZEN_ASSET_ISSUE`）。
2. 不把 Pilot 当 Formal；三组正式实验 = RC1 E1、RC2 V13、RC3 I11。
3. 不恢复 SUPERSEDED-DESIGNS.md 中的废弃方案。
4. 记录所有新决策并同步状态文件。
