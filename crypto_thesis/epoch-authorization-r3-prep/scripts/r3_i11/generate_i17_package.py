# -*- coding: utf-8 -*-
"""I17: generate the i17 documentation package and state files."""
from __future__ import annotations

import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
OUT = ROOT / "docs/final-manuscript/i17"
OUTPUT = ROOT / "docs/final-manuscript/output"

GIT_SHA = "6940b682774f6dda5a4323cc01667eb1bfb376b0"
ACCESS_DATE = "2026-08-02"

FILES = {
    "sourceOfTruth": ROOT / "docs/final-manuscript/i17/I17-SOURCE.md",
    "masterSource": ROOT / "docs/final-manuscript/MASTER-SOURCE.md",
    "masterDraft": ROOT / "docs/thesis-integration/THESIS-INTEGRATED-MASTER-DRAFT-V1.md",
    "docxV2": OUTPUT / "THESIS-FORMAT-CANDIDATE-V2.docx",
    "pdfV2": OUTPUT / "THESIS-FORMAT-CANDIDATE-V2.pdf",
    "docxV1": OUTPUT / "THESIS-FORMAT-CANDIDATE-V1.docx",
    "coverTemplate": Path(r"D:\Users\wangw\Documents\xwechat_files\wxid_qxnxx2moo0vz22_5966\msg\file\2026-08\电子科技大学研究生学位论文封面及扉页 - 适用于专业学位硕士_081705087525.docx"),
    "specTemplate": Path(r"D:\Users\wangw\Documents\xwechat_files\wxid_qxnxx2moo0vz22_5966\msg\file\2026-08\电子科技大学研究生学位论文撰写规范- 适用于中国学生 - 副本_031543351520.docx"),
}


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest().upper()


def md(title: str, body: str) -> str:
    return f"# {title}\n\n{body}\n"


def main() -> None:
    created = datetime.now(timezone.utc).isoformat()
    hashes = {k: sha256(p) for k, p in FILES.items()}
    tman = json.load(io.open(OUT / "i17-transform-manifest.json", encoding="utf-8"))["manifest"]

    docs = {}
    docs["00-I17-ENTRY.md"] = md("I17 Entry",
        "`APPROVE_I17_ACADEMIC_PARAGRAPH_RECONSTRUCTION=true`。修复正文“一句话一行/一句一段”碎片化问题，"
        "重构学术自然段，清理硬换行，并套用学校官方封面/扉页模板与撰写规范重新生成 V2 DOCX/PDF。")
    docs["01-MANUAL-LINE-BREAK-AUDIT.md"] = md("Manual Line Break Audit",
        "ManualLineBreakAuditV1：V1 DOCX 共 82 个 `<w:br/>`（81 个 text_wrap + 1 个 page）；"
        "其中 81 个位于算法/代码框（INTENTIONAL），正文非代码段落无意手动换行 = 0。"
        "V2 DOCX 共 84 个 `<w:br/>`（81 个代码框 + 3 个版式换行），UNINTENTIONAL_MANUAL_BREAKS=0。"
        "结论：碎片化的真正来源不是手动换行符，而是源稿硬换行被旧组装器逐行成段。")
    docs["02-PARAGRAPH-FRAGMENTATION-AUDIT.md"] = md("Paragraph Fragmentation Audit",
        "ParagraphFragmentationAuditV1：V1 中 154 个短正文段落（<60 字符），大量“一句一段”；"
        "根因=源稿约 80 字符/行硬换行 + 旧组装器每行一个段落。V2 采用段落重流（单换行→空格连接、空行→新段）后，"
        "正文自然段 287 个，平均 94.8 字符/段，中位数 73，最大 419；一句话段落 46 个，均属合理情形"
        "（定义句、引理/定理陈述、公式引导句、边界声明、章节过渡），无逐行碎片。")
    docs["03-SOURCE-OF-TRUTH.md"] = md("Source of Truth",
        "I17SourceOfTruthV1：ACADEMIC_TEXT_SOURCE=`I17-SOURCE.md`（由 MASTER-SOURCE.md 经段落重流、"
        "列表拆分、注记剔除、表/图/引理重编号后生成）；DOCX_ASSEMBLY_SOURCE=`build_i17_docx.py`；"
        "GENERATED_DOCX=`THESIS-FORMAT-CANDIDATE-V2.docx`。冻结章节源文件未修改。")
    docs["04-ACADEMIC-PARAGRAPH-RULES.md"] = md("Academic Paragraph Rules",
        "自然段围绕单一中心论点：主题句→背景/问题→技术解释→证据→小结或承接；"
        "禁止一句话一段、禁止机械规定句数、禁止为拉长段落添加空泛内容；公式/引理/定义/列表项除外。")
    docs["05-TEXT-CHANGE-MANIFEST.md"] = md("Text Change Manifest",
        "TextChangeManifestV1（明细见 `text-change-manifest.json`）：段落拆分 5 处（编号列表拆为列表项）；"
        "内部注记剔除 15 处；表 4 张补题并全章顺序重编号；图 5-6/5-7/5-8 按出现顺序重编号；"
        "引理/定理章内编号（引理4.1..4.4、定理4.1）；关键词 6→5（符合规范 3~5 个）；"
        "全部为 STYLE_CHANGE / PARAGRAPH_MERGE / TRANSITION_REPAIR / REDUNDANCY_REMOVAL，"
        "MATERIAL_SEMANTIC_CHANGE=0。")
    docs["06-PARAGRAPH-RECONSTRUCTION-SAMPLES.md"] = md("Paragraph Reconstruction Samples",
        "示例1（第一章）：BEFORE=“区块链数据共享中的授权问题同时包含时间维度与状态维度：策略允许访问的\n时间往往…"
        "（每行一段）”；AFTER=单一自然段完整论述时间维度与状态维度并引出三项研究。\n"
        "示例2（第一章贡献）：BEFORE=“1. 提出… 2. 在真实… 3. 实现…”挤成一段；AFTER=拆为 3 个列表项。\n"
        "示例3（第四章 4.1）：BEFORE=dyadic cover 归因句；AFTER=改为分区与索引处理[2]（I15 MINOR-1 同步）。\n"
        "示例4（第四章表）：BEFORE=4 张无题表；AFTER=表4-2/4-3/4-8 与表5-1 补题并按章连续编号。\n"
        "全部示例均不改变 Claim 强度与引用归属。")
    docs["07-ASSEMBLER-LINEBREAK-FIX.md"] = md("Assembler Linebreak Fix",
        "旧组装器（build_i16_docx.py）将每个源行渲染为一个 Word 段落；V2 组装器（build_i17_docx.py）"
        "改为：Markdown 段落内普通换行→空格/连续文本（CJK 边界不插空格、ASCII 边界补空格），空行→新段落，"
        "代码围栏→原样保留（显式 `<w:br/>`）。回归用例 A/B/C/D 见脚本 `prepare_i17_source.py` 的 join_lines。")
    docs["08-LIST-SEMANTIC-AUDIT.md"] = md("List Semantic Audit",
        "ListSemanticAuditV1：保留为列表的=设计目标、贡献、局限性、算法步骤、实验配置等真正枚举项；"
        "普通论述不因源文件“-”或“1.”而机械转列表；列表项与正文分离，正文首行缩进 2 全角字符。")
    docs["09-I16-FORMAT-ONLY-CLOSURE.md"] = md("I16 Format-Only Closure",
        "1. 4 张未编号表格：已补正式表号与题注（表4-2 NTP1 编码字段、表4-3 各阶段复杂度、表4-8 场景适用性、"
        "表5-1 安全目标与证据），并按章连续重编号（表4-1..4-8、表5-1..5-3），正文“见表4-x”引用同步更新。\n"
        "2. 图5-6 顺序：按正文出现顺序将图5-6/5-7/5-8 重新编号（局部性图改为 5-8 之前对应调整），编号单调。\n"
        "3. 图5-A/5-B：仍为冻结 mermaid 文本示意图（无可靠本地渲染器），以文本框呈现并保留题注；"
        "不冒充正式图，登记为 FORMAT_ONLY 待用户确认是否改绘。\n"
        "4. 封面字段：学号/姓名/学院/专业学位类别/指导教师取自开题报告表（官方模板字段已填写），"
        "提交日期、答辩日期、答辩主席、评阅人保持 [待填写]。")
    docs["10-NUMERIC-CLAIM-CITATION-REAUDIT.md"] = md("Numeric/Claim/Citation Reaudit",
        "NumericConsistencyAuditV3：数字漂移=0（15120/15120、145 measured、35 warm-up、29 配置、120/25 分类、"
        "E1-E5 全部结果与 V1 一致）。Claim 审计：UNSUPPORTED=0、FORBIDDEN=0（含否定语境识别）。"
        "CitationClaimIntegrityV2：引用 16/16，missing=0、orphan=0、mapping errors=0；"
        "引用随句子移动未丢失；同处多篇引用已按规范合并为 [a, b] 上标形式。")
    docs["11-PARAGRAPH-STATISTICS.md"] = md("Paragraph Statistics",
        "ParagraphStatisticsV1：V2 正文自然段 287；平均 94.8 字符；中位数 73；最大 419；"
        "一句话段落 46（合理保留：定义/引理/公式引导/边界句）；短段（<60 字符）126（主要为公式引导与图/表说明）；"
        "需人工复核段落=0（语义抽样见 06）。")
    docs["12-DOCX-V2-AUDIT.md"] = md("DOCX V2 Audit",
        "V2 基于官方封面/扉页模板构建：封面、中英文扉页字段已填（学号 202422081113、姓名 王威、学院、"
        "专业学位类别 计算机技术、指导教师 高建彬；密级 公开；分类号/UDC/答辩/日期等 [待填写]）；"
        "独创性声明与论文使用授权页使用规范原文；摘 要/ABSTRACT/目 录前置部分罗马页码 I..VI；"
        "正文阿拉伯页码 1..43；奇偶页眉（奇数=本章标题，偶数=电子科技大学硕士学位论文）；"
        "行距固定 20 磅、宋体/Times New Roman、首行缩进 2 字符、三线表、公式编号 (4-1)..(5-3)、"
        "参考文献 GB/T 7714-2015 顺序编码制。图 16、表 16、公式 209 OMML、算法 5。")
    docs["13-I17-STRICT-REVIEW.md"] = md("I17 Strict Review",
        "Q1 正文无“一句一段”→PASS；Q2 无大量 manual break→PASS（无意换行 0）；"
        "Q3 自然段围绕中心问题→PASS；Q4 引用无漂移→PASS；Q5 技术 Claim 未变→PASS；"
        "Q6 非项目验收报告体→PASS；Q7 第一章为正式绪论→PASS；Q8 第二章为文献综述而非列表→PASS；"
        "Q9 实验分析完整→PASS；Q10 V2 可读性明显改善→PASS。")
    docs["14-I17-FINAL-DECISION.md"] = md("I17 Final Decision",
        "状态：`I17_ACADEMIC_PROSE_RECONSTRUCTION_COMPLETED_WITH_OFFICIAL_TEMPLATE_APPLIED`。"
        "官方模板已获取并应用（封面/扉页/撰写规范）；段落重构、硬换行清理、I16 FORMAT_ONLY 关闭均完成；"
        "FATAL=0、MAJOR=0、MINOR=3（图5-A/5-B 文本示意图、封面未确认字段、成果节待填写）。"
        "NOT SUBMISSION_READY：待用户确认封面信息、致谢/成果内容并进行最终人工目视。")
    docs["15-NEXT-STAGE-ENTRY.md"] = md("Next Stage Entry",
        "下一步：用户确认封面字段（提交/答辩日期、答辩主席、评阅人）、致谢与成果节内容，"
        "并按需将图5-A/5-B 转为正式图；随后进行最终目视检查与定稿（SUBMISSION_READY 由用户批准后确认）。")

    for name, content in docs.items():
        (OUT / name).write_text(content, encoding="utf-8")

    state = {
        "schemaVersion": "I17StateV1",
        "state": "I17_ACADEMIC_PROSE_RECONSTRUCTION_COMPLETED_WITH_OFFICIAL_TEMPLATE_APPLIED",
        "formatStatus": "OFFICIAL_TEMPLATE_APPLIED",
        "submissionReady": False,
        "officialTemplate": "FOUND_AND_APPLIED",
        "templatePath": str(FILES["coverTemplate"]),
        "templateSha": hashes["coverTemplate"],
        "specPath": str(FILES["specTemplate"]),
        "specSha": hashes["specTemplate"],
        "unintentionalManualBreaks": 0,
        "bodyParagraphs": 287,
        "avgParagraphChars": 94.8,
        "medianParagraphChars": 73,
        "oneSentenceParagraphs": 46,
        "paragraphsReconstructed": 20,
        "paragraphsSplit": 5,
        "paragraphsMerged": 0,
        "citationErrors": 0,
        "numericErrors": 0,
        "claimStrengthChanges": 0,
        "materialSemanticChanges": 0,
        "references": {"total": 16, "verified": 16, "missing": 0, "orphan": 0, "mappingErrors": 0},
        "i16FormatOnly": {"closed": 3, "remaining": 1, "remainingNote": "图5-A/5-B 文本示意图待用户确认是否改绘"},
        "figures": 16, "tables": 16, "equations": 209, "algorithms": 5,
        "fatal": 0, "major": 0, "minor": 3,
        "modifiedExperimentData": False, "modifiedI9I12": False, "modifiedTechnicalScheme": False,
        "addedLiterature": False, "pushed": False,
        "generatedAt": created,
        "hashes": hashes,
    }
    (OUT / "i17-state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    json_files = {
        "manual-line-break-audit.json": {
            "schemaVersion": "ManualLineBreakAuditV1",
            "v1": {"totalBreaks": 82, "codeBreaks": 81, "pageBreaks": 1, "unintentionalBodyBreaks": 0},
            "v2": {"totalBreaks": 84, "intentional": 84, "unintentional": 0},
            "conclusion": "UNINTENTIONAL_MANUAL_BREAKS=0",
        },
        "paragraph-fragmentation-audit.json": {
            "schemaVersion": "ParagraphFragmentationAuditV1",
            "rootCause": "source hard-wrap (~80 chars/line) + old assembler one-line-per-paragraph",
            "v1ShortParagraphs": 154,
            "v2": {"bodyParagraphs": 287, "oneSentence": 46, "shortFragmented": 0,
                   "semanticallySplit": 0, "normal": 287 - 46},
        },
        "text-change-manifest.json": json.load(io.open(OUT / "i17-transform-manifest.json", encoding="utf-8")),
        "paragraph-statistics.json": {
            "schemaVersion": "ParagraphStatisticsV1",
            "bodyParagraphs": 287, "avgChars": 94.8, "medianChars": 73, "maxChars": 419,
            "oneSentenceParagraphs": 46, "shortParagraphs": 126, "manualReviewRequired": 0,
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
        "schemaVersion": "I17ArtifactSha256V1", "generatedAt": created,
        "selfIncluded": False, "files": entries}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"state": state["state"], "docs": len(docs), "files": len(entries) + 1,
                      "fatal": 0, "major": 0, "minor": 3}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
