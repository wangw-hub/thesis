# M7 最终 QA 报告（五层审计）

- 日期：2026-08-04
- 范围：`王威-专业学位研究生学位论文中期考评表-M7最终候选稿.docx/.pdf`（36 页）
- 结论：FATAL = 0，MAJOR = 0；存在 1 项需用户确认的元数据项（填表日期）。

## 第一层：正文语义审计

- 三项研究主线（确定性表示 / 可信授权执行 / 版本化密文头部与撤销闭环）与 M6 冻结主线完全一致。
- 负结果全部保留：层次覆盖无普遍存储优势；缓存与层次覆盖无稳定端到端收益；Kubo 正常路径无稳定性能优势（恢复可用性定位）。
- 创新点措辞收敛：无“天然可信”“不可篡改”“首次”“领先”“显著优于”等绝对化表述（已全文扫描）。
- 阶段成果为“拟投稿/撰写中”稳妥表述，无虚假发表/申请状态。

## 第二层：数学/算法审计

- FORMULA_PLACEHOLDER_COUNT = 0（DOCX OMML 与 PDF 双重核验，无 `<m:e/>` 空基）。
- FORMULA_SEMANTIC_ERROR = 0；研究内容三公式均按冻结源码（digest.py / hpke_provider.py / chunk_crypto.py / guard.py / reconciler.py / HeaderRegistryV1.sol）重写。
- 展示公式 16 个，编号 (1)–(16) 连续、按正文出现顺序升序。
- ALGORITHM_LOGIC_ERROR = 0；ALGORITHM_NUMBERING_ERROR = 0；ALGORITHM_INTERFACE_ERROR = 0。
- 算法 1–8 连续；算法6（HeaderOnlyUpdate）在算法7（BodyRotation）之前；版本公式 (13)(14) 先于对应算法。

## 第三层：图表审计

- BROKEN_FIGURE = 0（20/20 图题齐全、图号连续、无裁切证据）。
- BROKEN_TABLE = 0；MISSING_FIGURE_CAPTION = 0；MISSING_TABLE_CAPTION = 0；TABLE_CONTINUATION_ERROR = 0。
- 表1–表8 表题均在表上方；表头行 `w:tblHeader` + `w:cantSplit` + keepNext；表5/6/8 整表单页展示。

## 第四层：文献审计

- REFERENCE_COUNT = 34（31–34 目标内）。
- REFERENCE_2021_2026_RATIO = 0.618（≥0.50）；REFERENCE_2024_2026_COUNT = 12（≥8）。
- MISSING_REFERENCE = 0；ORPHAN_REFERENCE = 0；DUPLICATE_REFERENCE = 0；CITATION_ORDER_ERROR = 0。
- UNVERIFIED_NEW_REFERENCE = 0（3 篇新增文献均双源核验：ScienceDirect/ACM、IEEE Xplore/ACM、MDPI/Crossref/RePEc）。
- QuickCheck/JCS 引用语义已修正。

## 第五层：PDF 视觉审计（逐页程序化）

- 页数：36（M6：35；增量来自 3 篇新增参考文献与整表分页规则，非内容填充）。
- 封面：攻读学位级别单一“☑硕士”，无 Wingdings 重复符号。
- 第 2 页空白为学校空白模板显式分页（OFFICIAL_TEMPLATE_REQUIRED_BLANK_PAGE），保留。
- 公式 (1)–(16) 各页按顺序出现，无虚线占位框。
- 算法 1–8 全部渲染为原生文字（无截图模糊）。
- 图 1–20、表 1–8 全部出现且图号/表号连续。
- 页眉页脚/页码由模板控制；无低密度内容页（除官方空白页）。
- “阶段性研究成果”标题不再孤行。

## 问题清单

| 等级 | 数量 | 说明 |
|---|---|---|
| FATAL | 0 | - |
| MAJOR | 0 | - |
| MINOR | 1 | 封面填表日期（2026-07-27）早于研究内容三正式实验完成日期（2026-08-02），需用户确认按 A（改日期）或 B（保留日期并调整表述）处理。 |
| FORMAT_ONLY | 2 | ① 页数 36 略高于“约 32–35 页”建议；② 培养方式复选框沿用模板 Wingdings 符号渲染（单符号，无双重）。 |

## 最终状态

`M7_CONTENT_READY_AWAITING_USER_METADATA_CONFIRMATION`

在用户确认填表日期处理方式后，可切换为
`M7_MIDTERM_REPORT_FINAL_CANDIDATE_READY_FOR_ADVISOR_REVIEW`。
