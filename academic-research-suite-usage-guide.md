# academic-research-suite 使用手册

适用环境：Codex Desktop / Codex CLI  
已安装技能：`academic-research-suite`  
本机路径：`C:\Users\wangw\.codex\skills\academic-research-suite`

这份手册的目标很直接：让你把 `academic-research-suite` 用成一个稳定的学术工作流，从一个模糊方向推进到一篇可投稿论文，并把同一套材料扩展成硕士毕业论文。

## 1. 安装结果与基本用法

安装已完成。安装命令等价于：

```powershell
python C:\Users\wangw\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py `
  --repo Imbad0202/academic-research-skills-codex `
  --ref main `
  --path skills/academic-research-suite `
  --method git
```

Codex 版不是四个分散技能，而是一个总入口：

```text
academic-research-suite
```

它内部路由到五条 workflow：

| 你要做什么 | 内部 workflow | 最适合的场景 |
|---|---|---|
| 梳理方向、找研究问题、文献综述、系统综述 | `deep-research` | 选题、开题、文献矩阵、研究问题收敛 |
| 写论文、写摘要、写大纲、改论文、查引用、转格式 | `academic-paper` | 论文初稿、投稿稿、修订稿 |
| 模拟审稿、找致命问题、复审修改是否到位 | `academic-paper-reviewer` | 投稿前内审、导师修改前自查、返修验证 |
| 研究到投稿的完整流水线 | `academic-pipeline` | 从 0 到完整论文，含诚信检查和两轮审稿 |
| 实验设计、跑代码实验、管理问卷/访谈、验证统计结果 | `experiment-agent` | 需要数据、实验、统计验证的论文 |

重要提示：技能会在下一轮对话中稳定可用。以后你只要自然语言说清楚任务，Codex 会按 `academic-research-suite` 的路由规则进入对应 workflow。

## 2. 最常用的触发方式

Codex 版支持自然语言触发，也支持类似 Claude slash command 的纯文本别名。建议在 Codex 里使用不带斜杠的别名，避免客户端把 `/xxx` 当成特殊命令吞掉。

| 目标 | 推荐输入 |
|---|---|
| 从模糊方向开始 | `帮我用 academic-research-suite 梳理这个研究方向：...` |
| 苏格拉底式收敛研究问题 | `帮我进入 deep-research socratic 模式，我的方向是...` |
| 快速扫文献 | `ars-3w 请比较这个方向的 WHY/HOW/WHAT 文献：...` |
| 做完整文献综述 | `ars-lit-review 我的研究问题是...，请做文献综述` |
| 规划论文结构 | `ars-plan 我的研究问题是...，目标期刊/学校要求是...` |
| 只要论文大纲 | `ars-outline 基于这些材料生成论文大纲：...` |
| 写摘要 | `ars-abstract 基于这篇论文草稿写中英文摘要：...` |
| 检查引用 | `ars-citation-check 检查这篇论文的引用和参考文献：...` |
| 生成 AI 使用声明 | `ars-disclosure 目标期刊是...，帮我写 AI 使用声明` |
| 模拟审稿 | `ars-reviewer 请按投稿前标准审稿这篇论文：...` |
| 完整流水线 | `ars-full 我想从 0 到 1 完成一篇可投稿论文，方向是...` |

如果你只有“我想写一篇关于 X 的论文”这种宽泛表述，技能会优先进入 `deep-research socratic`，先把研究问题问清楚，而不是立刻写大纲。这是正确行为。

## 3. 从 0 到 1 写出可投稿论文的主流程

推荐用 `academic-pipeline` 做完整项目。它是 10 个阶段：

| 阶段 | 名称 | 产出 |
|---|---|---|
| Stage 1 | Research | 研究问题简报、方法蓝图、文献清单、综合报告 |
| Stage 2 | Write | 论文初稿 |
| Stage 2.5 | Integrity | 引用、数据、主张、AI 研究失败模式检查 |
| Stage 3 | Review | 五视角审稿报告、编辑决定、修改路线图 |
| Stage 4 | Revise | 修订稿、逐点回复 |
| Stage 3' | Re-review | 修改验证报告、残余问题 |
| Stage 4' | Re-revise | 必要时二次修订 |
| Stage 4.5 | Final Integrity | 最终引用/数据/主张验证 |
| Stage 5 | Finalize | Markdown、DOCX、LaTeX、PDF 或目标格式稿件 |
| Stage 6 | Process Summary | 论文创建过程记录和人机协作质量记录 |

最推荐的启动提示词：

```text
请使用 academic-research-suite 的 academic-pipeline。
目标：从 0 到 1 完成一篇可以投稿的学术论文。
我的研究方向是：[你的方向]
我的学科是：[学科]
目标期刊/会议/毕业要求是：[如果知道就写，不知道写“不确定”]
我目前已有材料：[文献/数据/代码/问卷/草稿/无]
请先进入 Stage 1，用 socratic 模式帮我收敛研究问题，不要直接写大纲。
```

### Stage 1：把方向收敛成研究问题

目标不是“找一个看起来很高级的题目”，而是得到一个可回答、可验证、边界清楚的 RQ。

你需要给 Codex 的材料：

```text
我的研究兴趣：
我的专业/导师方向：
我能获取的数据或场景：
我希望使用的方法：
我不想做/不能做的内容：
毕业或投稿时间节点：
```

好产出应包含：

```text
Research Question Brief
Methodology Blueprint
In-scope / Out-of-scope
2-3 个子问题
关键词与检索式
初步文献矩阵
风险与伦理问题
```

通过标准：

```text
RQ 能用一句话说清
研究对象、变量/概念、方法、数据来源明确
能解释 novelty 在哪里
知道什么证据能支持或推翻结论
导师或同行能判断这个题目是否可做
```

### Stage 2：把研究材料写成论文初稿

启动提示词：

```text
基于 Stage 1 的 RQ Brief、Methodology Blueprint、文献矩阵和综合报告，
请进入 academic-paper plan/full 模式。
先生成 Paper Configuration Record 和详细大纲，等我确认后再写正文。
目标格式：[IMRaD / 文献综述 / 案例研究 / 理论论文 / 学位论文章节]
目标字数：[例如 8000 英文词 / 12000 中文字]
引用格式：[APA 7 / IEEE / Chicago / 学校模板]
```

建议先用 `plan`，再进入 `full`。不要急着让它一次性写完全文。更稳的节奏是：

```text
先确认配置
再确认大纲
再确认 argument blueprint
再分节写初稿
最后做 citation-check 和 reviewer
```

### Stage 2.5：投稿前诚信检查

这是强制关卡，不建议跳过。

检查内容：

```text
引用是否真实存在
文内引用和参考文献是否一一对应
每个核心主张是否有证据
数据、统计、图表是否与原始结果一致
是否存在 AI 生成的幻觉引用或过度包装
是否有方法学伪造、结果幻觉、框架锁定等失败模式
```

提示词：

```text
请对这篇论文进入 academic-pipeline Stage 2.5 Integrity。
严格检查引用存在性、claim-reference alignment、数据/统计一致性、AI research failure modes。
无法验证的项目请标记 FAIL 或 UNVERIFIED，不要猜。
```

### Stage 3：模拟同行评审

用 `academic-paper-reviewer full` 做投稿前内审。它会模拟：

```text
Editor-in-Chief
Methodology Reviewer
Domain Reviewer
Perspective Reviewer
Devil's Advocate Reviewer
Editorial Synthesizer
```

提示词：

```text
请使用 academic-paper-reviewer full 模式审稿。
目标是投稿前发现会导致拒稿或大修的问题。
请输出：
1. 五位 reviewer 的独立报告
2. Editorial Decision
3. 按优先级排序的 Revision Roadmap
4. P0/P1/P2 问题清单
```

关键习惯：不要只看“优点”，重点看 P0/P1。Devil's Advocate 的 CRITICAL 问题必须认真处理。

### Stage 4：按审稿意见修订

提示词：

```text
请进入 academic-paper revision-coach/revision 模式。
输入包括：原稿、审稿报告、Editorial Decision、Revision Roadmap。
请先把所有意见拆成逐条任务表，标记：
AGREE / PARTIALLY_AGREE / DISAGREE / NEEDS_DATA / OUT_OF_SCOPE。
然后生成修订计划和 Response to Reviewers skeleton。
```

修订时不要盲从 reviewer。技能明确允许 `REVIEWER_DISAGREE`，但必须有证据和专业理由。

### Stage 4.5：最终诚信检查

最终检查必须从头验证，不只是检查旧问题是否修好。

提示词：

```text
请进入 Stage 4.5 Final Integrity。
从头验证最终稿的所有引用、核心主张、数据、图表、统计解释、AI 使用声明。
只有零关键问题时才标记 ready for finalization。
```

### Stage 5：定稿与投稿材料

提示词：

```text
请进入 academic-paper format-convert 模式。
目标格式：[学校模板 / 期刊模板 / APA 7 / IEEE / LaTeX / DOCX]
请输出：
1. 最终论文
2. 参考文献
3. Cover letter 或投稿说明
4. AI 使用声明
5. Data Availability / Ethics / Funding / Conflict of Interest / CRediT 声明
```

## 4. 如何用它完成硕士毕业论文

硕士毕业论文通常不只是“一篇长论文”，它还需要开题、章节体系、研究过程记录、学校格式、答辩材料。建议把硕士论文拆成两个层次：

```text
核心投稿论文：1 个清晰 RQ + 可投稿结构
硕士毕业论文：在投稿论文基础上扩展理论、文献、方法、过程、附录
```

推荐总路线：

| 阶段 | 目标 | 使用方式 |
|---|---|---|
| 0 | 明确学校要求 | 让 Codex 读取培养方案、格式模板、开题要求 |
| 1 | 选题和 RQ | `deep-research socratic` |
| 2 | 开题报告 | `academic-paper plan` + `deep-research lit-review` |
| 3 | 文献综述章 | `deep-research lit-review` 或 `systematic-review` |
| 4 | 方法章 | `deep-research research_architect` + `experiment-agent plan` |
| 5 | 实验/数据 | `experiment-agent run/manage/validate` |
| 6 | 投稿论文初稿 | `academic-paper full` |
| 7 | 毕业论文扩展 | `academic-paper outline-only/full` 按章节写 |
| 8 | 内审与修改 | `academic-paper-reviewer full` |
| 9 | 格式和查重前检查 | `citation-check` + `format-convert` |
| 10 | 答辩材料 | 用最终论文生成答辩 PPT 大纲和问答清单 |

### 硕士论文推荐章节结构

具体以学校模板为准，但常见结构是：

```text
第 1 章 绪论
第 2 章 文献综述与理论基础
第 3 章 研究设计与方法
第 4 章 数据/实验/案例分析
第 5 章 结果与讨论
第 6 章 结论、贡献、局限与展望
参考文献
附录
致谢
```

启动提示词：

```text
请使用 academic-research-suite 帮我规划硕士毕业论文。
我的专业是：[专业]
学校要求/模板文件在：[路径，如果有]
我的研究方向是：[方向]
我希望最终同时形成：[毕业论文 + 可投稿小论文]
请先不要写正文，先输出：
1. 可投稿论文 RQ
2. 毕业论文总题目候选
3. 章节结构
4. 每章研究任务
5. 数据/实验需求
6. 12 周/16 周写作计划
```

### 开题报告提示词

```text
请基于当前 RQ 和文献矩阵，生成硕士开题报告草案。
必须包含：
选题背景与意义
国内外研究现状
研究问题与研究目标
研究内容
研究方法与技术路线
创新点
可行性分析
进度安排
预期成果
参考文献
请标记哪些内容已经有文献支持，哪些只是待验证假设。
```

### 文献综述章提示词

```text
请进入 deep-research lit-review 模式。
围绕我的硕士论文 RQ，生成文献综述章材料。
请输出：
1. 检索式和数据库
2. 纳入/排除标准
3. 文献矩阵
4. 主题脉络
5. 争议与不足
6. 本研究切入点
7. 可直接改写进第 2 章的章节草稿
所有引用必须可验证。
```

### 方法章提示词

```text
请基于我的 RQ 设计硕士论文方法章。
请明确：
研究范式
变量/概念定义
数据来源
样本与采样策略
实验/问卷/访谈/模型流程
分析方法
效度、信度或鲁棒性检查
伦理风险
局限性
请同时指出哪些设计会被审稿人或答辩老师质疑。
```

### 结果章与讨论章提示词

```text
我已经有这些结果：[贴结果/文件路径]
请先使用 experiment-agent validate 检查统计解释和可复现性。
然后帮我生成：
1. 结果表述框架
2. 图表清单
3. 每个结果对应的 claim
4. 每个 claim 对应的证据
5. 讨论章逻辑
6. 不能过度声称的边界
```

### 答辩准备提示词

```text
请基于我的硕士论文最终稿，生成答辩准备包：
1. 8-12 分钟答辩陈述结构
2. PPT 页码安排
3. 研究贡献的 3 种说法：保守版、标准版、强表达版
4. 20 个可能被问到的问题
5. 每个问题的回答要点
6. 最容易被质疑的方法/数据/创新点
```

## 5. 每次对话都要维护的“材料包”

长论文最怕上下文腐烂。建议在你的项目目录里维护一个 `paper_materials` 文件夹：

```text
paper_materials/
  00_requirements/
    school_template.docx
    journal_guidelines.md
  01_research_question/
    rq_brief.md
    methodology_blueprint.md
  02_literature/
    search_strategy.md
    literature_matrix.xlsx
    annotated_bibliography.md
  03_data_experiment/
    data_dictionary.md
    experiment_plan.md
    validation_report.md
  04_drafts/
    manuscript_v1.md
    thesis_chapter_1.md
  05_reviews/
    internal_review_round1.md
    revision_roadmap.md
  06_final/
    manuscript_submission.md
    thesis_final.md
```

每次新开对话时，给 Codex 这段：

```text
这是我的当前材料包：
- RQ Brief: [路径]
- Methodology Blueprint: [路径]
- Literature Matrix: [路径]
- Current Draft: [路径]
- Review Roadmap: [路径]

请先读取这些材料，再判断应该进入 academic-research-suite 的哪个 workflow/mode。
```

## 6. 推荐工作节奏

如果你还有 3-6 个月：

| 周期 | 任务 |
|---|---|
| 第 1-2 周 | Socratic 选题、RQ、方法蓝图 |
| 第 3-5 周 | 文献检索、文献矩阵、开题报告 |
| 第 6-9 周 | 数据/实验/问卷/访谈 |
| 第 10-12 周 | 投稿论文初稿 |
| 第 13-14 周 | 内审、诚信检查、修订 |
| 第 15-18 周 | 扩展成硕士论文各章 |
| 第 19-20 周 | 格式、查重前自查、导师反馈 |
| 第 21-22 周 | 答辩 PPT、问答准备、最终提交 |

如果你只剩 4-8 周，改用压缩路线：

```text
第 1 周：RQ + 文献矩阵 + 开题/章节大纲
第 2 周：方法章 + 数据/实验可行性
第 3 周：结果与讨论
第 4 周：完整初稿
第 5 周：审稿式内审 + 大修
第 6 周：格式、引用、查重前检查、答辩材料
```

## 7. 高质量使用原则

### 不要让它替你决定学术判断

你必须自己确认：

```text
研究问题是否值得做
方法是否真的可行
数据是否真实可靠
结论是否过度声称
引用是否真的读过
导师/学院是否接受这种结构
```

### 每次要求它区分三类内容

```text
Evidence：文献或数据直接支持的内容
Inference：基于证据的推论
Recommendation：写作或研究策略建议
```

推荐提示词：

```text
请把输出分成 Evidence / Inference / Recommendation。
凡是没有来源或无法验证的内容，请标为 UNVERIFIED。
```

### 所有引用都要可验证

不要接受“看起来像真的”的参考文献。使用：

```text
ars-citation-check 请逐条验证参考文献是否存在，优先 DOI、出版社页面、期刊官网、Crossref、Semantic Scholar、OpenAlex。
不存在或无法确认的引用必须移除或替换。
```

### 写作不要一步到位

稳的顺序是：

```text
配置确认 -> 大纲确认 -> 论证链确认 -> 分节草稿 -> 引用检查 -> 内审 -> 修订 -> 定稿
```

## 8. 一套可以反复复制的总提示词

```text
请使用 academic-research-suite 帮我推进论文项目。

项目目标：
1. 完成一篇可投稿学术论文
2. 在此基础上完成硕士毕业论文

当前阶段：
[选题 / 开题 / 文献综述 / 方法设计 / 实验数据 / 初稿 / 修改 / 定稿 / 答辩]

我的材料：
[贴摘要，或列出文件路径]

我的约束：
学科：
学校/导师要求：
目标期刊或会议：
字数：
引用格式：
截止日期：
已有数据：
不能做的事情：

请先判断应该进入哪个 workflow 和 mode。
然后输出：
1. 当前阶段目标
2. 需要我补充的材料
3. 本轮要产出的 artifact
4. 质量门禁
5. 下一步行动

请不要虚构引用。证据、推论、建议分开写。
```

## 9. 常见错误与纠正方式

| 错误 | 后果 | 正确做法 |
|---|---|---|
| 一上来就让它写完整论文 | 结构漂、引用假、方法空 | 先 RQ 和方法蓝图 |
| 没有维护材料包 | 长对话后上下文丢失 | 每阶段保存 artifact |
| 跳过 Stage 2.5 / 4.5 | 幻觉引用和过度主张进终稿 | 强制完整诚信检查 |
| 把 reviewer 意见全盘接受 | 论文可能被改坏 | 建立 AGREE/DISAGREE 表 |
| 文献综述只做摘要堆砌 | 没有研究 gap | 做主题矩阵和争议矩阵 |
| 结果章夸大结论 | 答辩和审稿容易被打穿 | 每个 claim 绑定证据和边界 |
| 毕业论文和投稿论文完全分离 | 工作量翻倍 | 先做核心论文，再扩展毕业论文 |

## 10. 你的最佳下一步

如果你现在还没有确定题目，直接发：

```text
请用 academic-research-suite 的 deep-research socratic 模式带我选题。
我的专业是：
我的兴趣方向是：
导师方向是：
我能获取的数据/实验条件是：
我的毕业截止时间是：
```

如果你已经有题目，发：

```text
请评估这个硕士论文题目是否可做，并帮我收敛成可投稿论文 RQ：
题目：
研究背景：
已有材料：
数据来源：
目标贡献：
```

如果你已经有草稿，发：

```text
请使用 academic-research-suite 先做 Stage 2.5 Integrity，再做 academic-paper-reviewer full。
这是我的论文草稿路径：
这是我的参考文献路径：
目标是投稿前发现拒稿风险和毕业论文答辩风险。
```

把技能当成“研究项目经理 + 文献助理 + 写作编辑 + 审稿模拟器 + 诚信审计员”，不要当成自动代写机器。你负责判断、选择、承诺和最终学术责任；它负责把繁重的结构化工作做得更密、更稳。
