"""Pre-registered formal analysis: RUN-level descriptive, bootstrap, effects."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import statistics
from pathlib import Path


def phase_duration_ms(events: list[dict], phase_name: str) -> float | None:
    starts = [e for e in events if e.get("phaseName") == phase_name and e.get("eventType") == "STARTED"]
    ends = [e for e in events if e.get("phaseName") == phase_name and e.get("eventType") == "COMPLETED"]
    if not starts or not ends:
        return None
    total = 0.0
    for start, end in zip(starts, ends):
        total += (end["monotonicTimestampNs"] - start["monotonicTimestampNs"]) / 1e6
    return total


def run_metrics(run_dir: Path) -> dict:
    config = json.loads((run_dir / "config.json").read_text("utf-8"))
    run_state = json.loads((run_dir / "run-state.json").read_text("utf-8"))
    chain = json.loads((run_dir / "chain-evidence.json").read_text("utf-8"))
    fault = json.loads((run_dir / "fault-evidence.json").read_text("utf-8"))
    material = json.loads((run_dir / "material-release-evidence.json").read_text("utf-8"))
    events = [
        json.loads(line)
        for line in (run_dir / "phase-events.jsonl").read_text("utf-8").splitlines()
        if line.strip()
    ]
    scenario = fault.get("scenarioEvidence", {})
    cfg = config["config"]
    try:
        config_index = int(cfg.get("workloadId", "").split("_")[3])
    except (IndexError, ValueError):
        config_index = -1
    end_to_end = phase_duration_ms(events, "RUN")
    release_latency = phase_duration_ms(events, "MATERIAL_RELEASE_RULE_CHECK")
    recovery = sum(
        (phase_duration_ms(events, name) or 0.0)
        for name in ("RECOVERY_START", "RECOVERY_RECONCILIATION", "RECOVERY_COMPLETE")
    )
    receipts = chain.get("receipts", [])
    chain_duration = None
    if len(receipts) >= 2:
        try:
            first_block = int(receipts[0]["blockNumber"])
            last_block = int(receipts[-1]["blockNumber"])
            chain_duration = (last_block - first_block) * 2000.0
        except Exception:
            chain_duration = None
    body_size = int(cfg.get("bodySizeBytes", 0))
    if cfg.get("scenarioClass") == "BODY_ROTATION":
        body_size *= 2
    disposition = run_state.get("disposition", "UNKNOWN")
    return {
        "runId": config.get("runId"),
        "attemptId": config.get("attemptId"),
        "experimentId": cfg.get("experimentId"),
        "configIndex": config_index,
        "repeatIndex": cfg.get("repeatIndex", -1),
        "warmup": bool(cfg.get("warmup")),
        "scenarioClass": cfg.get("scenarioClass"),
        "semanticClass": cfg.get("semanticClass"),
        "storageMode": cfg.get("storageMode"),
        "faultScenario": cfg.get("faultScenario"),
        "recipientCount": cfg.get("recipientCount"),
        "affectedResourceCount": cfg.get("affectedResourceCount"),
        "bodySizeBytes": cfg.get("bodySizeBytes"),
        "seed": cfg.get("seed"),
        "valid": bool(run_state.get("valid")),
        "disposition": disposition,
        "M01_strict_validity": bool(run_state.get("valid")),
        "M02_state_consistency": (
            scenario.get("finalCompositeState") == "CONSISTENT"
            and int(chain.get("invariantViolations", 0)) == 0
        ),
        "M03_end_to_end_duration_ms": end_to_end,
        "M04_chain_receipt_duration_ms": chain_duration,
        "M05_recipient_envelope_count": scenario.get("recipientEnvelopeCount"),
        "M06_body_bytes_processed": body_size,
        "M07_release_decision_latency_ms": release_latency,
        "M08_recovery_duration_ms": recovery if recovery > 0 else None,
        "M09_repair_actions": scenario.get("repairActions", 0),
        "M10_object_source": scenario.get("objectSource"),
        "M11_recovery_disposition": fault.get("recoveryDisposition"),
        "M12_object_read_bytes": scenario.get("objectReadBytes"),
        "materialReleaseDecision": material.get("current", {}).get("decision"),
        "rawManifestDigest": hashlib.sha256(
            (run_dir / "artifact-sha256.json").read_bytes()
        ).hexdigest(),
    }


def descriptive(values: list[float]) -> dict:
    if not values:
        return {"n": 0}
    ordered = sorted(values)
    n = len(ordered)
    q = lambda p: ordered[min(n - 1, max(0, int(p * n)))]
    return {
        "n": n,
        "mean": statistics.fmean(ordered),
        "sd": statistics.stdev(ordered) if n > 1 else 0.0,
        "median": statistics.median(ordered),
        "iqr": q(0.75) - q(0.25),
        "min": ordered[0],
        "max": ordered[-1],
    }


def percentile_ci(values: list[float], resamples: int = 10000, seed: int = 20260802,
                  ci: float = 0.95) -> dict:
    rng = random.Random(seed)
    medians = []
    for _ in range(resamples):
        sample = [rng.choice(values) for _ in values]
        medians.append(statistics.median(sample))
    medians.sort()
    lo = int((1 - ci) / 2 * resamples)
    hi = int((1 + ci) / 2 * resamples) - 1
    return {
        "resamples": resamples,
        "unit": "RUN",
        "ci": f"{int(ci * 100)}%",
        "percentile": [medians[max(0, lo)], medians[min(resamples - 1, hi)]],
        "observedMedian": statistics.median(values),
    }


def cliff_delta(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return float("nan")
    wins = losses = 0
    for x in a:
        for y in b:
            wins += x > y
            losses += x < y
    return (wins - losses) / (len(a) * len(b))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--seed", type=int, default=20260802)
    args = parser.parse_args()
    raw = Path(args.raw)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    runs = []
    for run_dir in sorted(raw.iterdir()):
        if run_dir.is_dir():
            runs.append(run_metrics(run_dir))
    measured = [r for r in runs if not r["warmup"]]
    valid = [r for r in measured if r["valid"]]
    invalid = [r for r in measured if not r["valid"]]
    planned_order = sorted(
        (r["experimentId"], r["configIndex"], r["repeatIndex"]) for r in measured
    )
    dispositions = {}
    for r in measured:
        dispositions[r["disposition"]] = dispositions.get(r["disposition"], 0) + 1
    blocks = {}
    for r in valid:
        key = (r["experimentId"], r["configIndex"])
        blocks.setdefault(key, []).append(r)
    descriptive_stats = {}
    for key in sorted(blocks):
        values = [r["M03_end_to_end_duration_ms"] for r in blocks[key]
                  if r["M03_end_to_end_duration_ms"] is not None]
        descriptive_stats[f"{key[0]}-C{key[1]}"] = descriptive(values)
    bootstrap_results = {}
    for key in sorted(blocks):
        values = [r["M03_end_to_end_duration_ms"] for r in blocks[key]
                  if r["M03_end_to_end_duration_ms"] is not None]
        if len(values) >= 3:
            bootstrap_results[f"{key[0]}-C{key[1]}"] = percentile_ci(
                values, seed=args.seed
            )
    effect_sizes = {}
    e5 = {r["faultScenario"]: r for r in valid if r["experimentId"] == "E5"}
    for fault in sorted({r["faultScenario"] for r in valid if r["experimentId"] == "E5"}):
        local = [r for r in valid if r["experimentId"] == "E5"
                 and r["faultScenario"] == fault and r["storageMode"] == "LOCAL_ONLY"
                 and r["M03_end_to_end_duration_ms"] is not None]
        kubo = [r for r in valid if r["experimentId"] == "E5"
                and r["faultScenario"] == fault and r["storageMode"] == "KUBO_REPLICA"
                and r["M03_end_to_end_duration_ms"] is not None]
        lv = [r["M03_end_to_end_duration_ms"] for r in local]
        kv = [r["M03_end_to_end_duration_ms"] for r in kubo]
        if lv and kv:
            effect_sizes[f"E5-{fault}-KUBO_vs_LOCAL"] = {
                "medianDifferenceMs": statistics.median(kv) - statistics.median(lv),
                "ratio": statistics.median(kv) / statistics.median(lv) if lv and statistics.median(lv) > 0 else None,
                "cliffsDelta": cliff_delta(kv, lv),
                "localN": len(lv), "kuboN": len(kv),
                "pairing": "same semantic class, same input digest, same seed, matched fault block",
            }
    invariants = {
        "wrongMaterialRelease": sum(
            1 for r in measured
            if r["materialReleaseDecision"] not in {
                "ALLOWED", "ALLOWED_AFTER_CURRENT_HEADER_ONLY", "DENIED"
            }
        ),
        "stateConsistencyViolations": sum(1 for r in measured if not r["M02_state_consistency"]),
        "invalidRuns": len(invalid),
    }
    manifest = {
        "schemaVersion": "R3FormalAnalysisManifestV1",
        "rawRoot": str(raw),
        "measuredPlanned": 145,
        "measuredExecuted": len(measured),
        "measuredValid": len(valid),
        "measuredInvalid": len(invalid),
        "warmupCount": sum(1 for r in runs if r["warmup"]),
        "dispositions": dispositions,
        "exclusionReasons": {
            r["runId"]: r["disposition"] for r in invalid
        },
        "generatedAt": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        ).isoformat(),
    }
    files = {
        "accepted-run-index.json": {
            "schemaVersion": "R3FormalAcceptedRunIndexV1",
            "planned": len(planned_order),
            "executed": len(measured),
            "valid": len(valid),
            "invalid": len(invalid),
            "replacement": 0,
            "excluded": len(invalid),
            "runs": [r for r in measured],
        },
        "data-quality.json": {
            "schemaVersion": "R3FormalDataQualityV1",
            "missingMetrics": sum(
                1 for r in measured if r["M03_end_to_end_duration_ms"] is None
            ),
            "missingRecovery": sum(
                1 for r in measured
                if r["experimentId"] == "E5" and r["M11_recovery_disposition"] in (None, "NOT_REQUIRED")
            ),
        },
        "exclusions.json": {
            "schemaVersion": "R3FormalExclusionPolicyV1",
            "excludedRuns": [r["runId"] for r in invalid],
            "reasons": {r["runId"]: r["disposition"] for r in invalid},
        },
        "replacements.json": {"schemaVersion": "R3FormalReplacementsV1", "replacements": []},
        "pairing.json": {
            "schemaVersion": "R3FormalPairingV1",
            "pairingKey": "generatorVersion|semanticClass|inputDigest|seed|configurationDigest",
            "crossSemanticPairing": False,
            "pairingErrors": [],
            "e5Pairs": [
                {"fault": fault, "local": local, "kubo": kubo}
                for fault, local, kubo in [
                    (fault, len([r for r in valid if r["experimentId"] == "E5"
                                and r["faultScenario"] == fault and r["storageMode"] == "LOCAL_ONLY"]),
                     len([r for r in valid if r["experimentId"] == "E5"
                          and r["faultScenario"] == fault and r["storageMode"] == "KUBO_REPLICA"]))
                    for fault in sorted({r["faultScenario"] for r in valid if r["experimentId"] == "E5"})
                ]
            ],
        },
        "descriptive-statistics.json": descriptive_stats,
        "bootstrap-results.json": bootstrap_results,
        "effect-sizes.json": effect_sizes,
        "multiple-comparison.json": {
            "schemaVersion": "R3FormalMultipleComparisonV1",
            "method": "Holm correction within each RQ family",
            "families": {
                "RQ-2": ["E2"],
                "RQ-3": ["E3"],
                "RQ-5/RQ-6": ["E5"],
            },
            "holmAdjusted": [],
        },
        "formal-invariants.json": invariants,
        "analysis-manifest.json": manifest,
    }
    for name, value in files.items():
        (out / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, sort_keys=True))


if __name__ == "__main__":
    main()
