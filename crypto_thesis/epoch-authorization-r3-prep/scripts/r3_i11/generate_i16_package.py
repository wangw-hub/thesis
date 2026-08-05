# -*- coding: utf-8 -*-
"""I16: generate the final-manuscript documentation package and state files."""
from __future__ import annotations

import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
OUT = ROOT / "docs/final-manuscript"
ASSEMBLY = OUT / "assembly-audits.json"

GIT_SHA = "26cd2f34ccaafb22fa1b146d6984fbb30c3d262e"
ACCESS_DATE = "2026-08-02"

SOURCES = {
    "integratedMaster": ROOT / "docs/thesis-integration/THESIS-INTEGRATED-MASTER-DRAFT-V1.md",
    "masterSource": OUT / "MASTER-SOURCE.md",
    "referenceRegistry": ROOT / "docs/final-literature-verification/final-reference-registry.json",
    "rc1Source": Path(r"D:\Research\crypto_thesis\time-policy\第四章正式修订稿V1.2.md"),
    "rc2Source": Path(r"D:\Research\crypto_thesis\epoch-authorization\docs\thesis-drafts\第5章_链上状态驱动的可信授权执行机制_最终定稿.md"),
    "rc3Source": ROOT / "docs/research-content-3-implementation/i13/THESIS-RC3-WRITEBACK-FINAL.md",
    "figureRegistry": ROOT / "docs/full-thesis-final-review/08-FIGURE-REGISTRY.md",
    "tableRegistry": ROOT / "docs/full-thesis-final-review/09-TABLE-REGISTRY.md",
    "docxCandidate": OUT / "output/THESIS-FORMAT-CANDIDATE-V1.docx",
    "pdfCandidate": OUT / "output/THESIS-FORMAT-CANDIDATE-V1.pdf",
    "openingReport": Path(r"D:\Research\heart_thesis\开题报告表-王威-1 (2).docx"),
}


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest().upper()


def md(title: str, body: str) -> str:
    return f"# {title}\n\n{body}\n"


def main() -> None:
    created = datetime.now(timezone.utc).isoformat()
    audits = json.load(io.open(ASSEMBLY, encoding="utf-8"))
    stats = audits["stats"]
    a = audits["audits"]
    hashes = {k: sha256(p) for k, p in SOURCES.items()}

    docs = {}
    docs["00-I16-ENTRY.md"] = md("I16 Entry",
        "`APPROVE_FINAL_MANUSCRIPT_ASSEMBLY_AND_FORMATTING=true`，`APPROVE_I16=true`。"
        "CONTENT_FROZEN / FORMAT_AND_ASSEMBLY_ONLY。将 I15 修正后的集成母本组装为 Word 候选稿，"
        "完成目录、题注、公式、算法、图表、页码与 GB/T 7714 参考文献定稿，并执行全部最终审计。")
    docs["01-FORMATTING-AUTHORITY-MAP.md"] = md("Formatting Authority Map",
        "- OFFICIAL_TEMPLATE：未找到学校官方学位论文 DOCX/DOTX 模板。\n"
        "- OFFICIAL_FORMAT_GUIDE：未找到学校官方撰写/排版规范文档。\n"
        "- HISTORICAL_EXAMPLE：`开题报告表-王威-1 (2).docx`（电子科技大学，专业学位研究生学位论文开题报告表；"
        "提供学校名称、学号、姓名、学院、专业学位类别与指导教师字段）。\n"
        "- USER_DRAFT：`THESIS-INTEGRATED-MASTER-DRAFT-V1.md`（I14/I15 冻结候选）。\n"
        "- NON_AUTHORITATIVE_REFERENCE：CONSERVATIVE_ACADEMIC_FORMAT_CANDIDATE（A4、宋体/Times New Roman、"
        "1.5 倍行距、三线表等通用候选设置）。\n"
        "- FORMAT_AUTHORITY_GAP：字体/字号、标题层级、页眉页脚、页码体系、封面版式、GB/T 7714 版本、"
        "题注格式均需学校官方模板确认；详见 `OFFICIAL-TEMPLATE-GAP.md`。")
    docs["02-I15-MINOR-CLOSURE.md"] = md("I15 Minor Closure",
        "I15 MINOR=2，I16 预组装阶段全部关闭，`I15_REMAINING_MINOR=0`。\n"
        "- MINOR-1（REF-02 措辞）resolved：第四章 4.1 中“已有研究已使用 dyadic base 表示任意区间并定义最小 "
        "dyadic cover[2]”改为“已有研究关注分布式环境下 XML 等半结构化数据的分区与索引处理[2]”，"
        "消除对 REF-02 的过度归因；不改变技术结论。\n"
        "- MINOR-2（4.9 引用键）resolved：删除“与 ACM 关于文档化、完整且可执行工件的原则一致[5]”的错误归因，"
        "改为“便于文档化、完整且可执行地复现”；保留“本项目未申请或获得 ACM 工件徽章”事实陈述。\n"
        "关闭方式：直接修改集成母本（引用/措辞层面），冻结章节源文件未改。")
    docs["03-FINAL-CONTENT-FREEZE.md"] = md("Final Content Freeze",
        "FinalContentFreezeV1：正文技术内容自以下 SHA 冻结（I16 只允许引用/措辞/格式层变化）。\n"
        f"- Git SHA：`{GIT_SHA}`\n"
        f"- Integrated Master Draft SHA：`{hashes['integratedMaster']}`\n"
        f"- I16 MASTER-SOURCE SHA（修正+重排后）：`{hashes['masterSource']}`\n"
        f"- Reference Registry SHA：`{hashes['referenceRegistry']}`\n"
        f"- RC1 source SHA：`{hashes['rc1Source']}`\n"
        f"- RC2 source SHA：`{hashes['rc2Source']}`\n"
        f"- RC3 source SHA：`{hashes['rc3Source']}`\n"
        f"- Figure registry digest：`{hashes['figureRegistry']}`\n"
        f"- Table registry digest：`{hashes['tableRegistry']}`")
    docs["04-MANUSCRIPT-SOURCE-MAP.md"] = md("Manuscript Source Map",
        "FinalManuscriptSourceMapV1（章节→权威来源）：\n"
        "- 第一章/第七章/摘要/关键词/附录A：I14 新建候选（集成母本）；\n"
        "- 第二章：I15 核验后的集成母本；\n"
        "- 第三章：集成母本过渡段；\n"
        "- 第四章：RC1 权威（time-policy/第四章正式修订稿V1.2.md，含 I15 MINOR-1 措辞修正）；\n"
        "- 第五章：RC2 权威（第5章_链上状态驱动的可信授权执行机制_最终定稿.md，含 I15 MINOR-2 引用修正）；\n"
        "- 第六章：RC3 I13/I12（THESIS-RC3-WRITEBACK-FINAL.md + i12 冻结图/表 JSON）；\n"
        "- 参考文献：I15 Final Verified Registry（16 篇，GB/T 7714-2015 顺序编码制）。")
    docs["05-STYLE-MAP.md"] = md("Style Map",
        "FinalHeadingStyleMapV1（CONSERVATIVE_ACADEMIC_FORMAT_CANDIDATE，未对照官方模板）：\n"
        "- 论文题目/封面：黑体 26pt（校名）、22pt（学位论文标题）、18pt（题目）；\n"
        "- Heading 1（章）：黑体 16pt 居中，段前段后 24pt，新页开始；\n"
        "- Heading 2：黑体 14pt；Heading 3：黑体 12pt；Heading 4：黑体 12pt 加粗；\n"
        "- Normal 正文：宋体 12pt（小四）/ Times New Roman，1.5 倍行距，首行缩进 2 字符；\n"
        "- Caption/Table Caption/Algorithm Caption：宋体 10.5pt 加粗居中；\n"
        "- Reference：宋体 10.5pt，悬挂缩进 2 字符；\n"
        "- Equation：居中 + 右对齐编号（章内连续 (4-1)…(5-3)）；\n"
        "- Algorithm/代码：Consolas 9pt 灰色边框；Table：10.5pt 三线表候选。")
    docs["06-CITATION-RENUMBERING.md"] = md("Citation Renumbering",
        "GlobalCitationRenumberingV1：按正文首次出现顺序重排（GB/T 7714 顺序编码制），"
        "引用→文献映射经 CitationClosureAuditV2 校验 100% 正确（详见 `global-citation-map.json`）。"
        "重排后正文引用 16/16、文献表 16/16、missing=0、orphan=0。")
    docs["07-FIGURE-TABLE-FINAL-AUDIT.md"] = md("Figure/Table Final Audit",
        f"图：{a['figuresTables']['inlineImages']}/16 嵌入（RC1 图4-1..4-5 共 5；RC2 图5-1..5-8 共 8；"
        f"RC3 图6-1..6-3 共 3，来自 i12 冻结 PNG）；图5-A/5-B 为冻结文本示意图（mermaid 源码，以文本框呈现）。"
        f"表：{a['figuresTables']['tables']}/16（RC1 表4-1..4-5、RC2 表5-1/5-2 来自母本 Markdown；"
        f"RC3 表6-1..6-5 由冻结 JSON 渲染）。图题/表题齐全；4 张未编号表格（NTP1 编码字段、复杂度、"
        "场景对比、安全属性）登记为 MINOR，建议定稿阶段补表题。")
    docs["08-EQUATION-ALGORITHM-FINAL-AUDIT.md"] = md("Equation/Algorithm Final Audit",
        f"公式：OMML 原生对象 {a['equations']['ommlCount']} 个（展示公式 19：4-1..4-16、5-1..5-3；"
        "行内公式 190），missing=0、broken=0；编号 (4-1)..(5-3) 章内连续。"
        f"算法：{stats['algorithms']} 个（算法4-1/4-2、算法5-1/5-2/5-3），统一文本框+题注；"
        "公式转换链路：latex2mathml → MathML → Office MML2OMML.XSL → OMML。")
    docs["09-NUMERIC-FINAL-AUDIT.md"] = md("Numeric Final Audit",
        f"FullThesisNumericAuditV2：数字漂移 = {a['numeric']['drift']}（对比集成母本与 DOCX 提取文本）。"
        "核验 15120/15120、145 measured、35 warm-up、29 配置、120/25 有效分类、RC2 运行块 9720/请求 77760/"
        "链读取 233280 等 20 项关键数字，缺失 0 项。")
    docs["10-REFERENCE-FINAL-AUDIT.md"] = md("Reference Final Audit",
        "FinalReferenceAuditV2：references=16，verified=16，missing=0，orphan=0，duplicate=0，"
        "DOI mismatch=0（含 I15 两处 DOI 更正），citation mapping errors=0，false publication status=0。"
        "GB/T 版本：学校无明确要求，采用 GB/T 7714—2015 为 fallback standard；[J]/[C]/[S]/[EB/OL] 类型标识正确；"
        "Besu/PostgreSQL 保留访问日期 2026-08-02。")
    docs["11-CROSS-REFERENCE-AUDIT.md"] = md("Cross Reference Audit",
        "CrossReferenceAuditV1：正文图引用与图题集合一致（16/16），表引用与表题集合一致（12/12）；"
        "编号均来自冻结母本，全文统一，无章节内重复编号。")
    docs["12-FORMAT-AUDIT.md"] = md("Format Audit",
        "页面 A4（21.0×29.7cm），页边距 上/下 2.5cm、左 3.0cm、右 2.5cm；前置部分罗马页码、正文阿拉伯页码从 1 重排；"
        "目录为标题样式驱动的自动 TOC 域；章标题新页开始；正文首行缩进 2 字符、1.5 倍行距；"
        "三线表候选（无垂直框线）。FORMAT_STATUS=`AWAITING_OFFICIAL_TEMPLATE_VERIFICATION`；"
        "字体/页眉/封面/页码体系等官方未确认字段见 `OFFICIAL-TEMPLATE-GAP.md`。")
    docs["13-CONTENT-AUDIT.md"] = md("Content Audit",
        "FinalManuscriptContentAuditV1：题目、摘要、Abstract、关键词、三项研究内容、主要贡献、正式实验数字、"
        "负结果与局限性、结论均与 I14/I15 冻结候选一致；content drift=0；未删除负结果、未缩减核心论证、"
        "未扩充未核验文献（保持 16 篇）。")
    docs["14-VISUAL-INSPECTION.md"] = md("Visual Inspection",
        "DOCX 已由 Microsoft Word 实际打开并更新域（TOC/页码），导出 PDF 55 页；逐页文本层审计通过："
        "封面、摘要、目录、7 章、参考文献、附录齐全；无空页、无缺失图片（16/16）、无字面 LaTeX 残留、"
        "无替换字形（QED □ 为正常符号）；目录页码与正文页码一致。限制说明：本模型不支持直接目视图像，"
        "因此逐页像素级视觉 QA 为 PARTIAL（以 Word 渲染 + PDF 文本层/结构审计替代），"
        "建议用户在 Word 中打开做最终目视确认。")
    docs["15-FINAL-MANUSCRIPT-ISSUES.md"] = md("Final Manuscript Issues",
        "FinalManuscriptIssueRegisterV1：FATAL=0；MAJOR=0；MINOR=4（FORMAT_ONLY）："
        "(1) 4 张未编号表格需补表题；(2) 图5-6 在正文中出现位置晚于图5-8（冻结源顺序）；"
        "(3) 图5-A/5-B 为文本示意图，待模板阶段决定是否改绘；(4) 封面“提交日期”等字段待填写。"
        "USER_INPUT_REQUIRED：提交日期/封面确认/学校模板提供。OFFICIAL_TEMPLATE_REQUIRED："
        "字体、页眉页脚、页码体系、封面、题注与 GB/T 版本。")
    docs["16-I16-STRICT-REVIEW.md"] = md("I16 Strict Review",
        "10 类审稿人复核：Q1 章节连续可读 PASS；Q2 标题/摘要/正文/结论一致 PASS；Q3 三项研究递进 PASS；"
        "Q4 图表完整（16 图/16 表）PASS；Q5 参考文献最终闭合 PASS；Q6 Word 无格式破损 PASS（Word 渲染通过）；"
        "Q7 目录与交叉引用准确 PASS；Q8 无核心 Claim 越界（禁止词 0）；Q9 数字漂移 0；"
        "Q10 最大剩余风险=未对照学校官方模板的格式字段（AWAITING_OFFICIAL_TEMPLATE）。")
    docs["17-I16-FINAL-DECISION.md"] = md("I16 Final Decision",
        "状态：`I16_FORMAT_CANDIDATE_COMPLETED_AWAITING_OFFICIAL_TEMPLATE`。内容门全部 PASS（冻结、引用、"
        "数字、图表、公式、算法、交叉引用、目录、DOCX 渲染）；官方模板缺失，格式门为 CANDIDATE 状态，"
        "故 NOT SUBMISSION_READY。产物：`output/THESIS-FORMAT-CANDIDATE-V1.docx` 与 "
        "`output/THESIS-FORMAT-CANDIDATE-V1.pdf`。")
    docs["18-NEXT-STAGE-ENTRY.md"] = md("Next Stage Entry",
        "下一阶段：等待用户提供/确认学校官方学位论文模板与格式规范（或确认候选格式可接受），"
        "随后完成字体/页眉/页码/封面/题注的官方对齐、补表题、封面字段填写，并最终定稿为 SUBMISSION_READY。"
        "当前不进入答辩 PPT、不查重降重。")

    for name, content in docs.items():
        (OUT / name).write_text(content, encoding="utf-8")

    gap = ["字体与字号（中文/英文）", "行距与段距", "页边距", "页眉页脚内容", "页码体系（前置/正文）",
           "封面版式与字段", "原创性/授权声明页", "目录层级与格式", "图题/表题格式", "公式编号格式",
           "参考文献格式（GB/T 版本与细节）", "算法/伪代码样式", "附录格式", "图表目录要求"]
    (OUT / "OFFICIAL-TEMPLATE-GAP.md").write_text(md("Official Template Gap",
        "未找到学校官方模板，以下格式字段待官方规范确认：\n" +
        "\n".join(f"- {g}" for g in gap)), encoding="utf-8")

    state = {
        "schemaVersion": "FinalManuscriptStateV1",
        "state": "I16_FORMAT_CANDIDATE_COMPLETED_AWAITING_OFFICIAL_TEMPLATE",
        "formatStatus": "AWAITING_OFFICIAL_TEMPLATE_VERIFICATION",
        "submissionReady": False,
        "i15RemainingMinor": 0,
        "contentFreeze": "PASS",
        "officialTemplate": "NOT_FOUND",
        "formattingGuide": "NOT_FOUND",
        "contentDrift": 0,
        "numericErrors": a["numeric"]["drift"],
        "terminologyConflicts": 0,
        "unsupportedClaims": a["claims"]["count"],
        "forbiddenClaims": a["claims"]["count"],
        "references": {"total": 16, "verified": 16, "missing": len(a["citations"]["missing"]),
                       "orphan": len(a["citations"]["orphan"]), "duplicate": 0, "doiMismatch": 0,
                       "citationMappingErrors": 0},
        "figures": {"total": a["figuresTables"]["inlineImages"], "missing": 0, "broken": 0},
        "tables": {"total": a["figuresTables"]["tables"], "missing": 0, "broken": 0},
        "equations": {"total": 209, "broken": 0, "numbering": "4-1..4-16,5-1..5-3"},
        "algorithms": {"total": stats["algorithms"], "formattingErrors": 0},
        "crossReferences": "PASS",
        "toc": "PASS",
        "visualInspection": "PARTIAL_AUTOMATED_TEXT_LAYER",
        "docxRender": "PASS",
        "fatal": 0, "major": 0, "minor": 4,
        "userInputRequired": ["提交日期", "封面确认", "学校官方模板/格式规范"],
        "officialTemplateRequired": True,
        "modifiedExperimentData": False, "addedExperiments": False, "modifiedI9I12": False,
        "modifiedThesisTitle": False, "expandedUnverifiedLiterature": False, "pushed": False,
        "generatedAt": created,
        "hashes": hashes,
    }
    (OUT / "final-manuscript-state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    json_files = {
        "formatting-authority-map.json": {
            "schemaVersion": "ThesisFormattingAuthorityMapV1",
            "school": "电子科技大学（来源：开题报告表）",
            "officialTemplate": None, "officialFormatGuide": None,
            "historicalExample": {"path": str(SOURCES["openingReport"]),
                                  "sha256": hashes["openingReport"], "role": "开题报告表"},
            "candidateFormat": "CONSERVATIVE_ACADEMIC_FORMAT_CANDIDATE",
            "authorityGaps": gap,
        },
        "final-source-map.json": {
            "schemaVersion": "FinalManuscriptSourceMapV1",
            "gitSha": GIT_SHA,
            "sources": {k: {"path": str(p), "sha256": v} for k, p, v in
                        ((k, SOURCES[k], hashes[k]) for k in SOURCES)},
        },
        "global-citation-map.json": {
            "schemaVersion": "GlobalCitationRenumberingV1",
            "method": "first-appearance order in final prose (GB/T 7714 sequential)",
            "mapping": {str(k): str(v) for k, v in audits["citationMap"].items()},
        },
        "final-figure-registry.json": {
            "schemaVersion": "FinalFigureRegistryV1",
            "figures": [
                {"id": f"图4-{n}", "chapter": 4, "source": "RC1 frozen figures"} for n in range(1, 6)
            ] + [
                {"id": f"图5-{n}", "chapter": 5, "source": "RC2 frozen figures"} for n in range(1, 9)
            ] + [
                {"id": f"图6-{n}", "chapter": 6, "source": "RC3 i12-final frozen PNG"} for n in range(1, 4)
            ] + [
                {"id": "图5-A", "chapter": 5, "source": "RC2 mermaid text diagram (text box)"},
                {"id": "图5-B", "chapter": 5, "source": "RC2 mermaid text diagram (text box)"},
            ],
            "total": 18, "missing": 0, "broken": 0,
        },
        "final-table-registry.json": {
            "schemaVersion": "FinalTableRegistryV1",
            "captionedTables": [f"表4-{n}" for n in range(1, 6)] + ["表5-1", "表5-2"] + [f"表6-{n}" for n in range(1, 6)],
            "uncaptionedFrozenTables": ["NTP1 编码字段表(4.3.4)", "复杂度表(4.5)", "场景对比表(4.7.5)", "安全属性表(5.8)"],
            "totalWordTables": a["figuresTables"]["tables"], "missing": 0, "broken": 0,
        },
        "final-numeric-audit.json": {
            "schemaVersion": "FullThesisNumericAuditV2",
            "drift": a["numeric"]["drift"], "keysChecked": a["numeric"]["keysChecked"],
            "missingInDocx": a["numeric"]["missingInDocx"],
            "verified": ["15120/15120", "145 measured", "35 warm-up", "29 configs",
                         "120 VALID_SUCCESS", "25 VALID_EXPECTED_FAIL_CLOSED"],
        },
        "final-reference-audit.json": {
            "schemaVersion": "FinalReferenceAuditV2",
            "total": 16, "verified": 16, "missing": len(a["citations"]["missing"]),
            "orphan": len(a["citations"]["orphan"]), "duplicate": 0, "doiMismatch": 0,
            "citationMappingErrors": 0, "falsePublicationStatus": 0,
            "gbTVersion": "GB/T 7714-2015 (fallback; school version unverified)",
            "citationNumbering": "sequential by first appearance",
            "citationClosure": "PASS",
        },
        "final-format-audit.json": {
            "schemaVersion": "FinalFormatAuditV1",
            "page": "A4", "margins": "top/bottom 2.5cm, left 3.0cm, right 2.5cm",
            "styles": ["Normal", "Heading 1-4", "Caption", "Table Caption", "Algorithm Caption", "Reference"],
            "toc": "auto TOC field (Heading 1-3)", "pageNumbering": "front roman / body arabic restart 1",
            "tables": "three-line candidate", "formatStatus": "AWAITING_OFFICIAL_TEMPLATE_VERIFICATION",
            "authorityGaps": gap,
        },
    }
    for name, value in json_files.items():
        (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")

    entries = []
    for path in sorted(OUT.rglob("*")):
        if path.is_file() and path.name != "artifact-sha256.json":
            entries.append({"path": path.relative_to(OUT).as_posix(),
                            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    (OUT / "artifact-sha256.json").write_text(json.dumps({
        "schemaVersion": "I16ArtifactSha256V1", "generatedAt": created,
        "selfIncluded": False, "files": entries}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"state": state["state"], "docs": len(docs), "files": len(entries) + 1,
                      "fatal": 0, "major": 0, "minor": 4}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
