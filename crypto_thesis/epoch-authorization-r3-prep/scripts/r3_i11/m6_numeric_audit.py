# -*- coding: utf-8 -*-
"""M6: numeric consistency audit against frozen data sources."""
from __future__ import annotations

import io
import json
import re
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
SRC = ROOT / "docs/midterm-report/m6/M6-MIDTERM-SOURCE.md"
RC3_DESC = ROOT / "experiments/r3/formal/analysis/descriptive-statistics.json"
RC3_BOOT = ROOT / "experiments/r3/formal/analysis/bootstrap-results.json"
MATRIX = ROOT / "docs/research-content-3-implementation/i11/formal-config-matrix.json"
RC2_LAT = Path(r"D:\Research\crypto_thesis\epoch-authorization\docs\thesis-drafts\research-content-2-final\figure-sources\figure-5-2-run-latency.csv")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    t = io.open(SRC, encoding="utf-8").read()
    out = {"source_numbers": {}, "frozen_data": {}}

    # --- RC3 frozen values ---
    desc = json.loads(RC3_DESC.read_text(encoding="utf-8"))
    boot = json.loads(RC3_BOOT.read_text(encoding="utf-8"))
    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))["measured"]
    from collections import Counter
    exp_counts = Counter(c["experimentId"] for c in matrix)
    out["frozen_data"]["rc3"] = {
        "config_count": len(matrix),
        "per_experiment_configs": dict(exp_counts),
        "E1_medians": {k: desc[k]["median"] for k in ["E1-C1", "E1-C2", "E1-C3", "E1-C4"]},
        "E2_medians": {k: desc[k]["median"] for k in sorted(desc) if k.startswith("E2")},
        "E3_medians": {k: desc[k]["median"] for k in sorted(desc) if k.startswith("E3")},
        "E5_medians": {k: desc[k]["median"] for k in ["E5-C1", "E5-C2", "E5-C3", "E5-C4"]},
    }
    print("RC3 configs:", len(matrix))
    print("per-experiment configs:", dict(exp_counts))
    print("E1 medians:", {k: round(desc[k]["median"]) for k in ["E1-C1", "E1-C2", "E1-C3", "E1-C4"]})
    print("E5 medians:", {k: round(desc[k]["median"]) for k in ["E5-C1", "E5-C2", "E5-C3", "E5-C4"]})

    # --- RC2 frozen values ---
    lat = pd.read_csv(RC2_LAT)
    med = lat.groupby("method")["median_end_to_end_ms"].median()
    out["frozen_data"]["rc2_median_end_to_end"] = med.round(3).to_dict()
    print("RC2 method median of medians:", med.round(3).to_dict())

    # --- source text number extraction ---
    checks = {
        "168 个样本": "168",
        "15120": "15120",
        "81 项测试": "81",
        "98.61%": "98.61%",
        "29 个配置": "29",
        "35 次预热运行": "35",
        "145 个有效运行": "145",
        "9720": "9720",
        "77760": "77760",
        "233280": "233280",
        "2430": "2430",
        "10000 次": "10000",
        "98.66%": "98.66%",
        "98.80%": "98.80%",
        "350.4": "350.4",
        "561.0": "561.0",
        "1984.7": "1984.7",
        "24000": "24000",
        "2808": "2808",
        "3664": "3664",
        "3080": "3080",
        "5120": "5120",
        "7118": "7118",
        "3147": "3147",
        "5115": "5115",
        "5144": "5144",
        "5083": "5083",
        "6696": "6696",
        "3112.2": "3112.2",
        "3129.6": "3129.6",
        "196.128": "196.128",
        "198.601": "198.601",
        "17.926": "17.926",
        "0.390": "0.390",
        "0.176": "0.176",
    }
    missing = [k for k in checks if k not in t]
    out["source_numbers"] = {"checked": len(checks), "missing_in_source": missing}
    print("source numbers checked:", len(checks), "missing:", missing)

    # frozen RC1 values from processed CSVs
    rc1 = Path(r"D:\Research\crypto_thesis\time-policy\experiments\runs\e1_20260727_ec8b193_r3\processed")
    stat = pd.read_csv(rc1 / "e1_statistical_summary.csv")
    print("RC1 statistical summary rows:", len(stat))
    out["frozen_data"]["rc1_rows"] = len(stat)

    Path(ROOT / "docs/midterm-report/m6/_numeric_evidence.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote _numeric_evidence.json")


if __name__ == "__main__":
    main()
