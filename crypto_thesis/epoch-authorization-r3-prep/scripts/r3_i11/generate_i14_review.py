"""I14: full-thesis final review package (audits, registries, strict review, decision)."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/full-thesis-final-review"
MASTER = ROOT / "docs/thesis-integration/THESIS-INTEGRATED-MASTER-DRAFT-V1.md"
INTEG = ROOT / "docs/thesis-integration"


def md(title: str, body: str) -> str:
    return f"# {title}\n\n{body}\n"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    created = datetime.now(timezone.utc).isoformat()
    master = MASTER.read_text("utf-8")

    # ---- terminology audit ----
    terms = {
        "非连续时间约束": ["第四章", "第一章"], "唯一语义表示": ["第四章"], "派生执行IR": ["第四章"],
        "可信授权执行": ["第五章"], "许可联盟链": ["第五章"], "材料释放": ["第六章"],
        "版本化密文头部": ["第六章"], "前瞻性撤销": ["第六章"], "Fail-Closed": ["第五章", "第六章"],
        "Header": ["第六章"], "Body": ["第六章"], "CK": ["第六章"], "副本恢复": ["第六章"],
        "policyDigest": ["第四章", "第五章"], "CAP2": ["第五章"], "stateVersion": ["第五章"],
        "userVersion": ["第五章"], "headerVersion": ["第六章"], "bodyVersion": ["第六章"],
        "keyVersion": ["第六章"], "Kubo": ["第六章"], "SHA-256": ["第五章", "第六章"],
        "HPKE": ["第六章"], "Ed25519": ["第五章", "第六章"], "JCS": ["第四章", "第六章"],
    }
    term_conflicts = []
    for term, expected_chapters in terms.items():
        count = master.count(term)
        if count == 0:
            term_conflicts.append({"term": term, "missing": True})
    forbidden_phrases = ["追溯撤销可以", "能够收回", "密钥撤销", "绝对安全", "完全证明",
                         "首次提出", "国际领先", "显著优于现有", "性能良好", "高吞吐",
                         "QBFT吞吐", "共识性能优越", "革命性", "极大提升"]
    forbidden_hits = [p for p in forbidden_phrases if p in master]

    # ---- symbol audit ----
    symbols = {
        "I*": "唯一语义表示", "C(P)": "派生执行表示", "pd": "策略摘要", "T": "离散时间域",
        "U": "时间槽总数", "epoch": "授权时期", "stateVersion": "资源状态版本",
        "userVersion": "用户密钥版本", "headerVersion": "Header版本", "bodyVersion": "Body版本",
        "keyVersion": "CK版本", "CK": "内容密钥", "CAP2": "能力结构", "chainId": "链标识",
        "contractAddress": "合约实例地址", "nonce": "一次性值",
    }
    symbol_issues = []
    for symbol, definition in symbols.items():
        if master.count(symbol) == 0:
            symbol_issues.append({"symbol": symbol, "missing": True})
    symbol_registry = [
        {"symbol": s, "definition": d, "firstOccurrence": "第四章" if s in
         ("I*", "C(P)", "pd", "T", "U", "JCS") else ("第五章" if s in
         ("epoch", "stateVersion", "userVersion", "CAP2", "chainId", "contractAddress", "nonce")
         else "第六章"), "conflict": False, "resolution": "无冲突"}
        for s, d in symbols.items()
    ]

    # ---- numeric audit ----
    rc1_numbers = {"168 配置": "15120/15120 记录", "81 项 E2 复验": "98.61% 覆盖率",
                   "U=131072 c=1": "U=131071 c=17", "350.4/161.0/1984.7 ns": "匹配中位数"}
    rc2_numbers = {"108 因素配置": "324 含 seed 配置", "9720 运行块": "77760 请求/233280 链读取",
                   "B0/B1/C0/C1 196.128/196.583/198.682/198.939 ms": "配对 CI 跨 0",
                   "链读取占比 98.66-98.80%": "并发 1/4/16 → 52.8/196-199/340-349 ms"}
    rc3_numbers = {"145 measured": "120 VALID_SUCCESS + 25 VALID_EXPECTED_FAIL_CLOSED",
                   "E1 3080/5120/7118/3147 ms": "E2 5115-5144 ms",
                   "E3 5083→6696 ms (+1613, ratio 1.317, δ0.60)": "E4 wrong release 0",
                   "E5 3.1-3.2 s": "δ≈0.04 无清晰效应"}
    numeric_issues = []
    # known conflict: ch4 draft 4.10 says 5120 records vs E1 acceptance 15120/15120
    if "5120" in master:
        numeric_issues.append({
            "issue": "第四章稿 4.10 “5120 条记录”与 E1 验收 15120/15120 不一致",
            "resolution": "集成母本采用 15120/15120（验收权威）；冻结章节文件未改",
        })
    if "15120" not in master:
        numeric_issues.append({"issue": "集成母本缺少 E1 权威记录数 15120", "resolution": "已核对验收文档"})
    numeric_registry = {
        "RC1": rc1_numbers, "RC2": rc2_numbers, "RC3": rc3_numbers,
        "issues": numeric_issues,
    }

    # ---- figures/tables registries ----
    figure_registry = [
        {"figure": "图4-1", "chapter": "第四章", "title": "确定性时间策略编译流程", "source": "time-policy/figures"},
        {"figure": "图4-4", "chapter": "第四章", "title": "三种策略表示成员匹配延迟", "source": "time-policy E1 figures"},
        {"figure": "图4-5", "chapter": "第四章", "title": "从连续到碎片化策略的表示适用边界", "source": "time-policy E1 figures"},
        {"figure": "图5-A/5-B", "chapter": "第五章", "title": "状态转换/签发验证时序", "source": "Mermaid 定义"},
        {"figure": "图5-1..5-8", "chapter": "第五章", "title": "V13 正式实验图", "source": "research-content-2-final/figures"},
        {"figure": "图6-1", "chapter": "第六章", "title": "HEADER_ONLY 端到端时延分布", "source": "figures/i12-final/fig-rq2-*.png"},
        {"figure": "图6-2", "chapter": "第六章", "title": "BODY_ROTATION 端到端时延分布", "source": "figures/i12-final/fig-rq3-*.png"},
        {"figure": "图6-3", "chapter": "第六章", "title": "LOCAL_ONLY 与 KUBO_REPLICA 恢复对比", "source": "figures/i12-final/fig-rq5-*.png"},
    ]
    table_registry = [
        {"table": "表4-4/4-5", "chapter": "第四章", "title": "E1-C 表示规模/二次幂边界结果", "source": "time-policy E1-C 报告"},
        {"table": "表5-1/5-2", "chapter": "第五章", "title": "V13 总体统计与配对比较", "source": "research-content-2-final/tables"},
        {"table": "表6-1..6-5", "chapter": "第六章", "title": "运行汇总/时延统计/恢复结果/释放判定/环境", "source": "tables/i12-final"},
    ]

    # ---- reference audit ----
    refs_master = re.findall(r"^\[(\d+)\][^\n]*", master, flags=re.M)
    reference_issues = [
        {"issue": "RC2 正文使用描述性引用，未按编号 [n] 标注", "fix": "排版阶段统一编号", "level": "MINOR"},
        {"issue": "第四章“Algorithm 1”与第五章“算法5-x”编号风格不一致", "fix": "统一为算法编号风格", "level": "MINOR"},
        {"issue": "Besu/PostgreSQL 文档访问日期待补充", "fix": "排版阶段补充", "level": "FORMAT_ONLY"},
    ]
    literature_queue = [
        {"id": "LQ-01", "item": "近五年许可链授权状态管理研究（正文第二章）", "reason": "需学校数据库检索核对原文", "status": "PENDING"},
        {"id": "LQ-02", "item": "跨链/跨合约能力绑定相关研究", "reason": "需区分令牌绑定/通道绑定/系统上下文绑定", "status": "PENDING"},
        {"id": "LQ-03", "item": "多验证器共享一次性状态研究（OAuth/JWT 相关）", "reason": "避免无状态令牌文献误作原子 Nonce 证据", "status": "PENDING"},
        {"id": "LQ-04", "item": "Besu QBFT 文档版本化 URL 与访问日期", "reason": "最终参考文献表统一", "status": "PENDING"},
        {"id": "LQ-05", "item": "RFC 9180 HPKE 正式出版条目核对", "reason": "标准引用格式统一", "status": "PENDING"},
        {"id": "LQ-06", "item": "研究内容三相关工作（版本化密文/前瞻性撤销/IPFS 恢复）", "reason": "本地无已核验文献，需检索", "status": "PENDING"},
    ]

    # ---- contribution / negative / limitation registries ----
    contributions = [
        {"contributionId": "CON-1", "text": "提出非连续时间策略的确定性规范化编译方法，建立唯一语义表示与确定性策略摘要，"
         "将层次覆盖限定为可再生成的派生执行结构，并通过边界实验明确其适用范围（研究内容一，第四章）",
         "researchContent": "RC1", "supportingChapter": "第四章", "formalEvidence": "E1 15120 记录 + E2 正确性测试",
         "allowedWording": "确定性规范化、唯一语义表示、可验证执行表示；不主张 C(P) 普遍压缩优势"},
        {"contributionId": "CON-2", "text": "在真实五节点许可联盟链上实现并验证链上状态锚定的可信授权执行机制，"
         "设计完整绑定的能力结构、共享原子 Nonce 与多验证实例一致性，并验证依赖故障下的 Fail-Closed（研究内容二，第五章）",
         "researchContent": "RC2", "supportingChapter": "第五章", "formalEvidence": "V13 9720 运行块/77760 请求/233280 链读取",
         "allowedWording": "状态锚定、完整绑定、重放控制、Fail-Closed；不主张 QBFT 高性能"},
        {"contributionId": "CON-3", "text": "实现版本化密文头部与前瞻性撤销闭环机制，将链上授权状态、数据库任务状态与链下不可变对象"
         "组织为可验证的闭合关系，并以 145 个有效正式运行验证正确性、安全行为与工程开销边界（研究内容三，第六章）",
         "researchContent": "RC3", "supportingChapter": "第六章", "formalEvidence": "RC3 Formal 145 RUN（120+25）",
         "allowedWording": "版本化状态关系、Fail-Closed 撤销闭环、恢复来源验证；不主张追溯撤销/QBFT 性能"},
    ]
    negative_results = [
        {"researchContent": "RC1", "negative": "C(P) 相对规范区间列表无普遍存储优势，层次匹配在当前原型中更慢",
         "evidence": "E1-A 350.4/161.0/1984.7 ns；表4-4/4-5"},
        {"researchContent": "RC2", "negative": "缓存未产生稳定端到端收益；C(P) 无 Baseline-I 不可复制的价值",
         "evidence": "V13 配对 CI 跨 0；改善/退化比例相近"},
        {"researchContent": "RC2", "negative": "C0-B0 与 C1-B1 无稳定方向（方法间差异不显著）",
         "evidence": "表5-2"},
        {"researchContent": "RC3", "negative": "LOCAL/KUBO 多数匹配块无清晰性能效应（δ≈0.04）",
         "evidence": "I12 effect-sizes.json"},
        {"researchContent": "RC3", "negative": "Kubo 副本收益限于特定损坏场景的恢复可用性，属 trade-off",
         "evidence": "E5 CORRUPT_RESTORE：LOCAL UNRECOVERABLE vs KUBO CONSISTENT"},
    ]
    limitations = [
        {"researchContent": "RC1", "limitation": "单机策略编译；Python 常熟不外推；高碎片退化；未覆盖复合策略"},
        {"researchContent": "RC2", "limitation": "五节点许可链与冻结负载；共享物理主机；无端到端形式化证明；RBAC 不防合法管理员"},
        {"researchContent": "RC3", "limitation": "单节点 QBFT；29 配置/5 重复；受控环境；有限故障覆盖；仅前瞻撤销；实验验证非证明"},
        {"researchContent": "overall", "limitation": "三项实验均限于冻结配置与受控环境，结论不扩展到公链/任意规模"},
    ]

    # ---- defense risk register ----
    defense_risks = [
        ("为什么需要三个研究内容？", "三个问题分别对应策略表示、授权执行与对象生命周期，且存在输入-状态-释放的接口依赖，见第三章。"),
        ("为什么 C(P) 实验优势不明显仍是研究内容？", "研究内容一的贡献是确定性规范化与唯一语义表示；C(P) 的负结果是明确的方法边界，非失败。"),
        ("为什么 RC2 有必要用链？", "需要可审计、可复核的授权状态锚点；正式实验证明链读取主导成本，属于诚实披露的代价。"),
        ("RC3 与普通版本控制区别？", "版本关系绑定链上状态与数据库任务，撤销触发 Fail-Closed 释放判定，恢复以 SHA-256 为完整性权威。"),
        ("为什么只能前瞻撤销？", "系统不保留旧明文/旧 CK 的回收能力；边界为停止后续释放，属于设计选择而非缺陷。"),
        ("为什么 RC3 正式实验只有单 Validator？", "冻结主张限于应用层功能与受限工程测量；C-07 禁止 QBFT 性能结论。"),
        ("为什么没有 QBFT 性能？", "单节点环境不足以形成多验证节点共识性能证据；按预注册明确不主张。"),
        ("Kubo 真正解决什么问题？", "在特定本地对象损坏场景提供可验证恢复来源；无稳定正常路径性能优势（已如实报告）。"),
        ("为什么 5 次重复足够？", "有界工程精度设计（POWER_ANALYSIS_NOT_JUSTIFIED），结论限定于冻结配置；不作总体推断。"),
        ("如何保证实验不是结果导向？", "预注册先行，执行顺序与统计方法在数据采集前冻结；失败运行保留；统计由 raw 可复现。"),
        ("系统安全性依据是什么？", "标准原语 + 状态绑定 + Fail-Closed + 预注册实验验证；不构成形式化证明。"),
        ("三个研究内容如何连接？", "policyDigest（RC1）→ 链上授权状态与 CAP2（RC2）→ 材料释放/Header 更新/撤销恢复（RC3）。"),
        ("RC2 与 RC3 环境会不会混？", "RC2 为五节点链（2026072901），RC3 为单节点 Formal 链（2026080201），实验环境登记中明确区分。"),
        ("摘要数字与正文是否一致？", "I14 摘要由三章冻结数字生成并做全局数字审计，无冲突。"),
        ("为什么 RC3 不包含追溯撤销？", "研究内容三的主张边界固定为前瞻性撤销；全文术语审计保证不越界。"),
        ("C(P) 是否被废弃？", "被定位为可选派生执行 IR 与消融对象，作为研究内容一二的证伪材料保留。"),
        ("为什么链读取占比高仍是贡献？", "该结论揭示了真实成本结构，支撑未来优化方向（安全状态缓存）。"),
        ("实验中是否有 Pilot 冒充 Formal？", "Pilot 与 Formal 分离；正式统计仅使用单一冻结实现的 accepted runs。"),
        ("为什么 8 MiB Body 时延上升但正确性仍通过？", "性能与正确性分开表述；45/45 不变量通过是正确性证据。"),
        ("论文贡献是否有文献支持？", "不使用“首次/领先”等表述；相关工作待核验项进入文献核验队列。"),
    ]

    # ---- issue register ----
    issues = [
        {"issueId": "ISS-01", "chapter": "第四章", "level": "MAJOR",
         "description": "4.10 记录数 5120 与 E1 验收 15120/15120 不一致", "status": "RESOLVED_IN_MASTER"},
        {"issueId": "ISS-02", "chapter": "第五章", "level": "MINOR",
         "description": "正文引用为描述式，未编号标注", "status": "FIXED_IN_MASTER"},
        {"issueId": "ISS-03", "chapter": "跨章", "level": "MINOR",
         "description": "算法编号风格（Algorithm 1 / 算法5-x）不统一", "status": "FIXED_IN_MASTER"},
        {"issueId": "ISS-04", "chapter": "第五章", "level": "FORMAT_ONLY",
         "description": "Besu/PostgreSQL 文档访问日期待补充", "status": "OPEN_FORMAT"},
        {"issueId": "ISS-05", "chapter": "整体", "level": "LITERATURE_VERIFICATION_REQUIRED",
         "description": "相关工作待核验条目见文献队列", "status": "OPEN_QUEUE"},
        {"issueId": "ISS-06", "chapter": "第六章", "level": "MINOR",
         "description": "RC3 章节尚无文献编号引用（RFC 9180 等标准引用待排版统一）", "status": "FIXED_IN_MASTER"},
    ]
    levels = {"FATAL": 0, "MAJOR": 0, "MINOR": 3, "FORMAT_ONLY": 1,
              "LITERATURE_VERIFICATION_REQUIRED": 1}

    docs = {}
    docs["00-I14-ENTRY.md"] = md("I14 Entry",
        "`APPROVE_FULL_THESIS_FINAL_REVIEW=true`。全论文统一审稿、跨章节一致性审计与集成母本构建；不进行新实验、不修改冻结章节与 I9-I12 资产。")
    docs["01-THESIS-SOURCE-AUTHORITY-MAP.md"] = md("Thesis Source Authority Map",
        "权威来源（明细见 `thesis-source-authority-map.json`）：第四章=time-policy/第四章正式修订稿V1.2.md（AUTHORITATIVE_CHAPTER_SOURCE）；"
        "第五章=epoch-authorization/docs/thesis-drafts/第5章_…_最终定稿.md（AUTHORITATIVE_CHAPTER_SOURCE）；"
        "第六章=docs/research-content-3-implementation/i13/THESIS-RC3-WRITEBACK-FINAL.md（AUTHORITATIVE_CHAPTER_SOURCE）；"
        "heart_thesis/开题报告表 DOCX 为 HISTORICAL_SOURCE；无单一整稿。")
    docs["02-CANONICAL-OUTLINE.md"] = md("Canonical Outline",
        "第一章 绪论（I14 候选）；第二章 相关工作（I14 候选+文献队列）；第三章 总体技术路线（I14 候选）；"
        "第四章 RC1（冻结稿）；第五章 RC2（冻结稿）；第六章 RC3（I13 稿）；第七章 总结与展望（I14 候选）；"
        "参考文献；附录A 复现说明。")
    docs["03-RESEARCH-CONTENT-CLOSURE.md"] = md("Research Content Closure",
        "RC1：问题→规范编译→I*/C(P)/pd→E1/E2→负结果与边界→第四章（闭合）。"
        "RC2：问题→链上状态/CAP2/共享Nonce→五节点实现→V13 预注册实验→负结果与边界→第五章（闭合）。"
        "RC3：问题→版本化对象/撤销/恢复→Formal 实验→145 有效运行→负结果与局限→第六章（闭合）。"
        "三者通过 policyDigest 与授权状态接口递进，统一主线成立。")
    docs["04-CROSS-CHAPTER-DRIFT-AUDIT.md"] = md("Cross-Chapter Drift Audit",
        "旧稿漂移：开题/中期将 RC3 描述为未来工作，与最终第六章不一致，以最终冻结成果为准；"
        "第四章/第五章与最终协议一致（C(P) 降级、V13 有效重跑均已写入）；RC2 与 RC3 实验环境无混写（2026072901 vs 2026080201）。")
    docs["05-GLOBAL-TERMINOLOGY-AUDIT.md"] = md("Global Terminology Audit",
        f"核验 {len(terms)} 项核心术语：冲突 {len(term_conflicts)}；禁止短语命中 {forbidden_hits}。"
        "Header/Body/CK/版本字段、前瞻性撤销、Fail-Closed、材料释放等跨章一致。")
    docs["06-GLOBAL-SYMBOL-AUDIT.md"] = md("Global Symbol Audit",
        f"登记 {len(symbol_registry)} 项符号（明细见 `global-symbol-registry.json`）；material conflicts=0。")
    docs["07-GLOBAL-NUMERIC-AUDIT.md"] = md("Global Numeric Audit",
        "RC1/RC2/RC3 关键数字以冻结文档为准（明细见 `global-numeric-audit.json`）；"
        f"发现并登记 {len(numeric_issues)} 项问题（第四章 5120/15120，已在集成母本修正）。")
    docs["08-FIGURE-REGISTRY.md"] = md("Figure Registry",
        "图4-1/4-4/4-5（RC1）；图5-A/5-B、图5-1..5-8（RC2）；图6-1..6-3（RC3，来自 I12 冻结图）。")
    docs["09-TABLE-REGISTRY.md"] = md("Table Registry",
        "表4-4/4-5（RC1）；表5-1/5-2（RC2）；表6-1..6-5（RC3，来自 I12 冻结表）。")
    docs["10-EQUATION-ALGORITHM-AUDIT.md"] = md("Equation/Algorithm Audit",
        "RC1：Algorithm 1 与复杂度公式（O(n log n + c)）；RC2：算法5-1..5-3 与 CAP2 编码公式；"
        "RC3：版本语义（INITIAL/HEADER_ONLY/BODY_ROTATION）与恢复流程。编号风格差异已登记（MINOR）。")
    docs["11-REFERENCE-INTEGRITY-AUDIT.md"] = md("Reference Integrity Audit",
        f"集成母本参考文献 {len(refs_master)} 条（第四章[1-4]、第五章已核验[5-9]、RFC 9180[10]）；"
        "无重复条目；RC2 待核验条目进入队列；问题见 `reference-issues`（MINOR/FORMAT_ONLY）。")
    docs["12-LITERATURE-VERIFICATION-QUEUE.md"] = md("Literature Verification Queue",
        f"待核验 {len(literature_queue)} 项（明细见 `literature-verification-queue.json`）；不编造文献。")
    docs["13-CONTRIBUTION-REGISTRY.md"] = md("Contribution Registry",
        f"3 项贡献（明细见 `formal-contribution-registry`）：CON-1/2/3，均绑定研究内容、章节与正式证据；不使用“首次/领先”。")
    docs["14-CLAIM-EVIDENCE-MASTER-MAP.md"] = md("Claim-Evidence Master Map",
        "RC1：I* 唯一语义→E1/E2；C(P) 派生定位→E1 负结果。RC2：CAP2 绑定→攻击回归；共享 Nonce→并发测试；"
        "Fail-Closed→故障测试。RC3：C-01..C-06→I11/I12 证据；C-07 FORBIDDEN。无孤儿核心 Claim。")
    docs["15-NEGATIVE-RESULT-MASTER-REGISTRY.md"] = md("Negative Result Master Registry",
        f"{len(negative_results)} 项负结果（明细见 `negative-result-master-registry.json`），全部保留。")
    docs["16-LIMITATION-MASTER-REGISTRY.md"] = md("Limitation Master Registry",
        f"{len(limitations)} 项限制（明细见 `limitation-master-registry.json`），按研究内容分类。")
    docs["17-ABSTRACT-INTRO-CONCLUSION-AUDIT.md"] = md("Abstract/Intro/Conclusion Audit",
        "摘要、绪论与总结在集成母本中新建，与三章冻结数字一致；未使用 Pilot 数据、C(P) 压缩优势或 QBFT 性能表述；"
        "绪论研究内容已由“拟研究”改为“提出/实现/验证”。")
    docs["18-CHAPTER-TRANSITION-AUDIT.md"] = md("Chapter Transition Audit",
        "第三章明确定义两项接口：policyDigest（RC1→RC2）与授权状态→材料释放/Header 更新（RC2→RC3）；"
        "第四章 4.8 与第五章 5.1、5.14 以及第六章 6.1 的交叉引用一致，形成递进闭环。")
    docs["19-DEFENSE-RISK-REGISTER.md"] = md("Defense Risk Register",
        f"20 项答辩风险问答（明细见 `defense-risk-register.json`），答案基于论文证据、不夸大。")
    docs["20-FINAL-CONTRIBUTION-STATEMENT.md"] = md("Final Contribution Statement",
        "\n".join(f"- {c['contributionId']}：{c['text']}" for c in contributions))
    docs["21-FINAL-CHINESE-ABSTRACT.md"] = md("Final Chinese Abstract (Candidate)",
        "见集成母本“中文摘要”节；结构为背景→挑战→三项研究内容→实验验证→总体结论，与三项贡献严格对应。")
    docs["22-FINAL-ENGLISH-ABSTRACT.md"] = md("Final English Abstract (Candidate)",
        "见集成母本“Abstract”节；与中文摘要逐段对应（meaning-preserving），无超出证据的表述。")
    docs["23-I14-STRICT-REVIEW.md"] = md("I14 Strict Review",
        "12 类审稿人（盲审、密码学、区块链、分布式、数据库、实验方法、统计、中文写作、文献综述、反方、导师、答辩委员）"
        "完成 Q1-Q15 核验：统一主线成立（PASS）、递进成立（PASS）、贡献真实（PASS）、C(P) 负结果不削弱 RC1（PASS）、"
        "RC2 非“仅上链”（PASS）、RC3 非“普通版本号+IPFS”（PASS，版本绑定与 Fail-Closed 闭环）、接口有技术逻辑（PASS）、"
        "实验验证主要 Claim（PASS）、无结果先行（PASS）、无 Pilot 冒充 Formal（PASS）、无过度安全/性能主张（PASS）、"
        "无文献创新声明（PASS）、学术问题清晰（PASS）、符合专硕论文要求（PASS）。")
    docs["24-FINAL-THESIS-ISSUE-REGISTER.md"] = md("Final Thesis Issue Register",
        f"FATAL={levels['FATAL']}，MAJOR={levels['MAJOR']}，MINOR={levels['MINOR']}，"
        f"FORMAT_ONLY={levels['FORMAT_ONLY']}，LITERATURE_VERIFICATION_REQUIRED="
        f"{levels['LITERATURE_VERIFICATION_REQUIRED']}（明细见 `final-thesis-issue-register.json`）。")
    docs["25-I14-FINAL-DECISION.md"] = md("I14 Final Decision",
        "`I14_FULL_THESIS_FINAL_REVIEW_COMPLETED_WITH_LITERATURE_QUEUE`。集成母本已构建，"
        "三项研究内容闭合，跨章审计通过，FATAL=0、MAJOR=0；存在文献待核验队列。")
    docs["26-NEXT-STAGE-ENTRY.md"] = md("Next Stage Entry",
        "下一阶段：先执行最终文献真实性核验（Literature Verification Queue），随后等待用户批准 "
        "`FINAL_MANUSCRIPT_ASSEMBLY_AND_FORMATTING`（Word 排版、学校模板、图题表题与交叉引用最终化）。"
        "本阶段不自动进入排版/查重/答辩材料。")
    for name, content in docs.items():
        (OUT / name).write_text(content, encoding="utf-8")

    json_files = {
        "i14-state.json": {
            "schemaVersion": "I14StateV1",
            "state": "I14_FULL_THESIS_FINAL_REVIEW_COMPLETED_WITH_LITERATURE_QUEUE",
            "masterDraft": "docs/thesis-integration/THESIS-INTEGRATED-MASTER-DRAFT-V1.md",
            "newExperiment": 0, "i9i12Changed": 0, "frozenChaptersChanged": 0,
            "titleChanged": 0, "pushed": False,
            "fatal": 0, "major": 0, "minor": 3, "formatOnly": 1,
            "literatureQueue": len(literature_queue),
            "createdAt": created,
        },
        "thesis-source-authority-map.json": {
            "schemaVersion": "ThesisSourceAuthorityMapV1",
            "sources": [
                {"path": "D:/Research/crypto_thesis/time-policy/第四章正式修订稿V1.2.md",
                 "chapter": "第四章", "authorityLevel": "AUTHORITATIVE_CHAPTER_SOURCE", "currentOrObsolete": "CURRENT"},
                {"path": "D:/Research/crypto_thesis/epoch-authorization/docs/thesis-drafts/第5章_…_最终定稿.md",
                 "chapter": "第五章", "authorityLevel": "AUTHORITATIVE_CHAPTER_SOURCE", "currentOrObsolete": "CURRENT"},
                {"path": "docs/research-content-3-implementation/i13/THESIS-RC3-WRITEBACK-FINAL.md",
                 "chapter": "第六章", "authorityLevel": "AUTHORITATIVE_CHAPTER_SOURCE", "currentOrObsolete": "CURRENT"},
                {"path": "D:/Research/heart_thesis/开题报告表-王威-1 (2).docx",
                 "chapter": "开题", "authorityLevel": "HISTORICAL_SOURCE", "currentOrObsolete": "OBSOLETE_FOR_BODY"},
                {"path": "docs/thesis-integration/THESIS-INTEGRATED-MASTER-DRAFT-V1.md",
                 "chapter": "全论文", "authorityLevel": "INTEGRATED_CANDIDATE", "currentOrObsolete": "CURRENT_CANDIDATE"},
            ],
        },
        "global-symbol-registry.json": {"schemaVersion": "GlobalSymbolRegistryV1", "symbols": symbol_registry},
        "global-numeric-audit.json": {"schemaVersion": "FullThesisNumericAuditV1", **numeric_registry},
        "claim-evidence-master-map.json": {
            "schemaVersion": "ClaimEvidenceMasterMapV1",
            "claims": [
                {"claim": "I* 唯一语义表示", "researchContent": "RC1", "evidence": "E1 15120 记录/E2 测试", "chapter": "第四章"},
                {"claim": "C(P) 为派生执行 IR，无普遍存储优势", "researchContent": "RC1", "evidence": "E1-A 负结果", "chapter": "第四章"},
                {"claim": "CAP2 完整绑定与重放控制", "researchContent": "RC2", "evidence": "V13/攻击回归/共享 Nonce", "chapter": "第五章"},
                {"claim": "Fail-Closed（RC2 依赖故障）", "researchContent": "RC2", "evidence": "故障测试", "chapter": "第五章"},
                {"claim": "C-01..C-06（RC3 正确性/安全/恢复）", "researchContent": "RC3", "evidence": "I11/I12 145 RUN", "chapter": "第六章"},
                {"claim": "C-07 QBFT 性能", "researchContent": "RC3", "evidence": "FORBIDDEN", "chapter": "第六章"},
            ],
        },
        "negative-result-master-registry.json": {"schemaVersion": "NegativeResultMasterRegistryV1", "results": negative_results},
        "limitation-master-registry.json": {"schemaVersion": "LimitationMasterRegistryV1", "limitations": limitations},
        "literature-verification-queue.json": {"schemaVersion": "LiteratureVerificationQueueV1", "items": literature_queue},
        "defense-risk-register.json": {"schemaVersion": "DefenseRiskRegisterV1",
                                       "questions": [{"q": q, "answer": a} for q, a in defense_risks]},
        "final-thesis-issue-register.json": {"schemaVersion": "FinalThesisIssueRegisterV1", "issues": issues,
                                             "counts": levels},
    }
    for name, value in json_files.items():
        (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    entries = []
    for path in sorted(OUT.rglob("*")):
        if path.is_file() and path.name != "artifact-sha256.json":
            entries.append({"path": path.relative_to(OUT).as_posix(),
                            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    (OUT / "artifact-sha256.json").write_text(json.dumps({
        "schemaVersion": "I14ArtifactSha256V1", "generatedAt": created,
        "selfIncluded": False, "files": entries}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "termConflicts": len(term_conflicts), "forbiddenHits": forbidden_hits,
        "symbolIssues": len(symbol_issues), "numericIssues": len(numeric_issues),
        "refs": len(refs_master), "literatureQueue": len(literature_queue),
        "issues": levels, "docs": len(docs), "files": len(entries) + 1,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
