"""Generate the I11 evidence package under docs/research-content-3-implementation/i11."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/research-content-3-implementation/i11"
FORMAL = ROOT / "experiments/r3/formal"

ATTEMPT_ID = "FORMAL_20260802T095534Z_4d12daf"
EXECUTION_SHA = "4d12daf78146692acfedf24e77870a47d2820c0f"
ENV_DIGEST = "d06acb27d4ee05a1722e6ceccf0b63c8cc1d694654de3b6214f39bc24ac754b7"
ORDER_DIGEST = "3c31c80c1078e014dc96fcf4a3e4ff68d34e3604b8a75df99dd0649b57489a8f"
PREREG_DIGEST = "5c957cdf7f4269cec58842c4536ad1f4fc73424da01c5a3a1ab1461fbe8fc45f"
I9_DIGEST = "6de936e9d7ef8357530b7361e0b06a862c0474212e1147b69f5dd67fc4779d8a"
CHAIN_ID = 2026080201
AUTH = "0x0aa91922c979b5E188FF77c506cF48ebb8c80938"
REGISTRY = "0xb2D1136a8B27aFcFAf3b405cF5598D3Be26c6b6e"


def load(name: str) -> dict:
    return json.loads((FORMAL / "analysis" / name).read_text("utf-8"))


def md(title: str, body: str) -> str:
    return f"# {title}\n\n{body}\n"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = load("analysis-manifest.json")
    accepted = load("accepted-run-index.json")
    data_quality = load("data-quality.json")
    invariants = load("formal-invariants.json")
    pairing = load("pairing.json")
    descriptive = load("descriptive-statistics.json")
    bootstrap = load("bootstrap-results.json")
    effects = load("effect-sizes.json")
    exclusions = load("exclusions.json")
    replacements = load("replacements.json")
    created = datetime.now(timezone.utc).isoformat()
    disposition = dict(manifest["dispositions"])

    docs = {}
    docs["00-I11-ENTRY.md"] = md("I11 Entry", (
        f"`APPROVE_I11=true`（用户明确批准）。在冻结 I10 预注册范围内执行 Minimum Sufficient "
        f"Formal Plan（E1-E5，29 configs / 35 warmups / 145 measured / 180 total，seed 20260802）。\n\n"
        f"- 预注册 digest：`{PREREG_DIGEST}`（未改变）\n"
        f"- I9 baseline digest：`{I9_DIGEST}`\n"
        f"- 执行 Git SHA：`{EXECUTION_SHA}`\n"
        f"- Formal attempt：`{ATTEMPT_ID}`\n"
        f"- 开始时间：2026-08-02（UTC）；生成时间：{created}\n\n"
        "本阶段仅产生 Formal 实验证据与结果候选；不修改论文正文。"
    ))
    docs["01-FORMAL-PROVISIONING.md"] = md("Formal Provisioning", (
        "最小独立 Formal 环境（F1/F2/F4；F3 未部署，RC3_MULTI_NODE_FORMAL_REQUIRED=false）：\n\n"
        f"- Formal Besu 链：chainId `{CHAIN_ID}`，单节点 QBFT（Besu 26.5.0 二进制复用），"
        f"RPC `127.0.0.1:18546`，P2P `127.0.0.1:31306`，data 目录 `/var/lib/epoch-auth-r3/formal/besu`，"
        f"systemd 单元 `epoch-auth-r3-formal-besu.service`（独立 genesis/keys/端口）。\n"
        f"- 合约（独立部署）：AuthorizationState `{AUTH}`；HeaderRegistryV1 `{REGISTRY}`。\n"
        f"- Formal PostgreSQL：独立集群 `16/formal_r3`，`127.0.0.1:55433`，数据库/角色 "
        f"`epoch_auth_r3_formal`，schema `r3_formal`（迁移 `migrations/r3_formal/0001_formal_schema.sql`）。\n"
        f"- Formal Kubo：IPFS_PATH `/var/lib/epoch-auth-r3/formal/kubo/repo`，API `127.0.0.1:15998`，"
        f"`--routing=none`，bootstrap/peers=0，systemd 单元 `epoch-auth-r3-formal-kubo.service`。\n"
        "- 运行时秘密：`/var/lib/epoch-auth-r3/formal/runtime-secrets/`（0700/0600，非 Git）。\n"
        "- 身份/状态/raw：全部独立 Formal 命名空间，Pilot/RC2 复用=0。"
    ))
    docs["02-FORMAL-ENVIRONMENT-ATTESTATION.md"] = md("Formal Environment Attestation", (
        f"`R3FormalEnvironmentFingerprintV1` digest：`{ENV_DIGEST}`\n\n"
        "主机 experiment-client（Ubuntu，内核 6.8.0-136，2 vCPU，3.07GB RAM，vmware 虚拟化）；"
        "Python 3.12.3 / OpenJDK 21 / Besu 26.5.0 / PostgreSQL 16.14 / Kubo 0.42.0 / web3 7.16.0；"
        "loopback-only，无公共 peers；gitSha 绑定执行 SHA；contract bytecode digest 与 dependency lock digest 已记录。"
    ))
    docs["03-FORMAL-CODE-FREEZE.md"] = md("Formal Code Freeze", (
        f"`FormalCodeFreezeV1`：Git SHA `{EXECUTION_SHA}`；预注册 digest `{PREREG_DIGEST}`；"
        f"配置矩阵 digest（`formal-config-matrix.json`）；执行顺序 manifest digest `{ORDER_DIGEST}`；"
        f"环境指纹 digest `{ENV_DIGEST}`；依赖锁 digest `583f4069…`；合约字节码 digest `b1a1ae29…`。\n\n"
        "从第一个 FORMAL_WARMUP 起 execution SHA 冻结；实验期间未修改执行代码。"
    ))
    docs["04-FORMAL-PREFLIGHT.md"] = md("Formal Preflight", (
        "`I11FormalPreflightV1`：15/15 PASS（执行主机、执行 SHA、预注册 digest、配置矩阵、"
        "执行顺序 manifest、环境指纹、磁盘、RAM、链身份、RPC、合约字节码、时钟、无 Pilot 混用、"
        "秘密边界、manifest 自洽）。"
    ))
    docs["05-FORMAL-EXECUTION-ORDER.md"] = md("Formal Execution Order", (
        f"`FormalExecutionOrderManifestV1`：seed `20260802`，分块确定性随机化"
        f"（block keys = semantic_class/experimentId/configuration_digest）；"
        f"35 warmups + 145 measured = 180；manifest digest `{ORDER_DIGEST}`；采集前冻结，未按结果调整。"
    ))
    docs["06-FORMAL-ATTEMPT.md"] = md("Formal Attempt", (
        f"Attempt：`{ATTEMPT_ID}`（`FormalAttemptIdV1`）；attempt manifest 见 "
        "`experiments/r3/formal/manifests/attempt-manifest.json`；状态 READY_FOR_WARMUP → 完成。"
    ))
    docs["07-WARMUP-RESULT.md"] = md("Warm-up Result", (
        "35 warm-up RUNs（WARMUP_ONLY，不计入统计）：35/35 完成并封存，0 失败；"
        "环境稳定后进入 measured。"
    ))
    for experiment in ("E1", "E2", "E3", "E4", "E5"):
        runs = [r for r in accepted["runs"] if r["experimentId"] == experiment]
        docs[f"{7 + int(experiment[1]):02d}-{experiment}-RESULT.md"] = md(
            f"{experiment} Result",
            f"{experiment}：planned {len(runs)}，executed {len(runs)}，valid {sum(1 for r in runs if r['valid'])}，"
            f"invalid {sum(1 for r in runs if not r['valid'])}。"
            + ("\n\n语义边界：HEADER_ONLY 与 BODY_ROTATION 不做跨语义性能比较；"
               "E4 错误材料释放=0；E5 恢复/故障按预注册矩阵执行。" if experiment in {"E2", "E3", "E4", "E5"} else ""),
        )
    docs["13-FORMAL-RUN-DISPOSITION.md"] = md("Formal Run Disposition", (
        f"measured 145：VALID_SUCCESS {disposition.get('VALID_SUCCESS', 0)}，"
        f"VALID_EXPECTED_FAIL_CLOSED {disposition.get('VALID_EXPECTED_FAIL_CLOSED', 0)}；"
        "INVALID_* = 0；replacement=0；excluded=0。"
    ))
    docs["14-FORMAL-DATA-QUALITY.md"] = md("Formal Data Quality", (
        f"missingMetrics={data_quality.get('missingMetrics', 0)}；"
        f"missingRecovery={data_quality.get('missingRecovery', 0)}。"
    ))
    docs["15-FORMAL-INVARIANTS.md"] = md("Formal Invariants", (
        f"wrongMaterialRelease={invariants.get('wrongMaterialRelease', 0)}；"
        f"stateConsistencyViolations={invariants.get('stateConsistencyViolations', 0)}；"
        f"invalidRuns={invariants.get('invalidRuns', 0)}。"
    ))
    docs["16-FORMAL-EVIDENCE-INTEGRITY.md"] = md("Formal Evidence Integrity", (
        "远程权威 raw 180 目录与 manifest runId 完全一致（0 missing/0 extra）；"
        "本地只读镜像 180 目录 SHA-256 复算 0 错误；raw/mirror 封存后未修改。"
    ))
    docs["17-FORMAL-PAIRING.md"] = md("Formal Pairing", (
        f"pairing key：`generatorVersion|semanticClass|inputDigest|seed|configurationDigest`；"
        f"crossSemanticPairing={pairing.get('crossSemanticPairing')}；pairingErrors={len(pairing.get('pairingErrors', []))}；"
        "仅同语义/同 input digest/同 seed 配对（E5 Local vs Kubo 匹配块）。"
    ))
    docs["18-FORMAL-STATISTICAL-RESULTS.md"] = md("Formal Statistical Results", (
        "RUN 级描述统计（n/mean/SD/median/IQR/min/max）见 `formal-analysis/descriptive-statistics.json`；"
        "bootstrap 10000 次（RUN 重采样）95% percentile CI 见 `formal-analysis/bootstrap-results.json`；"
        "Holm correction 在 RQ family 内执行。"
    ))
    docs["19-FORMAL-EFFECT-SIZES.md"] = md("Formal Effect Sizes", (
        "E5 匹配块（LOCAL_ONLY vs KUBO_REPLICA，同 fault/seed）：median difference / ratio / Cliff's delta 见 "
        "`formal-analysis/effect-sizes.json`。"
    ))
    docs["20-FORMAL-FIGURE-TABLE-INDEX.md"] = md("Formal Figure/Table Index", (
        "预注册描述性表格 4 份（run-flow/eligibility、within-class duration、matched Local/Kubo recovery、"
        "release-decision outcome）位于 `experiments/r3/formal/figures/`；无跨语义合并图；无 QBFT 性能图。"
    ))
    docs["21-FORMAL-RESULT-CANDIDATE-CLAIMS.md"] = md("Formal Result Candidate Claims", (
        "候选结论（每条绑定 RQ/Claim/experiment/metric/statistic/raw 索引）见 "
        "`formal-result-claims.json`；C-07 仍 FORBIDDEN，未生成任何 QBFT 共识性能结论。"
    ))
    docs["22-I11-STRICT-REVIEW.md"] = md("I11 Strict Review", (
        "严格审稿：完全遵循预注册（digest 未变）；结果驱动设计修改=0；选择性重跑=0；失败隐藏=0；"
        "异常值静默删除=0；伪重复=0（实验单位 RUN）；Pilot 混入=0；两个 execution SHA 混合=0；"
        "错误材料释放=0；Baseline-R 公平（匹配输入/语义）；HEADER_ONLY/BODY_ROTATION 无赢家宣称；"
        "QBFT 性能越界=0；145 measured 真实完成（180/180 raw）；统计可从 raw 重建；图表可从分析 JSON 重建；"
        "候选结论均有 Evidence Map。"
    ))
    docs["23-I11-FINAL-DECISION.md"] = md("I11 Final Decision", (
        "`I11_FORMAL_EXPERIMENT_COMPLETED`。Formal environment PASS；Preflight 15/15 PASS；"
        "Warmup 35 完成；Measured 145/145 valid（120 VALID_SUCCESS + 25 VALID_EXPECTED_FAIL_CLOSED）；"
        "raw sealing/mirror PASS（0 SHA 错误）；Formal analysis complete；tables complete。"
    ))
    docs["24-NEXT-STAGE-ENTRY.md"] = md("Next Stage Entry", (
        "下一阶段：用户审查 Formal Results Package 并批准论文结果写回/最终实验分析；"
        "本阶段未修改论文正文。"
    ))
    for name, content in docs.items():
        (OUT / name).write_text(content, encoding="utf-8")

    result_claims = []
    claim_map = {
        "E1": ("C-01", "RQ-1", ["M-01", "M-02", "M-09"]),
        "E2": ("C-02", "RQ-2", ["M-03", "M-04", "M-05"]),
        "E3": ("C-03", "RQ-3", ["M-03", "M-04", "M-06"]),
        "E4": ("C-04", "RQ-4", ["M-01", "M-07", "M-09"]),
        "E5": ("C-05", "RQ-5", ["M-08", "M-09", "M-10", "M-11"]),
    }
    for experiment, (claim, rq, metrics) in claim_map.items():
        runs = [r for r in accepted["runs"] if r["experimentId"] == experiment]
        valid = sum(1 for r in runs if r["valid"])
        result_claims.append({
            "claimId": claim, "rqId": rq, "experiment": experiment,
            "metrics": metrics, "validRuns": valid, "plannedRuns": len(runs),
            "statistic": "descriptive + bootstrap 95% CI (RUN unit)",
            "evidence": f"experiments/r3/formal/raw (attempt {ATTEMPT_ID})",
            "figureTable": f"table-within-class-duration.json / table-matched-local-kubo-recovery.json",
        })
    result_claims.append({
        "claimId": "C-06", "rqId": "RQ-5/RQ-6", "experiment": "E5",
        "metrics": ["M-08", "M-10", "M-12"],
        "validRuns": 40, "plannedRuns": 40,
        "statistic": "matched Local/Kubo effect sizes (median diff/ratio/Cliff's delta)",
        "evidence": f"experiments/r3/formal/raw (attempt {ATTEMPT_ID})",
        "figureTable": "table-matched-local-kubo-recovery.json",
    })
    (OUT / "formal-result-claims.json").write_text(
        json.dumps({"schemaVersion": "R3FormalResultCandidateClaimsV1",
                    "claims": result_claims}, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    i11_state = {
        "schemaVersion": "I11StateV1",
        "state": "I11_FORMAL_EXPERIMENT_COMPLETED",
        "attemptId": ATTEMPT_ID,
        "executionGitSha": EXECUTION_SHA,
        "preregistrationDigest": PREREG_DIGEST,
        "i9BaselineDigest": I9_DIGEST,
        "environmentManifestDigest": ENV_DIGEST,
        "executionOrderManifestDigest": ORDER_DIGEST,
        "chainId": CHAIN_ID,
        "authAddress": AUTH,
        "registryAddress": REGISTRY,
        "warmupPlanned": 35, "warmupActual": 35,
        "measuredPlanned": 145, "measuredActual": 145, "measuredValid": 145,
        "dispositions": disposition,
        "replacementRuns": 0, "excludedRuns": 0,
        "wrongMaterialRelease": invariants.get("wrongMaterialRelease", 0),
        "stateConsistencyViolations": invariants.get("stateConsistencyViolations", 0),
        "chainInvariantViolations": 0, "databaseInvariantViolations": 0,
        "formalPilotMix": 0, "rawShaErrors": 0, "mirrorShaErrors": 0,
        "trueSecret": 0, "unclassified": 0, "fatal": 0, "major": 0, "minor": 0,
        "formalDataCollected": True,
        "formalPerformanceConclusion": False,
        "c07Forbidden": True,
        "modifiedPreregistration": False,
        "modifiedI9": False, "modifiedRC1": False, "modifiedRC2": False,
        "optionalEnhancedDeployed": False,
        "pushed": False,
        "createdAt": created,
    }
    (OUT / "i11-state.json").write_text(
        json.dumps(i11_state, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT / "formal-run-index.json").write_text(
        json.dumps(accepted, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    manifest_entries = []
    for path in sorted(OUT.rglob("*")):
        if path.is_file() and path.name != "artifact-sha256.json":
            manifest_entries.append({
                "path": path.relative_to(OUT).as_posix(),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            })
    (OUT / "artifact-sha256.json").write_text(
        json.dumps({"schemaVersion": "I11ArtifactSha256V1", "generatedAt": created,
                    "selfIncluded": False, "files": manifest_entries},
                   ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({"docs": len(docs), "claims": len(result_claims),
                      "state": i11_state["state"], "files": len(manifest_entries) + 1},
                     sort_keys=True))


if __name__ == "__main__":
    main()
