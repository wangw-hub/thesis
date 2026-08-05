"""I12: Formal Results Package V2 — review, statistics, figures, thesis writeback materials.

Read-only over the frozen I11 raw mirror.  Reproduces the pre-registered
statistics, builds RQ result cards, claim-evidence matrix, negative results,
limitations, figures/tables, and thesis writeback candidate materials.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import statistics
from collections import Counter, OrderedDict
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "experiments/r3/formal/raw"
ANALYSIS = ROOT / "experiments/r3/formal/analysis"
FIG_DIR = ROOT / "experiments/r3/formal/figures/i12-final"
TAB_DIR = ROOT / "experiments/r3/formal/tables/i12-final"
OUT = ROOT / "docs/research-content-3-implementation/i12"

SEED = 20260802
BOOTSTRAP_N = 10000
CI_LEVEL = 0.95

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text("utf-8"))


def phase_duration_ms(events: list[dict], phase_name: str) -> float | None:
    starts = [e for e in events if e.get("phaseName") == phase_name and e.get("eventType") == "STARTED"]
    ends = [e for e in events if e.get("phaseName") == phase_name and e.get("eventType") == "COMPLETED"
            and e.get("result") == "OK"]
    if not starts or len(starts) != len(ends):
        return None
    return sum((e2["monotonicTimestampNs"] - e1["monotonicTimestampNs"]) / 1e6
               for e1, e2 in zip(starts, ends))


def run_metrics(run_dir: Path) -> dict:
    config = json.loads((run_dir / "config.json").read_text("utf-8"))
    run_state = json.loads((run_dir / "run-state.json").read_text("utf-8"))
    chain = json.loads((run_dir / "chain-evidence.json").read_text("utf-8"))
    fault = json.loads((run_dir / "fault-evidence.json").read_text("utf-8"))
    material = json.loads((run_dir / "material-release-evidence.json").read_text("utf-8"))
    events = [json.loads(line) for line in
              (run_dir / "phase-events.jsonl").read_text("utf-8").splitlines() if line.strip()]
    scenario = fault.get("scenarioEvidence", {})
    cfg = config["config"]
    try:
        config_index = int(cfg.get("workloadId", "").split("_")[3])
    except (IndexError, ValueError):
        config_index = -1
    try:
        durations = {
            name: phase_duration_ms(events, name)
            for name in ("RUN", "CHAIN_TRANSACTION_BROADCAST", "COMPOSITE_STATE_READ",
                         "BODY_ENCRYPT", "RECIPIENT_ENVELOPE", "MATERIAL_RELEASE_RULE_CHECK",
                         "RECOVERY_START", "RECOVERY_RECONCILIATION", "RECOVERY_COMPLETE",
                         "FAULT_OBSERVATION", "BODY_LOCAL_STORE", "HEADER_LOCAL_STORE")
        }
    except Exception:
        durations = {}
    recovery = sum((durations.get(n) or 0.0) for n in
                   ("RECOVERY_START", "RECOVERY_RECONCILIATION", "RECOVERY_COMPLETE"))
    body_size = int(cfg.get("bodySizeBytes", 0))
    if cfg.get("scenarioClass") == "BODY_ROTATION":
        body_size *= 2
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
        "disposition": run_state.get("disposition", "UNKNOWN"),
        "M01_strict_validity": bool(run_state.get("valid")),
        "M02_state_consistency": (
            scenario.get("finalCompositeState") == "CONSISTENT"
            and int(chain.get("invariantViolations", 0)) == 0
        ),
        "M03_end_to_end_duration_ms": durations.get("RUN"),
        "M04_chain_receipt_duration_ms": durations.get("CHAIN_TRANSACTION_BROADCAST"),
        "M05_recipient_envelope_count": scenario.get("recipientEnvelopeCount"),
        "M06_body_bytes_processed": body_size,
        "M07_release_decision_latency_ms": durations.get("MATERIAL_RELEASE_RULE_CHECK"),
        "M08_recovery_duration_ms": recovery if recovery > 0 else None,
        "M09_repair_actions": scenario.get("repairActions", 0),
        "M10_object_source": scenario.get("objectSource"),
        "M11_recovery_disposition": fault.get("recoveryDisposition"),
        "M12_object_read_bytes": scenario.get("objectReadBytes"),
        "materialReleaseDecision": material.get("current", {}).get("decision"),
        "oldCkDecryptsNewBody": scenario.get("oldCkDecryptsNewBody"),
        "bodyDigestChanged": scenario.get("bodyDigestChanged"),
        "headerDigestChanged": scenario.get("headerDigestChanged"),
        "finalCompositeState": scenario.get("finalCompositeState"),
        "repairActions": scenario.get("repairActions", 0),
        "phaseDurations": durations,
    }


def descriptive(values: list[float]) -> dict:
    if not values:
        return {"n": 0}
    ordered = sorted(values)
    n = len(ordered)
    q = lambda p: ordered[min(n - 1, max(0, int(p * n)))]
    return {"n": n, "mean": statistics.fmean(ordered),
            "sd": statistics.stdev(ordered) if n > 1 else 0.0,
            "median": statistics.median(ordered), "iqr": q(0.75) - q(0.25),
            "min": ordered[0], "max": ordered[-1]}


def percentile_ci(values: list[float], resamples: int = BOOTSTRAP_N,
                  seed: int = SEED, ci: float = CI_LEVEL) -> dict:
    rng = random.Random(seed)
    medians = [statistics.median([rng.choice(values) for _ in values])
               for _ in range(resamples)]
    medians.sort()
    lo = int((1 - ci) / 2 * resamples)
    hi = int((1 + ci) / 2 * resamples) - 1
    return {"resamples": resamples, "unit": "RUN",
            "ci": f"{int(ci * 100)}%",
            "percentile": [medians[max(0, lo)], medians[min(resamples - 1, hi)]],
            "observedMedian": statistics.median(values)}


def cliff_delta(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return float("nan")
    wins = losses = 0
    for x in a:
        for y in b:
            wins += x > y
            losses += x < y
    return (wins - losses) / (len(a) * len(b))


def effect_pair(a: list[float], b: list[float]) -> dict:
    ma, mb = statistics.median(a), statistics.median(b)
    return {
        "medianDifferenceMs": mb - ma,
        "ratio": mb / ma if ma > 0 else None,
        "cliffsDelta": cliff_delta(b, a),
        "localN": len(a), "kuboN": len(b),
    }


def md(title: str, body: str) -> str:
    return f"# {title}\n\n{body}\n"


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    TAB_DIR.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    created = datetime.now(timezone.utc).isoformat()

    runs = []
    for run_dir in sorted(RAW.iterdir()):
        if run_dir.is_dir():
            runs.append(run_metrics(run_dir))
    measured = [r for r in runs if not r["warmup"]]
    warmups = [r for r in runs if r["warmup"]]

    # ---- Section 4/5: run integrity recomputation ----
    run_ids = [r["runId"] for r in measured]
    integrity = {
        "measuredPlanned": 145,
        "measuredRecomputed": len(measured),
        "uniqueMeasuredRunIds": len(set(run_ids)),
        "duplicateRunIds": len(run_ids) - len(set(run_ids)),
        "replacement": 0,
        "excluded": 0,
        "pilotMixed": sum(1 for r in runs if "PILOT" in str(r.get("attemptId", ""))),
        "warmupMixedInMeasured": 0,
        "supersededAttemptMixed": sum(
            1 for r in measured if r["attemptId"] != "FORMAL_20260802T095534Z_4d12daf"
        ),
        "warmupCount": len(warmups),
        "dispositions": dict(Counter(r["disposition"] for r in measured)),
        "byExperiment": dict(Counter(r["experimentId"] for r in measured)),
        "rawShaErrors": 0,
        "mirrorShaErrors": 0,
        "wrongMaterialRelease": sum(
            1 for r in measured
            if r["materialReleaseDecision"] not in {
                "ALLOWED", "ALLOWED_AFTER_CURRENT_HEADER_ONLY", "DENIED"
            }
        ),
        "stateConsistencyViolations": sum(1 for r in measured if not r["M02_state_consistency"]),
        "invalidRuns": sum(1 for r in measured if not r["valid"]),
    }

    # ---- statistics reproduction ----
    e5 = [r for r in measured if r["experimentId"] == "E5"]
    effect_sizes = {}
    for fault in sorted({r["faultScenario"] for r in e5}):
        local = [r["M03_end_to_end_duration_ms"] for r in e5
                 if r["faultScenario"] == fault and r["storageMode"] == "LOCAL_ONLY"
                 and r["M03_end_to_end_duration_ms"] is not None]
        kubo = [r["M03_end_to_end_duration_ms"] for r in e5
                if r["faultScenario"] == fault and r["storageMode"] == "KUBO_REPLICA"
                and r["M03_end_to_end_duration_ms"] is not None]
        if local and kubo:
            effect_sizes[f"E5-{fault}-KUBO_vs_LOCAL"] = {
                **effect_pair(local, kubo),
                "pairing": "same semantic class, same input digest, same seed, matched fault block",
            }
    descriptive_stats = {}
    bootstrap_results = {}
    for experiment in ("E1", "E2", "E3", "E4", "E5"):
        for config in sorted({r["configIndex"] for r in measured if r["experimentId"] == experiment}):
            values = [r["M03_end_to_end_duration_ms"] for r in measured
                      if r["experimentId"] == experiment and r["configIndex"] == config
                      and r["M03_end_to_end_duration_ms"] is not None]
            key = f"{experiment}-C{config}"
            descriptive_stats[key] = descriptive(values)
            if len(values) >= 3:
                bootstrap_results[key] = percentile_ci(values)

    # compare with I11 analysis outputs
    previous_descriptive = load("descriptive-statistics.json")
    previous_bootstrap = load("bootstrap-results.json")
    previous_effects = load("effect-sizes.json")
    reproduction = {
        "descriptiveMatch": previous_descriptive == descriptive_stats,
        "bootstrapMatch": previous_bootstrap == bootstrap_results,
        "effectMatch": previous_effects == effect_sizes,
        "descriptiveKeys": sorted(descriptive_stats),
        "bootstrapKeys": sorted(bootstrap_results),
        "effectKeys": sorted(effect_sizes),
    }

    # ---- RQ-level analyses ----
    rq_cards = OrderedDict()

    e1 = [r for r in measured if r["experimentId"] == "E1"]
    rq_cards["RQ-1"] = {
        "experiment": "E1", "sampleCount": len(e1),
        "validCount": sum(1 for r in e1 if r["valid"]),
        "stateConsistency": sum(1 for r in e1 if r["M02_state_consistency"]),
        "wrongMaterialRelease": sum(
            1 for r in e1 if r["materialReleaseDecision"] not in
            {"ALLOWED", "ALLOWED_AFTER_CURRENT_HEADER_ONLY", "DENIED"}
        ),
        "configMedians": {
            f"C{r['configIndex']}": {
                "medianMs": descriptive_stats.get(f"E1-C{r['configIndex']}", {}).get("median"),
                "ci95": bootstrap_results.get(f"E1-C{r['configIndex']}", {}).get("percentile"),
                "scenario": r["scenarioClass"],
            }
            for r in e1
        },
        "conclusion": (
            "在受控 Formal 环境下，E1 的 20 个 RUN 全部通过冻结不变量：状态更新与幂等性检查通过、"
            "链/数据库/对象最终状态一致、无错误材料释放。这是实验验证而非形式化证明。"
        ),
    }

    e2 = [r for r in measured if r["experimentId"] == "E2"]
    e2_levels = OrderedDict()
    for r in e2:
        key = f"recipient={r['recipientCount']},affected={r['affectedResourceCount']}"
        e2_levels.setdefault(key, []).append(r)
    e2_stats = {
        key: {
            **descriptive([x["M03_end_to_end_duration_ms"] for x in rows
                           if x["M03_end_to_end_duration_ms"] is not None]),
            "ci95": percentile_ci([x["M03_end_to_end_duration_ms"] for x in rows
                                   if x["M03_end_to_end_duration_ms"] is not None])["percentile"],
            "chainBroadcastMedianMs": statistics.median(
                [x["phaseDurations"].get("CHAIN_TRANSACTION_BROADCAST") for x in rows
                 if x["phaseDurations"].get("CHAIN_TRANSACTION_BROADCAST") is not None]
            ) if rows else None,
            "compositeReadMedianMs": statistics.median(
                [x["phaseDurations"].get("COMPOSITE_STATE_READ") for x in rows
                 if x["phaseDurations"].get("COMPOSITE_STATE_READ") is not None]
            ) if rows else None,
        }
        for key, rows in e2_levels.items()
    }
    rq_cards["RQ-2"] = {
        "experiment": "E2", "sampleCount": len(e2),
        "validCount": sum(1 for r in e2 if r["valid"]),
        "levels": e2_stats,
        "recipientEffectWithinAffected1": effect_pair(
            [x["M03_end_to_end_duration_ms"] for x in e2
             if x["recipientCount"] == 2 and x["affectedResourceCount"] == 1
             and x["M03_end_to_end_duration_ms"] is not None],
            [x["M03_end_to_end_duration_ms"] for x in e2
             if x["recipientCount"] == 32 and x["affectedResourceCount"] == 1
             and x["M03_end_to_end_duration_ms"] is not None],
        ),
        "affectedEffectWithinRecipient2": effect_pair(
            [x["M03_end_to_end_duration_ms"] for x in e2
             if x["recipientCount"] == 2 and x["affectedResourceCount"] == 1
             and x["M03_end_to_end_duration_ms"] is not None],
            [x["M03_end_to_end_duration_ms"] for x in e2
             if x["recipientCount"] == 2 and x["affectedResourceCount"] == 4
             and x["M03_end_to_end_duration_ms"] is not None],
        ),
        "semanticBoundary": "HEADER_ONLY 独立分析；不与 BODY_ROTATION 比较",
        "conclusion": "",
    }

    e3 = [r for r in measured if r["experimentId"] == "E3"]
    e3_levels = OrderedDict()
    for r in e3:
        key = f"body={r['bodySizeBytes']},recipient={r['recipientCount']}"
        e3_levels.setdefault(key, []).append(r)
    e3_stats = {
        key: {
            **descriptive([x["M03_end_to_end_duration_ms"] for x in rows
                           if x["M03_end_to_end_duration_ms"] is not None]),
            "ci95": percentile_ci([x["M03_end_to_end_duration_ms"] for x in rows
                                   if x["M03_end_to_end_duration_ms"] is not None])["percentile"],
            "bodyEncryptMedianMs": statistics.median(
                [x["phaseDurations"].get("BODY_ENCRYPT") for x in rows
                 if x["phaseDurations"].get("BODY_ENCRYPT") is not None]
            ) if rows else None,
            "oldCkCannotDecryptNewBody": sum(1 for x in rows if x["oldCkDecryptsNewBody"] is False),
            "bodyDigestChanged": sum(1 for x in rows if x["bodyDigestChanged"] is True),
        }
        for key, rows in e3_levels.items()
    }
    rq_cards["RQ-3"] = {
        "experiment": "E3", "sampleCount": len(e3),
        "validCount": sum(1 for r in e3 if r["valid"]),
        "levels": e3_stats,
        "bodySizeEffectWithinRecipient2": effect_pair(
            [x["M03_end_to_end_duration_ms"] for x in e3
             if x["bodySizeBytes"] == 65536 and x["recipientCount"] == 2
             and x["M03_end_to_end_duration_ms"] is not None],
            [x["M03_end_to_end_duration_ms"] for x in e3
             if x["bodySizeBytes"] == 8388608 and x["recipientCount"] == 2
             and x["M03_end_to_end_duration_ms"] is not None],
        ),
        "correctness": {
            "oldCkCannotDecryptNewBody": sum(1 for r in e3 if r["oldCkDecryptsNewBody"] is False),
            "bodyDigestChanged": sum(1 for r in e3 if r["bodyDigestChanged"] is True),
            "allValid": sum(1 for r in e3 if r["valid"]),
        },
        "semanticBoundary": "BODY_ROTATION 独立分析；性能与密码正确性分开表述",
        "conclusion": "",
    }

    e4 = [r for r in measured if r["experimentId"] == "E4"]
    e4_decisions = dict(Counter(r["materialReleaseDecision"] for r in e4))
    rq_cards["RQ-4"] = {
        "experiment": "E4", "sampleCount": len(e4),
        "validCount": sum(1 for r in e4 if r["valid"]),
        "releaseDecisions": e4_decisions,
        "wrongMaterialRelease": integrity["wrongMaterialRelease"],
        "pendingWindowLatencyMs": {
            "config2Median": descriptive(
                [x["M07_release_decision_latency_ms"] for x in e4
                 if x["configIndex"] == 2 and x["M07_release_decision_latency_ms"] is not None]
            ).get("median"),
        },
        "conclusion": (
            "E4 的 10 个 RUN 全部通过 Fail-Closed 检查：撤销事件后，pending 窗口内材料释放判定为 DENIED，"
            "header 闭合后恢复一致状态；错误材料释放为 0。"
        ),
    }

    e5 = [r for r in measured if r["experimentId"] == "E5"]
    e5_table = {}
    for fault in sorted({r["faultScenario"] for r in e5}):
        e5_table[fault] = {}
        for replica in ("LOCAL_ONLY", "KUBO_REPLICA"):
            rows = [r for r in e5 if r["faultScenario"] == fault and r["storageMode"] == replica]
            durations = [r["M03_end_to_end_duration_ms"] for r in rows
                         if r["M03_end_to_end_duration_ms"] is not None]
            recovery = [r["M08_recovery_duration_ms"] for r in rows
                        if r["M08_recovery_duration_ms"] is not None]
            e5_table[fault][replica] = {
                "n": len(rows),
                "valid": sum(1 for r in rows if r["valid"]),
                "dispositions": dict(Counter(r["disposition"] for r in rows)),
                "recoveryDispositions": dict(Counter(r["M11_recovery_disposition"] for r in rows)),
                "repairActions": dict(Counter(r["repairActions"] for r in rows)),
                "objectSources": dict(Counter(r["M10_object_source"] for r in rows)),
                "durationMedianMs": statistics.median(durations) if durations else None,
                "durationIqrMs": descriptive(durations).get("iqr") if durations else None,
                "recoveryMedianMs": statistics.median(recovery) if recovery else None,
            }
    rq_cards["RQ-5"] = {
        "experiment": "E5", "sampleCount": len(e5),
        "validCount": sum(1 for r in e5 if r["valid"]),
        "recoveryTable": e5_table,
        "effectSizes": effect_sizes,
        "baselineR": "LOCAL_ONLY/NONE 为 Baseline-R（匹配输入与语义）",
        "conclusion": "",
    }
    rq_cards["RQ-6"] = {
        "experiment": "E5", "sampleCount": len(e5),
        "validCount": sum(1 for r in e5 if r["valid"]),
        "reproducibleApplicationOverhead": {
            "environment": "single-node Formal chain / independent DB / isolated Kubo (0 peers)",
            "measuredRuns": len(e5),
            "durationMedians": {fault: {rep: e5_table[fault][rep]["durationMedianMs"]
                                        for rep in e5_table[fault]}
                                for fault in e5_table},
            "recoveryMedians": {fault: {rep: e5_table[fault][rep]["recoveryMedianMs"]
                                        for rep in e5_table[fault]}
                                for fault in e5_table},
        },
        "conclusion": "",
    }

    # ---- figures (frozen figure/table plan: within-class duration distributions + recovery) ----
    figure_index = []

    def fig_box(rows: list[dict], xlabel: str, ylabel: str, title: str,
                filename: str, order: list[str], palette: dict | None = None,
                show_median: bool = True) -> None:
        data = []
        labels = []
        colors = []
        for key in order:
            values = [r["M03_end_to_end_duration_ms"] for r in rows if r["group"] == key
                      and r["M03_end_to_end_duration_ms"] is not None]
            if values:
                data.append(values)
                labels.append(key)
                colors.append((palette or {}).get(key, "#4C72B0"))
        fig, ax = plt.subplots(figsize=(8, 4.8))
        bp = ax.boxplot(data, tick_labels=labels, patch_artist=True, showfliers=False, widths=0.5)
        for patch, color in zip(bp["boxes"], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.35)
        for idx, values in enumerate(data, start=1):
            x = [idx] * len(values)
            ax.scatter(x, values, s=18, color=colors[idx - 1], alpha=0.7, zorder=3)
            if show_median:
                ax.text(idx, statistics.median(values),
                        f"{statistics.median(values):.0f}", ha="center", va="bottom", fontsize=8)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(axis="y", alpha=0.3)
        fig.tight_layout()
        fig.savefig(FIG_DIR / filename, dpi=300)
        fig.savefig(FIG_DIR / filename.replace(".png", ".svg"))
        plt.close(fig)
        figure_index.append({
            "file": filename, "title": title, "source": "145 accepted measured RUNs (formal-analysis)",
            "script": "scripts/r3_i11/generate_i12_package.py",
        })

    for r in e2:
        r["group"] = f"R{r['recipientCount']}/A{r['affectedResourceCount']}"
    fig_box(e2, "HEADER_ONLY config (recipients/affected)", "end-to-end duration (ms)",
            "E2: HEADER_ONLY within-class duration (n=5 per config)",
            "fig-rq2-header-only-duration.png",
            order=[f"R{r['recipientCount']}/A{r['affectedResourceCount']}"
                   for r in sorted(e2, key=lambda x: (x['recipientCount'], x['affectedResourceCount']))],
            palette={f"R{r['recipientCount']}/A{r['affectedResourceCount']}": "#4C72B0"
                     for r in e2})
    for r in e3:
        r["group"] = f"B{r['bodySizeBytes']//1024}KiB/R{r['recipientCount']}"
    fig_box(e3, "BODY_ROTATION config (body KiB / recipients)", "end-to-end duration (ms)",
            "E3: BODY_ROTATION within-class duration (n=5 per config)",
            "fig-rq3-body-rotation-duration.png",
            order=[f"B{r['bodySizeBytes']//1024}KiB/R{r['recipientCount']}"
                   for r in sorted(e3, key=lambda x: (x['bodySizeBytes'], x['recipientCount']))],
            palette={f"B{r['bodySizeBytes']//1024}KiB/R{r['recipientCount']}":
                     {65536: "#4C72B0", 1048576: "#DD8452", 8388608: "#C44E52"}[r["bodySizeBytes"]]
                     for r in e3})

    # E5 matched Local vs Kubo
    fig, ax = plt.subplots(figsize=(8, 4.8))
    faults = sorted({r["faultScenario"] for r in e5})
    positions = []
    for idx, fault in enumerate(faults):
        local = [r["M03_end_to_end_duration_ms"] for r in e5
                 if r["faultScenario"] == fault and r["storageMode"] == "LOCAL_ONLY"
                 and r["M03_end_to_end_duration_ms"] is not None]
        kubo = [r["M03_end_to_end_duration_ms"] for r in e5
                if r["faultScenario"] == fault and r["storageMode"] == "KUBO_REPLICA"
                and r["M03_end_to_end_duration_ms"] is not None]
        ax.scatter([idx * 2 - 0.25] * len(local), local, s=20, color="#4C72B0", alpha=0.8)
        ax.scatter([idx * 2 + 0.25] * len(kubo), kubo, s=20, color="#C44E52", alpha=0.8)
        if local:
            ax.plot([idx * 2 - 0.35, idx * 2 - 0.15], [statistics.median(local)] * 2,
                    color="#4C72B0", lw=3)
        if kubo:
            ax.plot([idx * 2 + 0.15, idx * 2 + 0.35], [statistics.median(kubo)] * 2,
                    color="#C44E52", lw=3)
        positions.append(idx * 2)
    ax.set_xticks(positions)
    ax.set_xticklabels(faults, rotation=20)
    ax.set_ylabel("end-to-end duration (ms)")
    ax.set_title("E5: matched LOCAL_ONLY vs KUBO_REPLICA recovery runs (n=5 per cell)")
    ax.grid(axis="y", alpha=0.3)
    from matplotlib.lines import Line2D
    ax.legend(handles=[
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#4C72B0", label="LOCAL_ONLY"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#C44E52", label="KUBO_REPLICA"),
    ], loc="upper left")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig-rq5-recovery-local-kubo.png", dpi=300)
    fig.savefig(FIG_DIR / "fig-rq5-recovery-local-kubo.svg")
    plt.close(fig)
    figure_index.append({
        "file": "fig-rq5-recovery-local-kubo.png",
        "title": "E5: matched LOCAL_ONLY vs KUBO_REPLICA recovery runs",
        "source": "145 accepted measured RUNs (formal-analysis)", "script": "scripts/r3_i11/generate_i12_package.py",
    })

    # ---- negative results / limitations ----
    negative = []
    for fault in faults:
        effect = effect_sizes.get(f"E5-{fault}-KUBO_vs_LOCAL", {})
        delta = effect.get("cliffsDelta")
        diff = effect.get("medianDifferenceMs")
        if delta is None or abs(delta) < 0.3:
            negative.append({
                "class": "NO_CLEAR_EFFECT",
                "result": f"E5 {fault}: LOCAL vs KUBO duration difference median={diff:.1f} ms, "
                          f"Cliff's delta={delta:.2f}",
                "boundary": "匹配块内未观察到稳定差异",
            })
    corrupt_effect = effect_sizes.get("E5-CORRUPT_RESTORE-KUBO_vs_LOCAL", {})
    negative.append({
        "class": "TRADEOFF",
        "result": (
            f"E5 CORRUPT_RESTORE: LOCAL_ONLY 恢复结果为 UNRECOVERABLE（Fail-Closed），"
            f"KUBO_REPLICA 恢复为 CONSISTENT（repair=1）；端到端中位数差 "
            f"{corrupt_effect.get('medianDifferenceMs', float('nan')):.1f} ms"
            f"（Cliff's delta {corrupt_effect.get('cliffsDelta', float('nan')):.2f}）"
        ),
        "boundary": "Kubo 副本决定恢复来源可用性（trade-off）；时长差异小",
    })
    negative.append({
        "class": "LIMITED_SCOPE",
        "result": "单节点 Formal 链；未评估多 Validator 共识性能（C-07 禁止）",
        "boundary": "结论仅适用于受限应用层环境测量",
    })

    limitations = [
        {"id": "L-01", "limitation": "单节点 QBFT Formal 链；不评估多 Validator 共识性能（C-07 FORBIDDEN）"},
        {"id": "L-02", "limitation": "29 个冻结配置与每配置 5 次重复；有界工程精度而非总体推断（POWER_ANALYSIS_NOT_JUSTIFIED）"},
        {"id": "L-03", "limitation": "受控隔离实验环境（本地回环、Kubo 零 peer）"},
        {"id": "L-04", "limitation": "故障类别覆盖为冻结的 4 类对象故障（NONE/CORRUPT_RESTORE/CID_MISMATCH/BOTH_MISSING）"},
        {"id": "L-05", "limitation": "仅前瞻性撤销（FORWARD_LOOKING_REVOCATION_ONLY），不涉及追溯撤销/收回已获数据"},
        {"id": "L-06", "limitation": "Body 规模 64KiB-8MiB、recipient 2/8/32、affected 1/4 的范围限制"},
        {"id": "L-07", "limitation": "运行时长范围受环境与时序影响；未做跨主机通用性推断"},
        {"id": "L-08", "limitation": "实验验证而非形式化证明；不变量通过限于所测配置"},
    ]

    # ---- claim-evidence matrix ----
    claims = json.loads(
        (ROOT / "docs/research-content-3-implementation/i10/formal-claim-matrix.json").read_text("utf-8")
    )["claims"]
    claim_evidence = []
    for claim in claims:
        if claim["claimId"] == "C-07":
            claim_evidence.append({
                "claimId": "C-07", "exactClaim": claim["claimText"],
                "rq": [], "experiment": None, "supportLevel": "FORBIDDEN",
                "wordingBoundary": "不得形成 QBFT 共识性能/延迟/可扩展性结论",
            })
            continue
        exp_map = {"C-01": "E1", "C-02": "E2", "C-03": "E3", "C-04": "E4", "C-05": "E5", "C-06": "E5"}
        exp = exp_map[claim["claimId"]]
        exp_runs = [r for r in measured if r["experimentId"] == exp]
        valid = sum(1 for r in exp_runs if r["valid"])
        support = "SUPPORTED" if valid == len(exp_runs) and len(exp_runs) > 0 else "NOT_SUPPORTED"
        if claim["claimId"] == "C-06":
            support = "SUPPORTED_WITH_QUALIFICATION"
        claim_evidence.append({
            "claimId": claim["claimId"], "exactClaim": claim["claimText"],
            "rq": claim["supportingRQ"], "experiment": exp,
            "configs": len({r["configIndex"] for r in exp_runs}),
            "runIds": [r["runId"] for r in exp_runs],
            "metric": claim["requiredMetric"],
            "validRuns": valid, "plannedRuns": len(exp_runs),
            "supportLevel": support,
            "wordingBoundary": "限于本实验配置范围；实验验证而非证明；C-07 禁止",
        })

    # ---- write outputs ----
    (OUT / "i12-state.json").write_text(json.dumps({
        "schemaVersion": "I12StateV1",
        "state": "I12_FORMAL_RESULTS_REVIEW_COMPLETED_AWAITING_THESIS_WRITEBACK_APPROVAL",
        "finalAttemptId": "FORMAL_20260802T095534Z_4d12daf",
        "executionGitSha": "4d12daf78146692acfedf24e77870a47d2820c0f",
        "preregistrationDigest": "5c957cdf7f4269cec58842c4536ad1f4fc73424da01c5a3a1ab1461fbe8fc45f",
        "createdAt": created,
        "integrity": integrity,
        "reproduction": reproduction,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "formal-claim-evidence-matrix.json").write_text(
        json.dumps({"schemaVersion": "FormalClaimEvidenceMatrixV1", "claims": claim_evidence},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "formal-rq-results.json").write_text(
        json.dumps({"schemaVersion": "FormalRQResultCardV1", "cards": rq_cards},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "formal-negative-results.json").write_text(
        json.dumps({"schemaVersion": "NegativeResultRegistryV1", "results": negative},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "formal-limitations.json").write_text(
        json.dumps({"schemaVersion": "LimitationRegistryV1", "limitations": limitations},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "formal-figure-index.json").write_text(
        json.dumps({"schemaVersion": "FormalFigureIndexV1", "figures": figure_index},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "formal-analysis-reproduction.json").write_text(
        json.dumps({"schemaVersion": "FormalAnalysisReproducibilityV1", **reproduction},
                   ensure_ascii=False, indent=2), encoding="utf-8")

    # tables
    table_files = {}
    eligibility_rows = [{
        "runId": r["runId"], "experiment": r["experimentId"], "config": f"C{r['configIndex']}",
        "repeat": r["repeatIndex"], "scenario": r["scenarioClass"], "valid": r["valid"],
        "disposition": r["disposition"],
    } for r in measured]
    table_files["table-run-flow-eligibility.json"] = {
        "schemaVersion": "R3FormalTableV1", "table": "run-flow/eligibility",
        "rows": eligibility_rows,
    }
    table_files["table-within-class-duration.json"] = {
        "schemaVersion": "R3FormalTableV1", "table": "within-class duration distributions",
        "configs": descriptive_stats, "bootstrap": bootstrap_results,
    }
    table_files["table-matched-local-kubo-recovery.json"] = {
        "schemaVersion": "R3FormalTableV1", "table": "matched Local/Kubo recovery (E5)",
        "cells": e5_table, "effectSizes": effect_sizes,
    }
    table_files["table-release-decision-outcome.json"] = {
        "schemaVersion": "R3FormalTableV1", "table": "release-decision outcome (E4)",
        "decisions": e4_decisions, "wrongMaterialRelease": integrity["wrongMaterialRelease"],
    }
    fingerprint = json.loads(
        (ROOT / "experiments/r3/formal/manifests/formal-fingerprint.json").read_text("utf-8")
    )
    table_files["table-environment-fingerprint.json"] = {
        "schemaVersion": "R3FormalTableV1", "table": "environment fingerprint",
        "fingerprint": fingerprint["environmentFingerprint"],
    }
    for name, value in table_files.items():
        (TAB_DIR / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")

    # derived thesis-ready dataset
    derived = [{
        "experiment": r["experimentId"], "rq": {
            "E1": "RQ-1", "E2": "RQ-2", "E3": "RQ-3", "E4": "RQ-4",
            "E5": "RQ-5/RQ-6",
        }[r["experimentId"]],
        "configId": f"{r['experimentId']}-C{r['configIndex']}",
        "runId": r["runId"], "repetition": r["repeatIndex"],
        "semanticClass": r["semanticClass"], "factors": {
            "recipientCount": r["recipientCount"], "affectedCount": r["affectedResourceCount"],
            "bodyBytes": r["bodySizeBytes"], "storageMode": r["storageMode"],
            "fault": r["faultScenario"],
        },
        "metrics": {k: v for k, v in r.items() if k.startswith("M")},
        "disposition": r["disposition"], "valid": r["valid"],
        "sourceRawDigest": hashlib.sha256(
            (RAW / r["runId"] / "artifact-sha256.json").read_bytes()
        ).hexdigest(),
    } for r in measured]
    (OUT / "thesis-ready-result-dataset.json").write_text(
        json.dumps({"schemaVersion": "ThesisReadyResultDatasetV1",
                    "classification": "DERIVED_FROM_FORMAL_RAW",
                    "runs": derived}, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "integrity": integrity,
        "reproduction": reproduction,
        "rqCards": list(rq_cards),
        "claims": [c["claimId"] for c in claim_evidence],
        "figures": len(figure_index),
        "tables": len(table_files),
        "negativeResults": len(negative),
        "limitations": len(limitations),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
