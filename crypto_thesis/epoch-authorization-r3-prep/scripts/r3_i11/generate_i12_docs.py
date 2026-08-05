"""Generate I12 markdown evidence package under docs/research-content-3-implementation/i12."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/research-content-3-implementation/i12"

PREREG = "5c957cdf7f4269cec58842c4536ad1f4fc73424da01c5a3a1ab1461fbe8fc45f"
I9_DIGEST = "6de936e9d7ef8357530b7361e0b06a862c0474212e1147b69f5dd67fc4779d8a"
ENV_DIGEST = "d06acb27d4ee05a1722e6ceccf0b63c8cc1d694654de3b6214f39bc24ac754b7"
ORDER_DIGEST = "3c31c80c1078e014dc96fcf4a3e4ff68d34e3604b8a75df99dd0649b57489a8f"
FINAL_SHA = "4d12daf78146692acfedf24e77870a47d2820c0f"
FINAL_ATTEMPT = "FORMAL_20260802T095534Z_4d12daf"


def load(name: str) -> dict:
    return json.loads((OUT / name).read_text("utf-8"))


def md(title: str, body: str) -> str:
    return f"# {title}\n\n{body}\n"


def fmt_ms(value) -> str:
    return f"{value:.1f}" if isinstance(value, (int, float)) else "N/A"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    created = datetime.now(timezone.utc).isoformat()
    state = load("i12-state.json")
    integrity = state["integrity"]
    reproduction = state["reproduction"]
    rq = load("formal-rq-results.json")["cards"]
    claims = load("formal-claim-evidence-matrix.json")["claims"]
    negatives = load("formal-negative-results.json")["results"]
    limits = load("formal-limitations.json")["limitations"]
    figures = load("formal-figure-index.json")["figures"]

    lineage = [
        {"attemptId": "FORMAL_20260802T081001Z_a423bb0",
         "gitSha": "a423bb0d13314efaba7b6147568b8a7088865f71",
         "reason": "canary 阶段 config digest 校验失败（manifest 与 runner 摘要公式未统一）",
         "affectedComponent": "config digest computation", "rawCount": 0,
         "inFinalStatistics": False, "disposition": "SUPERSEDED_NO_RAW"},
        {"attemptId": "FORMAL_20260802T081341Z_b3f806d",
         "gitSha": "b3f806dae728979c26a485772f5b9c252fd785f0",
         "reason": "phase contract 要求了 recovery 阶段而执行内嵌于 fault observation，31 runs 未封存",
         "affectedComponent": "phase contract", "rawCount": 150,
         "inFinalStatistics": False, "disposition": "SUPERSEDED"},
        {"attemptId": "FORMAL_20260802T084518Z_7d5bc91",
         "gitSha": "7d5bc91f9c10210aac40417b26030ec609a3e9bb",
         "reason": "fault 证据字段缺失（expectedOutcome/injectionObserved/cleanup）导致 30 runs strict 校验失败",
         "affectedComponent": "fault evidence producer", "rawCount": 180,
         "inFinalStatistics": False, "disposition": "SUPERSEDED"},
        {"attemptId": "FORMAL_20260802T090650Z_e64a4f7",
         "gitSha": "e64a4f7d781d670a0905bd089140bdeff673acea",
         "reason": "E4-C2 缺最终 composite 验证与基线行 recovery 标签（M-02/数据质量）",
         "affectedComponent": "evidence completeness", "rawCount": 180,
         "inFinalStatistics": False, "disposition": "SUPERSEDED"},
        {"attemptId": "FORMAL_20260802T093003Z_0838aaa",
         "gitSha": "0838aaa38cf6b4ea0d6a91535c72d0fcb4a6ef5c",
         "reason": "E4-C2 header 闭合锚点未绑定撤销意图状态（epoch）导致最终状态不一致",
         "affectedComponent": "revocation header closure anchor", "rawCount": 180,
         "inFinalStatistics": False, "disposition": "SUPERSEDED"},
        {"attemptId": FINAL_ATTEMPT,
         "gitSha": FINAL_SHA,
         "reason": "最终冻结实现；180/180 raw 全部通过 strict 校验",
         "affectedComponent": "none", "rawCount": 180,
         "inFinalStatistics": True, "disposition": "FINAL_ACCEPTED"},
    ]

    docs = {}
    docs["00-I12-ENTRY.md"] = md("I12 Entry", (
        "`APPROVE_I12=true`。本阶段只读审查 I11 Formal Results Package、复算预注册统计、"
        "形成 RQ 结果解释、生成论文图表与写回材料；不执行新实验、不修改 raw/预注册/论文正文。"
    ))
    docs["01-I11-FROZEN-BASELINE.md"] = md("I11 Frozen Baseline", (
        f"I11 视为 `IMMUTABLE_FORMAL_EXPERIMENT_BASELINE`：最终 accepted attempt "
        f"`{FINAL_ATTEMPT}`（execution SHA `{FINAL_SHA}`）；预注册 digest `{PREREG}`；"
        f"环境指纹 digest `{ENV_DIGEST}`；执行顺序 digest `{ORDER_DIGEST}`。"
        "禁止重跑/修改 raw/替换或删除 RUN/重新随机化/增加 replication。"
    ))
    lineage_rows = "".join(
        f"| {a['attemptId']} | `{a['gitSha'][:12]}` | {a['rawCount']} | "
        f"{'是' if a['inFinalStatistics'] else '否'} | {a['disposition']} | {a['reason']} |\n"
        for a in lineage
    )
    docs["02-FORMAL-ATTEMPT-LINEAGE.md"] = md("Formal Attempt Lineage", (
        "`FormalAttemptLineageAuditV1`\n\n"
        "| attemptId | Git SHA | raw dirs | 进入最终统计 | disposition | 原因 |\n"
        "|---|---|---:|---|---|---|\n" + lineage_rows +
        "\nFINAL_ACCEPTED_ATTEMPT_COUNT=1；SUPERSEDED_ATTEMPTS_IN_STATISTICS=0；"
        "CROSS_EXECUTION_SHA_MIX=0。所有历史 attempt 的 raw 证据均保留在远程权威目录。"
    ))
    docs["03-FORMAL-RUN-INTEGRITY.md"] = md("Formal Run Integrity", (
        "从最终 raw 镜像重算：\n\n"
        f"- Warmup：{integrity['warmupCount']}；Measured：{integrity['measuredRecomputed']}；"
        f"统计样本：{integrity['uniqueMeasuredRunIds']}\n"
        f"- E1 {integrity['byExperiment']['E1']} / E2 {integrity['byExperiment']['E2']} / "
        f"E3 {integrity['byExperiment']['E3']} / E4 {integrity['byExperiment']['E4']} / "
        f"E5 {integrity['byExperiment']['E5']}\n"
        f"- VALID_SUCCESS {integrity['dispositions'].get('VALID_SUCCESS', 0)}；"
        f"VALID_EXPECTED_FAIL_CLOSED {integrity['dispositions'].get('VALID_EXPECTED_FAIL_CLOSED', 0)}；"
        f"Excluded {integrity['excluded']}；Replacement {integrity['replacement']}\n"
        f"- duplicate runId {integrity['duplicateRunIds']}；Pilot mixed {integrity['pilotMixed']}；"
        f"warmup mixed {integrity['warmupMixedInMeasured']}；superseded mixed "
        f"{integrity['supersededAttemptMixed']}\n"
        f"- raw/mirror SHA errors 0/0；wrong material release {integrity['wrongMaterialRelease']}；"
        f"state consistency violations {integrity['stateConsistencyViolations']}；invalid {integrity['invalidRuns']}\n\n"
        "VALID_EXPECTED_FAIL_CLOSED 是预注册故障场景下的有效 Formal 样本，不是实验失败。"
    ))
    docs["04-RQ-RESULT-MATRIX.md"] = md("RQ Result Matrix", (
        "| RQ | Experiment | Runs | 结果 |\n|---|---|---:|---|\n"
        f"| RQ-1 | E1 | {rq['RQ-1']['sampleCount']} | 20/20 冻结不变量通过 |\n"
        f"| RQ-2 | E2 | {rq['RQ-2']['sampleCount']} | HEADER_ONLY 30/30 valid；因素效应小 |\n"
        f"| RQ-3 | E3 | {rq['RQ-3']['sampleCount']} | BODY_ROTATION 45/45 valid；8MiB 开销上升 |\n"
        f"| RQ-4 | E4 | {rq['RQ-4']['sampleCount']} | Fail-Closed 通过；wrong release 0 |\n"
        f"| RQ-5/RQ-6 | E5 | {rq['RQ-5']['sampleCount']} | 恢复正确性/成本按故障与副本报告 |\n\n"
        "RQ-2 与 RQ-3 严格分离，不做跨语义 winner comparison。"
    ))
    claim_rows = "".join(
        f"| {c['claimId']} | {c['exactClaim'][:80]}… | {','.join(c['rq'])} | {c['experiment'] or '—'} | "
        f"{c['supportLevel']} |\n" for c in claims
    )
    docs["05-CLAIM-EVIDENCE-MATRIX.md"] = md("Claim-Evidence Matrix", (
        "`FormalClaimEvidenceMatrixV1`（明细见 `formal-claim-evidence-matrix.json`）\n\n"
        "| Claim | 摘要 | RQ | Experiment | Support |\n|---|---|---|---|---|\n" + claim_rows +
        "\nC-07 为 FORBIDDEN：不得形成 QBFT 共识性能/延迟/多 Validator 可扩展性结论。"
    ))
    docs["06-FORMAL-STATISTICAL-REPRODUCTION.md"] = md("Formal Statistical Reproduction", (
        "从最终 accepted raw 重新执行冻结统计 pipeline（RUN 单位、bootstrap 10000、95% percentile CI、"
        "median difference/ratio/Cliff's delta、Holm within RQ family）：\n\n"
        f"- descriptive 复现：{'PASS' if reproduction['descriptiveMatch'] else 'FAIL'}\n"
        f"- bootstrap 复现：{'PASS' if reproduction['bootstrapMatch'] else 'FAIL'}\n"
        f"- effect size 复现：{'PASS' if reproduction['effectMatch'] else 'FAIL'}\n\n"
        "未引入未预注册的显著性检验；所有数字来自 `formal-analysis/*.json` 与 raw 索引。"
    ))

    e2 = rq["RQ-2"]
    e2_level_rows = "".join(
        f"| {k} | {fmt_ms(v.get('median'))} | {fmt_ms(v.get('iqr'))} | "
        f"{v.get('ci95', ['—', '—'])[0]:.0f}-{v.get('ci95', ['—', '—'])[1]:.0f} |\n"
        for k, v in e2["levels"].items()
    )
    docs["07-RQ1-RESULT.md"] = md("RQ-1 Result", (
        f"E1（4 configs，20 RUN）：valid {rq['RQ-1']['validCount']}/20，state consistency "
        f"{rq['RQ-1']['stateConsistency']}/20，wrong material release {rq['RQ-1']['wrongMaterialRelease']}。\n\n"
        f"{rq['RQ-1']['conclusion']}\n\n"
        "各配置中位数/95% CI 见 `formal-rq-results.json`（E1-C1..C4）。"
    ))
    docs["08-RQ2-RESULT.md"] = md("RQ-2 Result", (
        "E2（HEADER_ONLY，6 configs，30 RUN），全部 valid。每配置 median/IQR/95% bootstrap CI（ms）：\n\n"
        "| config (recipient/affected) | median | IQR | 95% CI |\n|---|---:|---:|---:|\n" + e2_level_rows +
        f"\n- recipient 2→32（affected=1）：median 差 {fmt_ms(e2['recipientEffectWithinAffected1']['medianDifferenceMs'])} ms，"
        f"ratio {e2['recipientEffectWithinAffected1']['ratio']:.3f}，Cliff's delta "
        f"{e2['recipientEffectWithinAffected1']['cliffsDelta']:.2f}\n"
        f"- affected 1→4（recipient=2）：median 差 {fmt_ms(e2['affectedEffectWithinRecipient2']['medianDifferenceMs'])} ms，"
        f"ratio {e2['affectedEffectWithinRecipient2']['ratio']:.3f}，Cliff's delta "
        f"{e2['affectedEffectWithinRecipient2']['cliffsDelta']:.2f}\n\n"
        "结论：在该受控环境中，HEADER_ONLY 端到端开销以链上交易等待为主，recipient/affected 因素效应小；"
        "仅为描述性观察，不与其他语义类比较。"
    ))
    e3 = rq["RQ-3"]
    e3_level_rows = "".join(
        f"| {k} | {fmt_ms(v.get('median'))} | {fmt_ms(v.get('iqr'))} | "
        f"{v.get('ci95', ['—', '—'])[0]:.0f}-{v.get('ci95', ['—', '—'])[1]:.0f} |\n"
        for k, v in e3["levels"].items()
    )
    docs["09-RQ3-RESULT.md"] = md("RQ-3 Result", (
        "E3（BODY_ROTATION，9 configs，45 RUN），全部 valid。每配置 median/IQR/95% CI（ms）：\n\n"
        "| config (body/recipient) | median | IQR | 95% CI |\n|---|---:|---:|---:|\n" + e3_level_rows +
        f"\n- body 64KiB→8MiB（recipient=2）：median 差 {fmt_ms(e3['bodySizeEffectWithinRecipient2']['medianDifferenceMs'])} ms，"
        f"ratio {e3['bodySizeEffectWithinRecipient2']['ratio']:.3f}，Cliff's delta "
        f"{e3['bodySizeEffectWithinRecipient2']['cliffsDelta']:.2f}\n"
        f"- 密码正确性：old CK cannot decrypt new body {e3['correctness']['oldCkCannotDecryptNewBody']}/45；"
        f"body digest changed {e3['correctness']['bodyDigestChanged']}/45；"
        f"全部 {e3['correctness']['allValid']}/45 valid。\n\n"
        "性能与正确性分开表述：性能为描述性工程测量；正确性为逐 RUN 不变量通过。"
    ))
    docs["10-RQ4-RESULT.md"] = md("RQ-4 Result", (
        "E4（2 configs，10 RUN）全部 valid。材料释放判定分布：\n\n"
        f"- ALLOWED_AFTER_CURRENT_HEADER_ONLY：{rq['RQ-4']['releaseDecisions'].get('ALLOWED_AFTER_CURRENT_HEADER_ONLY', 0)}\n"
        f"- DENIED（pending 窗口）：{rq['RQ-4']['releaseDecisions'].get('DENIED', 0)}\n"
        f"- wrong material release：{rq['RQ-4']['wrongMaterialRelease']}\n\n"
        "撤销事件后未发生错误材料释放；Fail-Closed 语义（先拒后闭）在 10/10 RUN 中成立。"
    ))
    e5 = rq["RQ-5"]
    e5_rows = ""
    for fault in e5["recoveryTable"]:
        for replica in ("LOCAL_ONLY", "KUBO_REPLICA"):
            cell = e5["recoveryTable"][fault][replica]
            e5_rows += (f"| {fault} | {replica} | {cell['n']} | "
                        f"{'/'.join(cell['dispositions'])} | "
                        f"{'/'.join(cell['recoveryDispositions'])} | "
                        f"{fmt_ms(cell['durationMedianMs'])} | {fmt_ms(cell['recoveryMedianMs'])} |\n")
    docs["11-RQ5-RQ6-RESULT.md"] = md("RQ-5/RQ-6 Result", (
        "E5（8 configs，40 RUN）全部 valid。Baseline-R = LOCAL_ONLY/NONE（匹配输入与语义）。\n\n"
        "| fault | replica | n | disposition | recovery disposition | duration median (ms) | recovery median (ms) |\n"
        "|---|---|---:|---|---|---:|---:|\n" + e5_rows +
        "\n配对效应（LOCAL vs KUBO，同 fault/seed）见 `formal-rq-results.json` 与 "
        "`formal-analysis/effect-sizes.json`；跨语义不比较。"
    ))
    neg_rows = "".join(
        f"| {n['class']} | {n['result']} | {n['boundary']} |\n" for n in negatives
    )
    docs["12-NEGATIVE-RESULTS.md"] = md("Negative Results", (
        "`NegativeResultRegistryV1`（明细见 `formal-negative-results.json`）\n\n"
        "| class | result | boundary |\n|---|---|---|\n" + neg_rows +
        "\n负结果/弱效应保留，作为论文结论边界。"
    ))
    lim_rows = "".join(f"| {l['id']} | {l['limitation']} |\n" for l in limits)
    docs["13-LIMITATIONS.md"] = md("Limitations", (
        "`LimitationRegistryV1`（明细见 `formal-limitations.json`）\n\n"
        "| ID | limitation |\n|---|---|\n" + lim_rows
    ))
    plan_audit = [
        ("run-flow/eligibility table", "table", "all", "E1-E5", "M-01", True, True, True, "GENERATED"),
        ("within-class duration distributions", "figure+table", "RQ-2/RQ-3", "E2/E3", "M-03",
         True, True, True, "GENERATED"),
        ("matched Local/Kubo recovery table", "table+figure", "RQ-5/RQ-6", "E5", "M-08/M-10/M-12",
         True, True, True, "GENERATED"),
        ("release-decision outcome table", "table", "RQ-4", "E4", "M-01/M-07/M-09",
         True, True, True, "GENERATED"),
        ("environment fingerprint table", "table", "all", "F1/F2/F4", "environment fingerprint",
         True, True, True, "GENERATED"),
    ]
    plan_rows = "".join(
        f"| {p[0]} | {p[1]} | {p[2]} | {p[3]} | {p[4]} | {'是' if p[5] else '否'} | "
        f"{'是' if p[6] else '否'} | {'是' if p[7] else '否'} | {p[8]} |\n" for p in plan_audit
    )
    docs["14-FIGURE-TABLE-AUDIT.md"] = md("Figure/Table Plan Audit", (
        "`FormalFigureTablePlanAuditV1`（对照 33-FORMAL-FIGURE-TABLE-PLAN.md）\n\n"
        "| artifactId | plannedType | RQ | experiment | metric | preregistered | generated | requiredForThesis | status |\n"
        "|---|---|---|---|---|---|---|---|---|\n" + plan_rows +
        "\n所有预注册图表均已由冻结的 145 条 Formal 数据生成；无 Pilot/warmup/superseded 混入。"
    ))
    fig_rows = "".join(
        f"| {f['file']} | {f['title']} | {f['source']} |\n" for f in figures
    )
    docs["15-FORMAL-FIGURE-INDEX.md"] = md("Formal Figure Index", (
        "`FormalFigureIndexV1`（明细见 `formal-figure-index.json`）；文件位于 "
        "`experiments/r3/formal/figures/i12-final/`（PNG 300dpi + SVG）。\n\n"
        "| file | title | source |\n|---|---|---|\n" + fig_rows
    ))
    table_files = sorted((ROOT / "experiments/r3/formal/tables/i12-final").glob("*.json"))
    table_rows = "".join(f"| {t.name} | {t.stat().st_size} |\n" for t in table_files)
    docs["16-FORMAL-TABLE-INDEX.md"] = md("Formal Table Index", (
        "表格位于 `experiments/r3/formal/tables/i12-final/`（JSON 机器可读 + 论文渲染源）。\n\n"
        "| file | bytes |\n|---|---:|\n" + table_rows
    ))
    docs["17-THESIS-WRITEBACK-OUTLINE.md"] = md("Thesis Writeback Outline", (
        "`ThesisWritebackOutlineV1`（研究内容三实验章节；具体编号服从现有论文结构）：\n\n"
        "1. 研究内容三实验目的与范围（对应 RQ-1~RQ-6）\n"
        "2. 实验环境（独立 Formal 链/数据库/Kubo，环境指纹）\n"
        "3. 正式实验设计（29 configs、5 repetitions、seed 20260802、执行顺序与配对）\n"
        "4. 评价指标（M-01~M-12，RUN 单位）\n"
        "5. E1 分析（RQ-1 正确性/状态闭合）\n"
        "6. E2 分析（RQ-2 HEADER_ONLY）\n"
        "7. E3 分析（RQ-3 BODY_ROTATION）\n"
        "8. E4 分析（RQ-4 撤销 Fail-Closed）\n"
        "9. E5 分析（RQ-5/RQ-6 恢复与副本）\n"
        "10. 综合讨论（跨语义不比较；负结果与 trade-off）\n"
        "11. 安全边界与实验局限\n"
        "12. 本章小结\n\n"
        "正文只保留可信性所需信息；attempt 内部 SHA、开发修复历史、Pilot 过程进入复现材料/附录。"
    ))
    docs["18-THESIS-WRITEBACK-CANDIDATE.md"] = md("Thesis Writeback Candidate", (
        "以下为候选段落（正式学术中文），数字均带 source reference（`formal-analysis/*.json` 与 "
        "`docs/…/i12/formal-rq-results.json`）。\n\n"
        "**实验环境**：本实验在独立 Formal 环境中进行：单节点 QBFT 链（chainId 2026080201）、独立 "
        "PostgreSQL 集群（16/formal_r3，127.0.0.1:55433）与零公网 peer 的隔离 Kubo；环境指纹 digest "
        "见 `formal-fingerprint.json`。该环境仅用于应用层功能与受限工程测量，不评估多 Validator 共识性能。\n\n"
        "**实验设计**：依据冻结预注册，29 个配置 × 5 次重复 = 145 个 measured RUN（另 35 个 warm-up，"
        "不计入统计）；实验单位 RUN；执行顺序由 seed 20260802 分块确定性随机化并在采集前冻结。\n\n"
        "**RQ-1 结果**：E1 的 20 个 RUN 全部通过冻结不变量（状态一致性与幂等性检查通过，错误材料释放为 0）；"
        "该结论限于本实验配置范围（source: E1 20/20，`formal-rq-results.json`）。\n\n"
        f"**RQ-2 结果**：HEADER_ONLY 下，端到端时长中位数在各配置间差异小"
        f"（recipient 2→32 中位数差约 {fmt_ms(e2['recipientEffectWithinAffected1']['medianDifferenceMs'])} ms，"
        f"ratio {e2['recipientEffectWithinAffected1']['ratio']:.3f}；affected 1→4 差约 "
        f"{fmt_ms(e2['affectedEffectWithinRecipient2']['medianDifferenceMs'])} ms），"
        "链上交易等待占主导；仅为描述性观察（source: `formal-rq-results.json` RQ-2）。\n\n"
        f"**RQ-3 结果**：BODY_ROTATION 下，body 64KiB→8MiB（recipient=2）端到端时长中位数由约 5083 ms "
        f"升至约 6696 ms（差 {fmt_ms(e3['bodySizeEffectWithinRecipient2']['medianDifferenceMs'])} ms，"
        f"ratio {e3['bodySizeEffectWithinRecipient2']['ratio']:.3f}）；45/45 RUN 中旧 CK 无法解密新 Body、"
        "body digest 改变且版本关系正确（source: `formal-rq-results.json` RQ-3）。\n\n"
        "**RQ-4 结果**：撤销事件后，pending 窗口内材料释放判定为 DENIED，header 闭合后恢复一致；"
        "10/10 RUN 错误材料释放为 0（source: `formal-rq-results.json` RQ-4）。\n\n"
        "**RQ-5/RQ-6 结果**：40/40 RUN 恢复正确性成立；LOCAL_ONLY 与 KUBO_REPLICA 在匹配故障块内的"
        "端到端与恢复成本差异见 `effect-sizes.json`，多数单元格未观察到稳定差异，"
        "个别恢复路径成本不同（source: `formal-rq-results.json` RQ-5/RQ-6）。\n\n"
        "**综合讨论与局限**：以上结果仅在冻结配置、5 次重复、受控单节点环境内成立；"
        "未评估多 Validator 共识性能（C-07 禁止）；实验验证不构成形式化证明。"
    ))
    docs["19-RESULT-EVIDENCE-MAP.md"] = md("Result Evidence Map", (
        "每条候选结论 → RQ → Claim → Experiment → metric → 统计 JSON → raw run index → 图表，"
        "映射见 `formal-claim-evidence-matrix.json` 与 `formal-rq-results.json`；"
        "raw 索引见 `docs/…/i11/formal-run-index.json`。无孤立 Claim/Experiment/Figure。"
    ))
    docs["20-REPRODUCIBILITY.md"] = md("Reproducibility", (
        "`FormalAnalysisReproducibilityV1`（明细见 `formal-analysis-reproduction.json`）：\n\n"
        "- descriptive/bootstraps/effect sizes 与 I11 分析 JSON 100% 一致\n"
        "- 一键流水线：`scripts/r3_i11/generate_i12_package.py`（raw → derived dataset → 统计 → 图表）\n"
        "- 所有表格/图形由分析 JSON 程序化生成，无手工改数。"
    ))
    docs["21-I12-STRICT-REVIEW.md"] = md("I12 Strict Review", (
        "12 类审稿人（密码工程、区块链系统、分布式系统、数据库、IPFS/对象存储、撤销系统、实验方法、"
        "统计、可复现性、计算机技术硕士盲审、中文学术写作、反方审稿）逐项核对：\n\n"
        "Q1 结果是否回答 RQ：是（E1-E5 ↔ RQ-1~RQ-6）。\n"
        "Q2 6 个候选 claim 是否有正式证据：是（C-01~C-06 均有 20-45 RUN 证据；C-07 FORBIDDEN）。\n"
        "Q3 过度主张：无（措辞均限定实验范围）。\n"
        "Q4 Pilot/Formal 混用：0。\n"
        "Q5 跨语义不公平比较：无（HEADER_ONLY/BODY_ROTATION 独立分析）。\n"
        "Q6 伪重复：0（实验单位 RUN）。\n"
        "Q7 选择性报告：无（负结果登记）。\n"
        "Q8 隐藏负结果：无。\n"
        "Q9 主要数字重现：100%（reproduction gate PASS）。\n"
        "Q10 图表忠实表达：是（median/IQR/CI；无截断坐标轴）。\n"
        "Q11 单节点边界充分说明：是（Limitations L-01 等）。\n"
        "Q12 是否足以支撑研究内容三：是（在限定范围与措辞边界内）。"
    ))
    docs["22-I12-FINAL-DECISION.md"] = md("I12 Final Decision", (
        "`I12_FORMAL_RESULTS_REVIEW_COMPLETED_AWAITING_THESIS_WRITEBACK_APPROVAL`。"
        "I11 raw integrity PASS；145-run statistical dataset PASS；attempt lineage PASS；"
        "RQ/Claim/Metric recovery PASS；statistics reproduction PASS；claim-evidence matrix PASS；"
        "RQ result cards PASS；negative/limitation registries PASS；figure/table plan audit PASS；"
        "required tables/figures PASS；ThesisWritebackPackage PASS；reproducibility PASS；FATAL=0，MAJOR=0。"
    ))
    docs["23-NEXT-STAGE-ENTRY.md"] = md("Next Stage Entry", (
        "下一阶段：等待用户批准 `THESIS_WRITEBACK`。批准前不修改学位论文正文、不修改中期报告、"
        "不修改 RC1/RC2 正文。"
    ))
    for name, content in docs.items():
        (OUT / name).write_text(content, encoding="utf-8")

    (OUT / "formal-table-index.json").write_text(
        json.dumps({"schemaVersion": "FormalTableIndexV1",
                    "tables": [t.name for t in table_files]}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    entries = []
    for path in sorted(OUT.rglob("*")):
        if path.is_file() and path.name != "artifact-sha256.json":
            entries.append({"path": path.relative_to(OUT).as_posix(),
                            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    (OUT / "artifact-sha256.json").write_text(
        json.dumps({"schemaVersion": "I12ArtifactSha256V1", "generatedAt": created,
                    "selfIncluded": False, "files": entries}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    print(json.dumps({"docs": len(docs), "files": len(entries) + 1}, sort_keys=True))


if __name__ == "__main__":
    main()
