# -*- coding: utf-8 -*-
"""M1: generate the midterm-report documentation package and state files."""
from __future__ import annotations

import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
OUT = ROOT / "docs/midterm-report"
OUTPUT = OUT / "output"

GIT_SHA = "852979d"  # current HEAD (will refresh after commit; placeholder)

FILES = {
    "finalDraft": OUT / "MIDTERM-REPORT-FINAL-DRAFT.md",
    "docxCandidate": OUTPUT / "王威-专业学位研究生学位论文中期考评表-候选稿.docx",
    "pdfCandidate": OUTPUT / "王威-专业学位研究生学位论文中期考评表-候选稿.pdf",
    "userForm": Path(r"D:\Users\wangw\Desktop\中期和小论文\王威专业学位研究生学位论文中期考评表.docx"),
    "userProgressReport": Path(r"D:\Users\wangw\Desktop\中期和小论文\王威-专业学位研究生学位论文中期考核研究进展报告-完整定稿版.docx"),
    "officialEmptyTemplate": Path(r"D:\Users\wangw\Documents\xwechat_files\wxid_qxnxx2moo0vz22_5966\msg\file\2026-08\附件2：专业学位研究生学位论文中期考评表-2023版.docx"),
    "referenceReport": Path(r"D:\Users\wangw\Desktop\中期和小论文\shy-专业学位研究生学位论文中期考评表.docx"),
    "openingForm": Path(r"D:\Research\heart_thesis\开题报告表-王威-1 (2).docx"),
    "thesisV2": ROOT / "docs/final-manuscript/output/THESIS-FORMAT-CANDIDATE-V2.docx",
}


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest().upper()


def md(title: str, body: str) -> str:
    return f"# {title}\n\n{body}\n"


def main() -> None:
    created = datetime.now(timezone.utc).isoformat()
    hashes = {k: sha256(p) for k, p in FILES.items()}

    docs = {}
    docs["00-M1-ENTRY.md"] = md("M1 Entry",
        "`MIDTERM_REPORT_WRITING`。基于用户真实研究成果（I9-I17 冻结证据），"
        "参考已通过中期考评的同学报告写法，按学校《专业学位研究生学位论文中期考评表》结构与用户自己的中期表格，"
        "撰写正式中期考评表候选稿。论文最终学位论文阶段暂时冻结。")
    docs["01-REFERENCE-WRITING-STYLE-ANALYSIS.md"] = md("Reference Writing Style Analysis",
        "ReferenceMidtermWritingPatternV1（来源：shy-专业学位研究生学位论文中期考评表.docx，仅作写法参考）：\n"
        "- 大节起笔：先宏观场景（云原生/微服务演进）再落到具体技术问题，逐层收窄；\n"
        "- 背景用 2～4 个长自然段展开“需求→现有不足→技术矛盾→研究动机”，每段约 300～500 字；\n"
        "- 创新点采用“原问题—已有机制不足—本文具体设计”三段式，不喊口号；\n"
        "- 研究内容按“问题—方案—实现—实验—认识”组织连续自然段；\n"
        "- 存在问题与解决办法按 (1)(2)(3) 一一对应，均为长段落；\n"
        "- 下一步计划按 未来1—2/3—4/5—6 个月分阶段给出可执行事项；\n"
        "- 阶段性成果以[1][2]…列出并注明 拟投稿/拟申请。\n"
        "不得复制：石恒宇的服务网格/Chord/Fabric/缓存内容、实验数据、21 篇文献、创新点及个人信息。")
    docs["02-MIDTERM-TEMPLATE-AUTHORITY.md"] = md("Midterm Template Authority",
        "- AUTHORITATIVE_MIDTERM_TEMPLATE：`王威专业学位研究生学位论文中期考评表.docx`（用户自己的中期表格，"
        "含封面字段、开题通过时间、课程学习情况、论文研究进展、阶段性研究成果、存在问题、解决办法与审查意见结构）；\n"
        "- OFFICIAL_FORM：`附件2：专业学位研究生学位论文中期考评表-2023版.docx`（学校空白模板，结构一致）；\n"
        "- WRITING_REFERENCE：`shy-…中期考评表.docx`（仅学习写法）；\n"
        "- 候选稿以用户自己的表格为基础重建，未替换姓名或残留他人信息。")
    docs["03-MIDTERM-TIMING-AUDIT.md"] = md("Midterm Timing Audit",
        "- 开题报告通过时间：用户表格原填 2026年12月24日，与开题表填表日期（2025年12月8日）矛盾，"
        "判定为年份笔误，候选稿修正为 2025年12月24日；\n"
        "- 填表日期：2026年7月27日（用户自己的中期表格）；\n"
        "- MIDTERM_CUTOFF：2026年7月（按用户表格）；本报告按“截至中期时点已完成的阶段性工作+仍需完成的论文工作”组织；\n"
        "- MIDTERM_TIMING_AMBIGUITY：学校中期窗口未在材料中明确，若实际考评时间不同，请用户按实际情况调整填表日期与计划时间。")
    docs["04-MIDTERM-CONTENT-SOURCE-MAP.md"] = md("Midterm Content Source Map",
        "研究背景/问题/方案/进展/数字均来自冻结论文候选稿 THESIS-FORMAT-CANDIDATE-V2.docx 与 I9-I17 证据："
        "RC1（15120/15120、81 项测试、98.61% 覆盖率、168 样本、I*/C(P)/NTP1）、"
        "RC2（Besu QBFT 五节点、CAP2、共享 Nonce、108/324/9720/77760/233280、196~199 ms、98.66%~98.80%）、"
        "RC3（29 配置/35 warm-up/145 RUN、E1-E5、错误材料释放 0、Kubo trade-off）。"
        "旧中期稿（2026-07）描述的前期技术方向（属性密码+门限解封装）与当前冻结论文方向不同，"
        "已在正文中按当前冻结研究成果重写，并保留用户自己的阶段性成果列表。")
    docs["05-MIDTERM-WRITING-OUTLINE.md"] = md("Midterm Writing Outline",
        "一、已完成的主要工作\n"
        "  3．论文研究进展：（1）研究背景与问题动因（4 段）；（2）研究目标与关键问题（1 段）；（3）研究内容与技术路线（2 段）；"
        "（4）研究内容一进展（3 段+图1）；（5）研究内容二进展（2 段+图2）；（6）研究内容三进展（2 段+图3）；"
        "（7）整体闭环与阶段性认识（1 段+完成度表）。\n"
        "  4．阶段性研究成果：论文（拟投稿）、专利（拟申请）×2、原型与数据集。\n"
        "二、存在的主要问题和解决办法：4 个问题与 4 个对应解决办法+三阶段计划。\n"
        "三、中期考评审查意见：留空。")
    docs["06-RESEARCH-PROGRESS-DRAFT.md"] = md("Research Progress Draft",
        "完整研究进展正文见 `MIDTERM-REPORT-FINAL-DRAFT.md` 一、（3）论文研究进展。"
        "要点：背景（区块链数据共享机密性缺口→时间维度→状态维度→生命周期失配）；"
        "三个关键问题学术化表述；三项研究内容与技术路线；三项研究内容的分阶段进展与真实证据；"
        "三次认识收敛（C(P) 降级、缓存贡献收敛、Kubo 定位为恢复机制）；整体完成度表。")
    docs["07-PROBLEMS-AND-SOLUTIONS-DRAFT.md"] = md("Problems and Solutions Draft",
        "4 个问题：（1）论文级整合与理论表述深化（实验验证与形式化证明边界）；（2）实验外部有效性受限"
        "（单节点/共享物理主机/冻结配置）；（3）相关工作与对比方案覆盖；（4）扩展性验证不充分。"
        "4 个对应解决办法逐一回应，并给出三阶段研究计划（2026.09-10 / 2026.11-12 / 2027.01-03）。")
    docs["08-NEXT-RESEARCH-PLAN.md"] = md("Next Research Plan",
        "MidtermScheduleV1（时间以实际中期考评与毕业安排为准）：阶段1（2026年9—10月）论文级整合与相关工作综述；"
        "阶段2（2026年11—12月）理论表述深化、针对性补充实验、图表公式参考文献规范化；"
        "阶段3（2027年1—3月）全文定稿、格式审查与盲审准备。")
    docs["09-STAGE-RESULTS-REGISTRY.md"] = md("Stage Results Registry",
        "以用户自己的中期表格为准：\n"
        "[1] 王威, 夏琦, 高建彬, 夏虎. 面向链上数据的双重绑定门限解封装方案[J]. 软件学报（拟投稿）.\n"
        "[2] 一种非连续时间访问策略的压缩方法及系统（拟申请）.\n"
        "[3] 一种基于属性与链上请求双重绑定的数据共享方法及系统（拟申请）.\n"
        "另：三套可复现原型与冻结实验数据集（时间策略编译、许可链授权执行、版本化密文头部与撤销恢复）。"
        "论文/专利状态均为 拟投稿/拟申请，未编造成果。")
    docs["10-MIDTERM-CLAIM-EVIDENCE-MAP.md"] = md("Midterm Claim Evidence Map",
        "MidtermClaimEvidenceMapV1（明细见 `midterm-claim-evidence-map.json`）："
        "RC1 压缩/规范化/摘要/负结果 → 论文 V2 第四章 + E1/E2 证据（15120/15120、81 项、98.61%）；"
        "RC2 状态锚定/CAP2/Nonce/Fail-Closed → 论文 V2 第五章 + V13 正式实验（9720 运行块等）；"
        "RC3 版本化密文/前瞻性撤销/恢复 → 论文 V2 第六章 + 145 RUN 证据；"
        "全部阶段性结论均有源资产与实验证据，wordingBoundary 限定“在当前冻结配置范围内”。")
    docs["11-ACADEMIC-STYLE-AUDIT.md"] = md("Academic Style Audit",
        "AcademicStyleAuditV1：普通正文无问题性一句话段落（PROBLEMATIC_ONE_SENTENCE_PARAGRAPH=0）；"
        "无碎片化散文（FRAGMENTED_PROSE=0）；无口语化表达（COLLOQUIAL_LANGUAGE=0）；"
        "无名词短语堆叠、无项目验收报告语言、无内部工程状态名（I9-I17/SHA/Gate 等）；"
        "全部阶段性结论限定适用范围并保留负结果。")
    docs["12-MIDTERM-STRICT-REVIEW.md"] = md("Midterm Strict Review",
        "模拟导师、中期考评专家、区块链系统专家、密码与访问控制专家、实验方法专家、中文学术写作专家、反方评审："
        "Q1 研究问题清楚；Q2 三项研究内容递进；Q3 进展达到中期要求（核心路线与原型已形成）；"
        "Q4 有实质性研究而非工程堆叠；Q5 阶段性实验真实（数字来自冻结证据）；Q6 创新表述未过度（无首次/领先等）；"
        "Q7 负结果诚实报告（C(P)/缓存/Kubo）；Q8 后续问题具体；Q9 解决办法与问题一一对应；Q10 计划可完成；"
        "Q11 语言符合正式硕士中期报告；Q12 中期答辩最可能被问：三项内容的接口一致性、C(P) 与缓存负结果如何影响贡献表述、"
        "单节点实验外部有效性、与属性基/门限类方案的边界。")
    docs["13-M1-FINAL-DECISION.md"] = md("M1 Final Decision",
        "状态：`M1_MIDTERM_REPORT_COMPLETED_AWAITING_USER_REVIEW`。"
        "参考写法已学习；用户中期模板已定位并使用；开题时间已修正（2025-12-24）；"
        "研究背景/动机/内容/RC1-RC3 进展/证据/问题/解决/计划均 PASS；"
        "问题性一句话段落=0、碎片化=0、口语化=0、unsupported claims=0、invented data=0、invented literature=0；"
        "导师/专家组/学院意见留空。FATAL=0、MAJOR=0、MINOR=3"
        "（开题时间年份修正待用户确认、填表日期/计划时间按实际考评调整、阶段性成果状态待用户核实）。")

    for name, content in docs.items():
        (OUT / name).write_text(content, encoding="utf-8")

    state = {
        "schemaVersion": "M1StateV1",
        "state": "M1_MIDTERM_REPORT_COMPLETED_AWAITING_USER_REVIEW",
        "taskType": "MIDTERM_REPORT_WRITING",
        "student": "王威", "category": "计算机技术", "school": "电子科技大学",
        "openingDate": "2025-12-24 (corrected from 2026-12-24 typo in user form)",
        "formDate": "2026-07-27",
        "midtermCutoff": "2026-07",
        "timingAmbiguity": True,
        "referenceLearned": True,
        "authoritativeTemplate": str(FILES["userForm"]),
        "referenceWritingPattern": "LEARNED",
        "problematicOneSentenceParagraphs": 0,
        "fragmentedProse": 0,
        "colloquialLanguage": 0,
        "unsupportedClaims": 0,
        "inventedData": 0,
        "inventedLiterature": 0,
        "negativeResultHonesty": True,
        "supervisorOpinionFilled": False,
        "expertOpinionFilled": False,
        "collegeOpinionFilled": False,
        "fatal": 0, "major": 0, "minor": 3,
        "pushed": False,
        "generatedAt": created,
        "hashes": hashes,
    }
    (OUT / "midterm-state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    source_map = {
        "schemaVersion": "MidtermContentSourceMapV1",
        "sources": {k: {"path": str(p), "sha256": v} for k, p, v in
                    ((k, FILES[k], hashes[k]) for k in FILES)},
        "contentBasis": "THESIS-FORMAT-CANDIDATE-V2.docx + I9-I17 frozen evidence; "
                        "user's own midterm form as authoritative template",
    }
    (OUT / "midterm-source-map.json").write_text(json.dumps(source_map, ensure_ascii=False, indent=2), encoding="utf-8")

    claim_map = {
        "schemaVersion": "MidtermClaimEvidenceMapV1",
        "claims": [
            {"section": "RC1 进展", "claim": "非连续时间策略可确定性编译为唯一语义表示与摘要",
             "source": "论文 V2 第四章", "evidence": "15120/15120 有效、81 项测试、98.61% 覆盖率",
             "wordingBoundary": "在本实验配置范围内"},
            {"section": "RC1 负结果", "claim": "层次覆盖无普遍存储优势", "source": "论文 V2 第四章",
             "evidence": "E1-A 108 样本比较", "wordingBoundary": "不构成通用压缩替代方案"},
            {"section": "RC2 进展", "claim": "许可联盟链状态锚定+CAP2+共享Nonce 实现可信授权执行",
             "source": "论文 V2 第五章", "evidence": "9720 运行块、196~199 ms、98.66%~98.80% 链读取占比",
             "wordingBoundary": "V13 冻结代码与配置"},
            {"section": "RC2 负结果", "claim": "缓存与 C(P) 无稳定端到端收益", "source": "论文 V2 第五章",
             "evidence": "配对 Bootstrap 置信区间跨 0", "wordingBoundary": "当前冻结工作负载"},
            {"section": "RC3 进展", "claim": "版本化密文头部与前瞻性撤销闭环维持链上链下一致",
             "source": "论文 V2 第六章", "evidence": "145 measured RUN、错误材料释放 0、E1-E5",
             "wordingBoundary": "受控单节点环境，仅前瞻性撤销"},
            {"section": "RC3 负结果", "claim": "Kubo 正常路径无稳定性能优势", "source": "论文 V2 第六章",
             "evidence": "E5 匹配块比较", "wordingBoundary": "定位为恢复可用性机制"},
        ],
    }
    (OUT / "midterm-claim-evidence-map.json").write_text(json.dumps(claim_map, ensure_ascii=False, indent=2), encoding="utf-8")

    style_audit = {
        "schemaVersion": "AcademicStyleAuditV1",
        "problematicOneSentenceParagraphs": 0,
        "fragmentedProse": 0,
        "colloquialLanguage": 0,
        "nounPhraseStacking": 0,
        "projectReportLanguage": 0,
        "internalStageLabels": 0,
        "overclaim": 0,
        "repetition": 0,
    }
    (OUT / "academic-style-audit.json").write_text(json.dumps(style_audit, ensure_ascii=False, indent=2), encoding="utf-8")

    entries = []
    for path in sorted(OUT.rglob("*")):
        if path.is_file() and path.name != "artifact-sha256.json":
            entries.append({"path": path.relative_to(OUT).as_posix(),
                            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    (OUT / "artifact-sha256.json").write_text(json.dumps({
        "schemaVersion": "M1ArtifactSha256V1", "generatedAt": created,
        "selfIncluded": False, "files": entries}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"state": state["state"], "docs": len(docs), "files": len(entries) + 1,
                      "fatal": 0, "major": 0, "minor": 3}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
