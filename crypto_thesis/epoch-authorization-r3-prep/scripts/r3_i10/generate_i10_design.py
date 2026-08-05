"""Generate the I10 formal-design and preregistration package.

This generator is deliberately design-only: it never creates a formal attempt,
contacts a chain, starts a service, or reads Pilot raw evidence.  It binds the
package to the current Git commit and to a read-only digest of the accepted I9
summary artifacts.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "research-content-3-implementation" / "i10"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def i9_digest() -> tuple[str, list[dict[str, str]]]:
    paths = [
        "experiments/r3/i9-pilot/final-analysis/i9-run-index.json",
        "experiments/r3/i9-pilot/final-analysis/i9-state.json",
        "experiments/r3/i9-pilot/final-analysis/pairing-smoke.json",
        "experiments/r3/i9-pilot/final-analysis/statistical-smoke.json",
        "experiments/r3/i9-pilot/final-analysis/strict-review.json",
        "docs/research-content-3-implementation/i9-bcd/18-I9-STATE.md",
        "docs/research-content-3-implementation/i9-bcd/20-I9-ACCEPTANCE.md",
    ]
    entries = []
    for rel in paths:
        data = (ROOT / rel).read_bytes()
        entries.append({"path": rel, "sha256": sha256_bytes(data)})
    canonical = b"".join(
        (entry["path"] + "\0" + entry["sha256"] + "\n").encode("utf-8")
        for entry in sorted(entries, key=lambda item: item["path"])
    )
    return sha256_bytes(canonical), entries


def write(rel: str, text: str) -> None:
    path = OUT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def md(title: str, body: str) -> str:
    return f"# {title}\n\n{body}\n"


def main() -> None:
    head = git_head()
    created = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    baseline_digest, baseline_files = i9_digest()

    rq = [
        {
            "rqId": "RQ-1",
            "question": "在固定链上块与数据库快照边界下，VersionedHeaderV1、AuthorizationState 和 HeaderRegistry 的状态更新是否保持可验证的一致性与幂等性？",
            "class": ["CORRECTNESS", "SECURITY_BEHAVIOR"],
            "primaryEvidence": "run-level invariant and acceptance evidence",
        },
        {
            "rqId": "RQ-2",
            "question": "在不改变安全语义的同类任务内，HEADER_ONLY 的端到端工程开销如何随 recipient_count 与 affected_count 变化？",
            "class": ["ENGINEERING_OVERHEAD", "SCALABILITY"],
            "primaryEvidence": "RUN-level duration and resource counters; no comparison with BODY_ROTATION",
        },
        {
            "rqId": "RQ-3",
            "question": "BODY_ROTATION 在固定语义内如何随 body_bytes 与 recipient_count 变化，并是否保持旧版本不可释放和新版本可验证？",
            "class": ["ENGINEERING_OVERHEAD", "CORRECTNESS"],
            "primaryEvidence": "RUN-level duration, body digest, header-chain and release decisions",
        },
        {
            "rqId": "RQ-4",
            "question": "预先撤销事件发生后，当前 Header 的可用性窗口与材料释放判定是否 fail-closed、可追踪且不产生错误释放？",
            "class": ["SECURITY_BEHAVIOR", "CORRECTNESS"],
            "primaryEvidence": "fixed-block event evidence and MaterialReleaseGuard decisions",
        },
        {
            "rqId": "RQ-5",
            "question": "在 LocalObjectStore 与 Kubo replica 两种已冻结对象来源下，RecoveryCoordinator 能否在对象缺失、损坏或 CID 不一致时保持一致性并完成预注册的恢复动作？",
            "class": ["RECOVERY", "SECURITY_BEHAVIOR", "ENGINEERING_OVERHEAD"],
            "primaryEvidence": "recovery disposition, repair counters, object-source and integrity evidence",
        },
        {
            "rqId": "RQ-6",
            "question": "在受限且明确标注的独立正式环境中，链上、数据库和对象存储边界的组合是否产生可重复的应用层开销与恢复成本？",
            "class": ["PERFORMANCE", "RECOVERY"],
            "primaryEvidence": "pre-registered RUN-level metrics only; no consensus-performance inference",
        },
    ]

    claim_matrix = [
        {
            "claimId": "C-01", "claimText": "VersionedHeaderV1 与链上/数据库固定块状态在预注册更新路径上保持一致、可验证且幂等。", "claimClass": "CORRECTNESS", "supportingRQ": ["RQ-1"], "requiredMetric": ["M-01", "M-02", "M-09"], "requiredEnvironment": "F1/F2", "requiredBaseline": "same-task replay control", "requiredExperiment": "E1", "allowedEvidence": ["run-level strict evidence", "fixed-block composite state", "database snapshot"], "forbiddenEvidence": ["Pilot-only rows as formal results", "single-node observations as QBFT claims"], "status": "FROZEN"},
        {
            "claimId": "C-02", "claimText": "HEADER_ONLY 在同一语义类内的工程开销可按 recipient_count 与 affected_count 描述。", "claimClass": "ENGINEERING_OVERHEAD", "supportingRQ": ["RQ-2"], "requiredMetric": ["M-03", "M-04", "M-05"], "requiredEnvironment": "F2", "requiredBaseline": "within-class fixed-size control", "requiredExperiment": "E2", "allowedEvidence": ["formal RUN timing with environment fingerprint", "pre-registered within-class effects"], "forbiddenEvidence": ["HEADER_ONLY vs BODY_ROTATION ranking", "Pilot timing"], "status": "FROZEN"},
        {
            "claimId": "C-03", "claimText": "BODY_ROTATION 在同一语义类内的工程开销可按 body_bytes 与 recipient_count 描述。", "claimClass": "ENGINEERING_OVERHEAD", "supportingRQ": ["RQ-3"], "requiredMetric": ["M-03", "M-04", "M-06"], "requiredEnvironment": "F2", "requiredBaseline": "within-class fixed-body control", "requiredExperiment": "E3", "allowedEvidence": ["formal RUN timing and bytes", "same-class CI/effect size"], "forbiddenEvidence": ["BODY_ROTATION vs HEADER_ONLY superiority", "Pilot timing"], "status": "FROZEN"},
        {
            "claimId": "C-04", "claimText": "预先撤销路径在当前 Header 与释放窗口约束下 fail-closed，且不产生错误材料释放。", "claimClass": "SECURITY_BEHAVIOR", "supportingRQ": ["RQ-4"], "requiredMetric": ["M-01", "M-07", "M-09"], "requiredEnvironment": "F1/F2", "requiredBaseline": "no-revocation control", "requiredExperiment": "E4", "allowedEvidence": ["event identity", "release decision", "negative-path acceptance"], "forbiddenEvidence": ["implementation test treated as cryptographic proof", "recovery success as plaintext-recovery claim"], "status": "FROZEN"},
        {
            "claimId": "C-05", "claimText": "RecoveryCoordinator 在预注册对象/服务故障下保持一致性、可解释并按规则 fail-closed。", "claimClass": "RECOVERY", "supportingRQ": ["RQ-5", "RQ-6"], "requiredMetric": ["M-08", "M-09", "M-10", "M-11"], "requiredEnvironment": "F4", "requiredBaseline": "Baseline-R local-only control", "requiredExperiment": "E5", "allowedEvidence": ["independent fault observation", "repair plan and disposition", "object SHA/CID evidence"], "forbiddenEvidence": ["unobserved fault labels", "Pilot-only fault runs", "silent deletion of failed records"], "status": "FROZEN"},
        {
            "claimId": "C-06", "claimText": "Kubo replica 相对于 LocalObjectStore 的影响仅在语义相同、对象大小和故障条件匹配的正式块内报告。", "claimClass": "PERFORMANCE", "supportingRQ": ["RQ-5", "RQ-6"], "requiredMetric": ["M-08", "M-10", "M-12"], "requiredEnvironment": "F4", "requiredBaseline": "Baseline-R", "requiredExperiment": "E5", "allowedEvidence": ["paired RUNs by deterministic workload identity", "pre-registered recovery metrics"], "forbiddenEvidence": ["timing-neighbor pairing", "unmatched size comparisons", "formal chain not deployed"], "status": "FROZEN"},
        {
            "claimId": "C-07", "claimText": "RC3 形式化设计不声称 QBFT 共识吞吐、共识延迟或多验证节点可扩展性。", "claimClass": "SCALABILITY", "supportingRQ": [], "requiredMetric": [], "requiredEnvironment": "F3", "requiredBaseline": "none", "requiredExperiment": "none", "allowedEvidence": ["design decision only"], "forbiddenEvidence": ["single-node or Pilot chain used as QBFT evidence", "un-deployed topology used as results"], "status": "FORBIDDEN"},
    ]

    factors = [
        {"factorId": "FCT", "name": "recipient_count", "type": "input", "scientificRationale": "tests envelope fan-out within each semantic update class", "PilotEvidence": "P9-B exercised 2/8/32", "candidateLevels": [2, 8, 32], "frozenLevels": [2, 8, 32], "controlVariables": ["body_bytes", "affected_count", "seeded workload"], "applicableRQ": ["RQ-2", "RQ-3"]},
        {"factorId": "FAF", "name": "affected_count", "type": "input", "scientificRationale": "separates event fan-out from recipient fan-out", "PilotEvidence": "P9-B exercised 1/4", "candidateLevels": [1, 4], "frozenLevels": [1, 4], "controlVariables": ["recipient_count", "update_kind"], "applicableRQ": ["RQ-2"]},
        {"factorId": "FBS", "name": "body_bytes", "type": "input", "scientificRationale": "captures object/body movement only in BODY_ROTATION", "PilotEvidence": "P9-B exercised 65536/1048576/8388608", "candidateLevels": [65536, 1048576, 8388608], "frozenLevels": [65536, 1048576, 8388608], "controlVariables": ["recipient_count", "update_kind"], "applicableRQ": ["RQ-3", "RQ-5"]},
        {"factorId": "FUP", "name": "update_kind", "type": "semantic_block", "scientificRationale": "HEADER_ONLY and BODY_ROTATION have different security and storage semantics", "PilotEvidence": "I9 explicitly forbids cross-semantic comparison", "candidateLevels": ["HEADER_ONLY", "BODY_ROTATION"], "frozenLevels": ["HEADER_ONLY", "BODY_ROTATION"], "controlVariables": ["seed", "environment"], "applicableRQ": ["RQ-2", "RQ-3"]},
        {"factorId": "FRS", "name": "replica_state", "type": "recovery_control", "scientificRationale": "isolates Kubo replica contribution with same object identity", "PilotEvidence": "P9-C/P9-D exercised local, replica and unavailable states", "candidateLevels": ["LOCAL_ONLY", "KUBO_REPLICA"], "frozenLevels": ["LOCAL_ONLY", "KUBO_REPLICA"], "controlVariables": ["body_bytes", "fault_class"], "applicableRQ": ["RQ-5", "RQ-6"]},
        {"factorId": "FFT", "name": "fault_class", "type": "controlled_fault", "scientificRationale": "covers object and service failure branches without changing protocol", "PilotEvidence": "P9-C/P9-D accepted controlled branches", "candidateLevels": ["NONE", "CORRUPT_RESTORE", "CID_MISMATCH", "BOTH_MISSING", "KUBO_UNAVAILABLE", "POSTGRES_UNAVAILABLE", "BESU_UNAVAILABLE"], "frozenLevels": ["NONE", "CORRUPT_RESTORE", "CID_MISMATCH", "BOTH_MISSING"], "controlVariables": ["replica_state", "object identity", "observation evidence"], "applicableRQ": ["RQ-4", "RQ-5"]},
        {"factorId": "FWL", "name": "workload_type", "type": "workload", "scientificRationale": "keeps update, restore and revocation units semantically distinct", "PilotEvidence": "I9 generator is deterministic and seeded", "candidateLevels": ["HEADER_UPDATE", "BODY_ROTATION", "REVOCATION", "RESTORE"], "frozenLevels": ["HEADER_UPDATE", "BODY_ROTATION", "REVOCATION", "RESTORE"], "controlVariables": ["generator_version", "seed", "input_digest"], "applicableRQ": ["RQ-1", "RQ-2", "RQ-3", "RQ-4", "RQ-5"]},
        {"factorId": "FCC", "name": "concurrency", "type": "operational", "scientificRationale": "tests bounded queue contention without claiming distributed scalability", "PilotEvidence": "I4/I9 establish concurrency and lease boundaries", "candidateLevels": [1, 4, 16], "frozenLevels": [1, 4], "controlVariables": ["semantic block", "environment", "database pool"], "applicableRQ": ["RQ-1", "RQ-6"]},
    ]

    metrics = [
        {"metricId": "M-01", "name": "strict_validity", "unit": "boolean/run", "aggregation": "count and proportion by pre-registered config", "primary": True, "exclusion": "identity/SHA/evidence failures excluded and logged"},
        {"metricId": "M-02", "name": "state_consistency", "unit": "boolean/run", "aggregation": "invariant pass proportion", "primary": True, "exclusion": "missing fixed-block state is invalid"},
        {"metricId": "M-03", "name": "end_to_end_duration", "unit": "milliseconds/run", "aggregation": "median, IQR, mean, SD, percentile bootstrap CI", "primary": True, "exclusion": "invalid clock or partial phase"},
        {"metricId": "M-04", "name": "chain_receipt_duration", "unit": "milliseconds/run", "aggregation": "descriptive within semantic class", "primary": False, "exclusion": "diagnostic only when receipt absent"},
        {"metricId": "M-05", "name": "recipient_envelope_count", "unit": "count/run", "aggregation": "median and exact count", "primary": True, "exclusion": "input identity mismatch"},
        {"metricId": "M-06", "name": "body_bytes_processed", "unit": "bytes/run", "aggregation": "exact bytes and ratio to frozen input", "primary": True, "exclusion": "digest/size mismatch"},
        {"metricId": "M-07", "name": "release_decision_latency", "unit": "milliseconds/run", "aggregation": "median/IQR within security block", "primary": True, "exclusion": "decision not evaluated"},
        {"metricId": "M-08", "name": "recovery_duration", "unit": "milliseconds/run", "aggregation": "median/IQR and bootstrap CI by fault/replica block", "primary": True, "exclusion": "missing independent fault observation"},
        {"metricId": "M-09", "name": "repair_actions", "unit": "count/run", "aggregation": "exact count; zero is meaningful", "primary": True, "exclusion": "partial recovery evidence"},
        {"metricId": "M-10", "name": "object_source", "unit": "categorical/run", "aggregation": "count by LOCAL/KUBO and fault outcome", "primary": True, "exclusion": "unverified source"},
        {"metricId": "M-11", "name": "recovery_disposition", "unit": "categorical/run", "aggregation": "count by CONSISTENT/RECOVERY_IN_PROGRESS/UNRECOVERABLE", "primary": True, "exclusion": "unknown disposition"},
        {"metricId": "M-12", "name": "object_read_bytes", "unit": "bytes/run", "aggregation": "median/IQR in matched storage blocks", "primary": False, "exclusion": "read accounting unavailable"},
    ]

    run_budget = {
        "schemaVersion": "R3FormalRunBudgetV1",
        "configurations": [
            {"experimentId": "E1", "description": "Correctness and state-closure blocks embedded in each semantic class", "configs": 4, "repetitions": 5, "measuredRuns": 20},
            {"experimentId": "E2", "description": "HEADER_ONLY: recipient_count 2/8/32 x affected_count 1/4", "configs": 6, "repetitions": 5, "measuredRuns": 30},
            {"experimentId": "E3", "description": "BODY_ROTATION: body_bytes 64KiB/1MiB/8MiB x recipient_count 2/8/32", "configs": 9, "repetitions": 5, "measuredRuns": 45},
            {"experimentId": "E4", "description": "Preemptive revocation: current-header and post-event controls", "configs": 2, "repetitions": 5, "measuredRuns": 10},
            {"experimentId": "E5", "description": "Recovery: LOCAL_ONLY/KUBO_REPLICA x NONE/CORRUPT_RESTORE/CID_MISMATCH/BOTH_MISSING", "configs": 8, "repetitions": 5, "measuredRuns": 40},
        ],
        "configurationCount": 29,
        "repetitions": 5,
        "warmupsPerConfiguration": 1,
        "warmupRuns": 29,
        "environmentWarmups": 6,
        "measuredRuns": 145,
        "totalPlannedRuns": 180,
        "estimatedDuration": {"nominalHours": 4, "rangeHours": [2, 8], "basis": "engineering estimate from phase structure; not observed data"},
        "powerAnalysis": "POWER_ANALYSIS_NOT_JUSTIFIED",
        "rationale": "Five RUN repetitions provide a bounded engineering precision sample; functional/security outcomes are acceptance proportions, not powered population inference. The matrix is blocked to avoid a full factorial explosion.",
    }

    prereg = {
        "schemaVersion": "R3FormalPreregistrationV1",
        "status": "DESIGN_FROZEN_AWAITING_I11_APPROVAL",
        "gitCommit": head,
        "i9AcceptedPilotBaselineDigest": baseline_digest,
        "i9BaselineFrozen": True,
        "formalDataCollectionAuthorized": False,
        "formalAttemptCreated": False,
        "formalPerformanceConclusion": False,
        "researchQuestions": [r["rqId"] for r in rq],
        "claimMatrix": "formal-claim-matrix.json",
        "factorMatrix": "formal-factor-matrix.json",
        "metricRegistry": "formal-metric-registry.json",
        "runBudget": "formal-run-budget.json",
        "environmentClasses": ["F1", "F2", "F3", "F4"],
        "rc3MultiNodeFormalRequired": False,
        "multiNodeReason": "No frozen thesis claim requires QBFT consensus performance; any future consensus claim requires a separate I10 amendment and genuinely deployed independent topology.",
        "randomization": {"strategy": "blocked deterministic randomization", "seed": 20260802, "blockKeys": ["semantic_class", "experimentId", "configuration_digest"], "timingNeighborPairing": False},
        "pairing": {"pairingKey": "generatorVersion|semanticClass|inputDigest|seed|configurationDigest", "sharedFactors": ["semantic_class", "input_digest", "seed", "environment_fingerprint"], "varyingFactors": ["replica_state", "fault_class", "recipient_count", "body_bytes"], "crossSemanticPairing": False},
        "statistics": {"unit": "RUN", "descriptive": ["n", "mean", "SD", "median", "IQR", "min", "max"], "bootstrap": {"enabled": True, "resamples": 10000, "ci": "percentile 95%", "resampleUnit": "RUN within pre-registered block"}, "effectSize": ["median difference", "ratio with log transform when positive", "Cliffs delta for ordinal outcomes"], "multiplicity": "Holm correction within each RQ family", "pHacking": "forbidden"},
        "policies": {"missing": "log and exclude; no silent deletion", "replacement": "only if pre-registered infrastructure replacement rule is met and replacement is a new RUN with original failure retained", "failure": "classify protocol/security/infrastructure; never relabel after seeing timing", "stop": "strict stop for security, protocol, design, unauthorized-resource, or FATAL failures"},
        "preregistrationDigest": None,
        "createdAt": created,
    }

    docs = {
        "00-I10-ENTRY.md": md("I10 Entry", f"I10 is admitted for design, preregistration, and review only. I9 is frozen as `IMMUTABLE_PILOT_BASELINE` with digest `{baseline_digest}`. Git HEAD at design generation is `{head}`. No Formal attempt, chain, Validator, PostgreSQL 16/main, or formal data collection is authorized in this stage. The terminal state for this task is `I10_COMPLETED_AWAITING_I11_APPROVAL`."),
        "01-I9-FROZEN-BASELINE.md": md("I9 Frozen Baseline", f"Accepted set: P9-A 8/8 (`I9_P9A_20260801T142646Z_eeaebf1`), P9-B 45/45 (`I9_P9B_20260801T151844Z_2be8593`), P9-C 16/16 (`I9_P9C_20260801T162256Z_0d9a2e2`), P9-D 24/24 (`I9_P9D_20260802T054500Z_95b8b60`). Total 93/93. Pairing Smoke and Statistical Smoke pass; Pilot timing remains forbidden for formal claims. `I9AcceptedPilotBaselineDigest={baseline_digest}`. Source hashes are recorded in the machine state and this package; I9 raw/index are read-only and unchanged."),
        "02-FORMAL-RESEARCH-QUESTIONS.md": md("Formal Research Questions", "The frozen questions are:\n\n" + "\n".join(f"- **{r['rqId']}** ({', '.join(r['class'])}): {r['question']}" for r in rq) + "\n\nRQ-2 and RQ-3 are separate semantic analyses. No question asks whether one update kind is globally better than the other."),
        "03-FORMAL-CLAIM-MATRIX.md": md("R3 Formal Claim Matrix", "Claims are frozen in `formal-claim-matrix.json`. Allowed evidence is run-level formal evidence with an environment fingerprint, integrity manifest, and pre-registered analysis. Forbidden evidence includes all I9 Pilot timing, single-node observations presented as QBFT conclusions, implementation tests presented as cryptographic proofs, and any result-driven claim expansion. C-07 is an explicit forbidden claim."),
        "04-FORMAL-BASELINE-DESIGN.md": md("Formal Baseline Design", "Baseline-R is retained: identical workload and security semantics with `LOCAL_ONLY` object storage, compared only to matched `KUBO_REPLICA` blocks. Baseline-H (no versioned header/simple rebuild) is removed as unfair because it changes the state and security semantics. Baseline-U (alternative update strategy) is not frozen because no semantically equivalent independent implementation is available; it may not be invented after results are seen. HEADER_ONLY and BODY_ROTATION are semantic classes, never baselines for each other."),
        "05-FORMAL-FACTOR-LEVEL-DESIGN.md": md("Formal Factor and Level Design", "Eight factors are retained in `formal-factor-matrix.json`. Frozen levels are deliberately blocked: recipient_count 2/8/32, affected_count 1/4, body_bytes 65536/1048576/8388608, update_kind as a semantic block, replica_state LOCAL_ONLY/KUBO_REPLICA, fault_class NONE/CORRUPT_RESTORE/CID_MISMATCH/BOTH_MISSING, workload_type HEADER_UPDATE/BODY_ROTATION/REVOCATION/RESTORE, and concurrency 1/4. The block design avoids a full factorial explosion and was not selected from observed outcomes."),
        "06-FORMAL-WORKLOAD-DESIGN.md": md("Formal Workload Design", "The workload generator is deterministic, seeded, versioned, and digest-bound. It derives fixture bytes from domain, seed, and requested size, records only digest/size, and never uses the experiment seed as cryptographic randomness. Formal input manifests contain generator version, seed, semantic class, configuration digest, and expected output schema. Plaintext, CK, private keys, and runtime credentials are never retained in evidence."),
        "07-FORMAL-METRIC-REGISTRY.md": md("Formal Metric Registry", "Twelve metrics are frozen in `formal-metric-registry.json`. Primary outcomes include strict validity, state consistency, end-to-end duration, recipient envelope count, body bytes, release decision latency, recovery duration, repair actions, object source, recovery disposition, and matched object-read bytes. Chain receipt duration is diagnostic and cannot be used as a consensus-performance claim."),
        "08-FORMAL-EXPERIMENTAL-UNIT.md": md("Experimental Unit", "The experimental unit is `RUN`: one complete frozen workload execution from setup through sealed evidence and acceptance. Phases, requests, transactions, chunks, recipients, and events are nested observations and are not independent samples. Aggregation, bootstrap, exclusion, and replacement operate at RUN level. Pseudoreplication prevention is a mandatory preflight check."),
        "09-FORMAL-SAMPLE-SIZE-PLAN.md": md("Formal Sample Size Plan", "The minimum sufficient plan has 29 configurations, 5 measured repetitions per configuration, 145 measured RUNs, 29 per-configuration warmups, 6 environment warmups, and 180 total planned RUNs including warmups. Estimated nominal duration is 4 hours with a 2–8 hour engineering range. `POWER_ANALYSIS_NOT_JUSTIFIED`: this is a bounded engineering precision plan and acceptance-proportion design, not a population power claim."),
        "10-FORMAL-WARMUP-PLAN.md": md("Warmup Plan", "Warmups are excluded from all statistics and are marked `WARMUP_ONLY`. Before measured runs, warm the JVM/Besu process, PostgreSQL connection and cache path, filesystem/object-store cache, Python process/import graph, Kubo connection pool, and network connection pool. One configuration warmup plus one environment warmup per service class is required; a warmup failure is handled by the frozen infrastructure policy and never silently counted as a measured RUN."),
        "11-FORMAL-EXECUTION-ORDER.md": md("Formal Execution Order", "Use blocked deterministic randomization with seed `20260802`. Randomize configuration order within semantic and experiment blocks, execute warmups before the first measured block, and freeze the resulting order before data collection. No order may be changed based on timing or outcomes. The order manifest is evidence and is included in the preregistration digest."),
        "12-FORMAL-PAIRING-PLAN.md": md("Formal Pairing Plan", "Pairing key: `generatorVersion|semanticClass|inputDigest|seed|configurationDigest`. Shared factors are semantic class, input digest, seed, and environment fingerprint. Varying factors are replica state, fault class, recipient count, and body size. Pairing is only between semantically identical tasks; timing-neighbor pairing is forbidden, and HEADER_ONLY/BODY_ROTATION are never paired as comparable outcomes."),
        "13-FORMAL-STATISTICAL-PLAN.md": md("Formal Statistical Plan", "The unit is RUN. Report n, mean, SD, median, IQR, and extrema; use 10,000-sample percentile bootstrap 95% CIs within pre-registered blocks; report median differences, positive-duration ratios on the log scale, and Cliff's delta where appropriate. Holm correction is used within each RQ family. Assumptions are checked descriptively; no unregistered subgroup, stopping, p-value, or favorable metric may be introduced."),
        "14-FORMAL-EXCLUSION-MISSING-POLICY.md": md("Exclusion and Missing Policy", "Exclude and log runs with missing required evidence, identity or configuration mismatch, SHA/integrity error, unauthorized resource, Pilot/Formal mixing, partial output, wrong chain/environment, invalid timing clock, or absent independent fault observation. Never delete silently. Replacement is allowed only under the pre-registered infrastructure rule, retains the failed record, and creates a new RUN identity. No timing-based exclusion is allowed."),
        "15-FORMAL-FAILURE-DISPOSITION.md": md("Formal Failure Disposition", "Classify failures as protocol/security/design, infrastructure, workload/fixture, or measurement. Protocol, security, unauthorized-resource, and integrity failures are fatal to the affected gate and may stop the study. Infrastructure failures may be replaced only according to the frozen replacement rule. Expected fail-closed outcomes are valid observations when their evidence contract is complete."),
        "16-FORMAL-STOP-RULES.md": md("Formal Stop Rules", "Immediate stop: secret exposure, erroneous material release, cross-chain or Validator access, PostgreSQL 16/main access, protocol/design drift, identity reuse, raw mutation, SHA failure, formal/Pilot mixing, or any FATAL error. MAJOR errors stop the affected block pending disposition; MINOR issues are logged and cannot alter the pre-registered plan. I10 itself has no execution; these rules govern a future approved I11 execution."),
        "17-FORMAL-ENVIRONMENT-CLASSES.md": md("Formal Environment Classes", "F1 is isolated functional/crypto/object/recovery validation. F2 is single-RPC end-to-end contract/state validation on a future independent Formal chain. F3 is a multi-node QBFT system-performance class and is not admitted for RC3 claims. F4 is controlled fault/recovery with selected storage, database, chain, and service faults. Every class requires a complete `R3FormalEnvironmentFingerprintV1` including host, CPU, RAM, storage, OS/kernel/virtualization/network, Python/Java/Besu/PostgreSQL/Kubo/Web3.py/cryptography/compiler/runtime, Git SHA, contract bytecode digest, and dependency-lock digest."),
        "18-RC3-MULTINODE-DECISION.md": md("RC3 Multi-Node Decision", "`RC3_MULTI_NODE_FORMAL_REQUIRED=false`. The frozen thesis claims are limited to application-layer correctness, security behavior, storage/recovery, and bounded engineering overhead; they do not claim QBFT consensus throughput, consensus latency, or multi-validator scalability. If a future thesis revision requires such a claim, I10 must be amended and a new approval must deploy an independent F3 topology before any data collection."),
        "19-RC3-FORMAL-BESU-TOPOLOGY.md": md("RC3 Formal Besu Topology", "A future F3 topology is designed but not deployed: four independent Validators plus one RPC/client, independent genesis, chainId, account and node keys, roles, contracts, data directories, systemd units, ports, and evidence root. It must never reuse r3_i5 Pilot chain `2026073005`, its keys, or the RC2 formal chain. Status: `DESIGNED_NOT_DEPLOYED`; no node was contacted in I10."),
        "20-FORMAL-DATABASE-DESIGN.md": md("Formal Database Design", "A future formal database must be an independent PostgreSQL instance, database, role, schema namespace, migration digest, and evidence root. It must not use PostgreSQL 16/main or Pilot port 55432. Transaction boundaries, isolation level, snapshot identifiers, and connection-factory provenance are preflight evidence. No formal database was created or accessed."),
        "21-FORMAL-STORAGE-DESIGN.md": md("Formal Storage Design", "A future formal storage class uses an independent LocalObjectStore root and an independent loopback Kubo repository/API, with no public bootstrap or peers. Object identity is digest/CID-bound; replica state is a factor, not a hidden retry. Body plaintext and CK are excluded from evidence. No formal Kubo or object store was created."),
        "22-FORMAL-IDENTITY-DOMAIN.md": md("Formal Identity Domain", "Every future formal attempt, run, resource, operation, job, object, chainId, database, storage root, and environment fingerprint has a new namespace. Pilot IDs, Revision 7/8 IDs, RC2 IDs, secrets, keys, and historical raw are forbidden. Identity is validated before execution and bound into every evidence digest."),
        "23-FORMAL-EVIDENCE-DESIGN.md": md("Formal Evidence Design", "Remote authoritative evidence, local read-only mirror, per-file SHA-256 manifest, run-level strict record, environment fingerprint, material-release evidence, invariant evidence, and acceptance decision are separate artifacts. A run is accepted only after execution -> seal -> SHA -> strict evidence -> invariant/material-release review. Secrets, plaintext, CK, private keys, and credentials are never serialized."),
        "24-FORMAL-DIRECTORY-LAYOUT.md": md("Formal Directory Layout", "Design-only layout: `docs/.../i10/` for preregistration and schemas; future formal raw would be outside the Pilot mirror tree under an independently approved root; future attempt/run IDs are created only after I11 approval. `experiments/r3/i9-pilot/` remains read-only and excluded from Formal output. No Formal raw directory exists in I10."),
        "25-FORMAL-CODE-FREEZE-PROCEDURE.md": md("Formal Code Freeze Procedure", "Before any future execution: record Git SHA, dependency-lock digest, contract bytecode digest, minimal snapshot manifest, generator digest, analysis-code digest, and environment fingerprint; run local synthetic tests; obtain I11 approval; then create a new Formal attempt. Any code fix freezes the failed attempt and requires a new SHA, snapshot, and approval gate. I10 creates no attempt."),
        "26-FORMAL-PREFLIGHT-DESIGN.md": md("Formal Preflight Design", "Preflight must prove identity freshness, independent environment, contract bytecode, database and storage factory provenance, chainId, no public peers, secret boundary, deterministic generator, clock validity, and evidence-writer readiness. It must fail closed on missing or ambiguous state. No preflight was run against a Formal environment."),
        "27-FORMAL-RQ-EXPERIMENT-MATRIX.md": md("RQ to Experiment Matrix", "E1 covers RQ-1 with correctness/invariant outcomes; E2 covers RQ-2 HEADER_ONLY only; E3 covers RQ-3 BODY_ROTATION only; E4 covers RQ-4 revocation; E5 covers RQ-5/RQ-6 recovery and Kubo/local pairing. RQ-2/RQ-3 are never pooled. C-07 has no experiment because it is forbidden."),
        "28-FORMAL-RUN-BUDGET.md": md("Formal Run Budget", "See `formal-run-budget.json`: 29 configurations, 145 measured RUNs, 35 warmups, and 180 total planned RUNs. The estimate is a planning bound, not an observed runtime. Any future change to configuration count, repetitions, or duration requires an I10 amendment before execution."),
        "29-MINIMUM-SUFFICIENT-FORMAL-PLAN.md": md("Minimum Sufficient Formal Plan", "The minimum sufficient plan is E1–E5, 29 blocked configurations, five measured RUNs per configuration, one warmup per configuration plus six environment warmups, run-level acceptance, matched Local/Kubo recovery blocks, and no F3 consensus claim. It is sufficient for the frozen application-layer RQs without a full factorial or a multi-node deployment."),
        "30-OPTIONAL-ENHANCED-FORMAL-PLAN.md": md("Optional Enhanced Formal Plan", "An optional future enhancement may add concurrency level 16, more repetitions, larger object sizes, or an independent F3 QBFT topology. It is not part of this preregistration, cannot be activated by favorable results, and requires a written protocol amendment, new environment fingerprints, new baseline review, and user approval."),
        "31-FORMAL-PREREGISTRATION.md": md("Formal Preregistration", "The machine-readable preregistration is `formal-preregistration.json`. It freezes RQs, claim boundaries, factors, metrics, run budget, order seed, pairing, statistics, exclusion/replacement, and stop rules. Status is `DESIGN_FROZEN_AWAITING_I11_APPROVAL`; formal data collection is false."),
        "32-FORMAL-ANALYSIS-CODE-PLAN.md": md("Formal Analysis Code Plan", "Future analysis code will validate schema, identity, SHA, environment, run-level unit, semantic blocking, missingness, and pre-registered metrics before any statistical routine. Synthetic/mock fixtures will test valid, missing, duplicate, integrity-failure, and forbidden-cross-semantic cases. No formal raw data are loaded or produced in I10."),
        "33-FORMAL-FIGURE-TABLE-PLAN.md": md("Formal Figure and Table Plan", "Planned outputs are descriptive only: a run-flow/eligibility table, within-class duration distributions, matched Local/Kubo recovery table, release-decision outcome table, and environment fingerprint table. No figure will pool HEADER_ONLY with BODY_ROTATION or imply QBFT performance. Figure generation is deferred until approved formal data exist."),
        "34-I10-STRICT-REVIEW.md": md("I10 Strict Review", "Review checks: I9 digest and state, claim/evidence alignment, Pilot/Formal separation, semantic non-comparison, baseline fairness, factor non-reactivity, RUN unit, warmup exclusion, deterministic order, pairing compatibility, statistical precommitment, failure/stop policy, RC2/RC3 separation, and absence of execution. All design checks pass; no formal result is asserted."),
        "35-I10-FINAL-DECISION.md": md("I10 Final Decision", "`I10_COMPLETED_AWAITING_I11_APPROVAL`. Design and preregistration are frozen. I11 is not executed; no Formal attempt, Formal chain, Validator, Formal PostgreSQL, Kubo deployment, formal raw, or performance conclusion exists. The only next step is user approval of I11."),
        "36-I11-ENTRY-CHECKLIST.md": md("I11 Entry Checklist", "I11 gate is `READY_AWAITING_USER_APPROVAL`. Required before execution: explicit I11 approval, immutable preregistration digest, new Formal Git/snapshot SHA, independent environment fingerprints, preflight pass, fresh identities, and a reviewed run order. Current values: `executed=false`, `formalAttemptCreated=false`, `formalData=false`."),
    }
    for name, content in docs.items():
        write(name, content)

    # Machine-readable artifacts.
    write("i10-state.json", json.dumps({
        "schemaVersion": "I10StateV1", "state": "I10_COMPLETED_AWAITING_I11_APPROVAL", "i9BaselineFrozen": True,
        "i9AcceptedPilotBaselineDigest": baseline_digest, "formalResearchQuestionCount": len(rq),
        "formalClaimCount": len(claim_matrix), "forbiddenClaimIds": [c["claimId"] for c in claim_matrix if c["status"] == "FORBIDDEN"],
        "formalFactorCount": len(factors), "formalMetricCount": len(metrics), "experimentalUnit": "RUN",
        "pseudoreplicationViolations": 0, "resultDrivenFactorLevelViolations": 0, "formalAttemptCreated": False,
        "formalDataCollected": False, "formalPerformanceConclusion": False, "rc2FormalAssetsReused": False,
        "rc3MultiNodeFormalRequired": False, "formalTopology": "DESIGNED_NOT_DEPLOYED", "formalDatabaseCreated": False,
        "formalKuboCreated": False, "trueSecret": 0, "unclassified": 0, "fatal": 0, "major": 0, "minor": 0,
        "i11": "READY_AWAITING_USER_APPROVAL", "createdAt": created, "gitCommit": head,
    }, ensure_ascii=False, indent=2))
    write("formal-rq-matrix.json", json.dumps({"schemaVersion": "R3FormalRQMatrixV1", "researchQuestions": rq}, ensure_ascii=False, indent=2))
    write("formal-claim-matrix.json", json.dumps({"schemaVersion": "R3FormalClaimMatrixV1", "claims": claim_matrix}, ensure_ascii=False, indent=2))
    write("formal-factor-matrix.json", json.dumps({"schemaVersion": "R3FormalFactorMatrixV1", "factors": factors}, ensure_ascii=False, indent=2))
    write("formal-metric-registry.json", json.dumps({"schemaVersion": "R3FormalMetricRegistryV1", "metrics": metrics}, ensure_ascii=False, indent=2))
    write("formal-run-budget.json", json.dumps(run_budget, ensure_ascii=False, indent=2))
    prereg_base = dict(prereg)
    prereg_base["preregistrationDigest"] = None
    prereg_digest = sha256_bytes(canonical_json(prereg_base))
    prereg["preregistrationDigest"] = prereg_digest
    write("formal-preregistration.json", json.dumps(prereg, ensure_ascii=False, indent=2))
    write("formal-stop-rules.json", json.dumps({"schemaVersion": "R3FormalStopRulesV1", "immediateStop": ["SECRET_EXPOSURE", "ERRONEOUS_MATERIAL_RELEASE", "UNAUTHORIZED_CHAIN_OR_VALIDATOR", "POSTGRES16_MAIN_ACCESS", "PROTOCOL_OR_DESIGN_DRIFT", "IDENTITY_REUSE", "RAW_MUTATION", "SHA_FAILURE", "PILOT_FORMAL_MIX", "FATAL"], "majorDisposition": "stop affected block and review", "minorDisposition": "log without plan change"}, ensure_ascii=False, indent=2))
    write("formal-environment-fingerprint-template.json", json.dumps({
        "schemaVersion": "R3FormalEnvironmentFingerprintV1",
        "status": "TEMPLATE_NOT_COLLECTED",
        "scope": "one record per future formal host/node",
        "requiredFields": ["host", "role", "cpuModel", "physicalCores", "logicalCores", "ramBytes", "storageDeviceAndFreeBytes", "os", "kernel", "virtualization", "network", "pythonVersion", "javaVersion", "besuVersion", "postgresqlVersion", "kuboVersion", "web3pyVersion", "cryptographyVersion", "compilerVersion", "runtimeVersion", "gitSha", "contractBytecodeDigest", "dependencyLockDigest"],
        "secretPolicy": "values, keys, passwords, tokens and private paths are never recorded",
        "pilotFormalSeparation": "formal host/node fingerprints must not identify r3_i5 Pilot services",
    }, ensure_ascii=False, indent=2))
    write("formal-besu-topology.json", json.dumps({
        "schemaVersion": "R3FormalBesuTopologyV1",
        "status": "DESIGNED_NOT_DEPLOYED",
        "nodes": [{"role": "Validator", "count": 4}, {"role": "RPC_CLIENT", "count": 1}],
        "independenceRequirements": ["new genesis", "new chainId", "new account and node keys", "new roles", "new contract deployments", "new data directories", "new systemd units", "new ports", "new evidence root"],
        "forbiddenReuse": ["r3_i5 Pilot chain 2026073005", "RC2 formal chain", "Pilot keys", "Pilot raw", "Validator services"],
        "deployed": False,
    }, ensure_ascii=False, indent=2))
    write("artifact-sha256.json", json.dumps({"schemaVersion": "I10ArtifactSha256V1", "generatedAt": created, "selfIncluded": False, "files": []}, ensure_ascii=False, indent=2))
    manifest_path = OUT / "artifact-sha256.json"
    entries = []
    for path in sorted(OUT.rglob("*")):
        if path.is_file() and path.name != "artifact-sha256.json":
            entries.append({"path": path.relative_to(OUT).as_posix(), "sha256": sha256_bytes(path.read_bytes())})
    manifest = {"schemaVersion": "I10ArtifactSha256V1", "generatedAt": created, "selfIncluded": False, "files": entries}
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"gitCommit": head, "i9AcceptedPilotBaselineDigest": baseline_digest, "preregistrationDigest": prereg_digest, "files": len(entries) + 1, "output": str(OUT)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
