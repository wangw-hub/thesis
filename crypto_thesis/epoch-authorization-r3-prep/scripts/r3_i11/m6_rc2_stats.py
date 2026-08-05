# -*- coding: utf-8 -*-
"""M6: recompute RC2 table statistics from frozen figure-source CSVs."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


SRC = Path(r"D:\Research\crypto_thesis\epoch-authorization\docs\thesis-drafts\research-content-2-final\figure-sources")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    run = pd.read_csv(SRC / "figure-5-2-run-latency.csv")
    conc = pd.read_csv(SRC / "figure-5-4-concurrency.csv")
    stage = pd.read_csv(SRC / "figure-5-7-stage-share.csv")
    paired = pd.read_csv(SRC / "figure-5-3-paired-effects.csv")

    print("=== overall stats per method (from figure-5-2) ===")
    for m in ["B0", "B1", "C0", "C1"]:
        d = run[run["method"] == m]
        print(f"{m}: median={d['median_end_to_end_ms'].median():.3f} mean={d['median_end_to_end_ms'].mean():.3f} n={len(d)}")

    print("=== concurrency-level medians (figure-5-4) ===")
    for m in ["B0", "B1", "C0", "C1"]:
        d = conc[conc["method"] == m]
        print(m, "levels:", d["level"].tolist())
        print("  throughput median across levels:", d["median_throughput_rps"].median())
        print("  cache hit median across levels:", d["median_cache_hit_rate"].median())

    print("=== stage share (figure-5-7) ===")
    for _, r in stage.iterrows():
        print(f"{r['method']}: chain_read={r['chain_read']:.3f} match={r['match']:.3f} issue={r['issue']:.3f} verify={r['verify']:.3f} other={r['other']:.3f}")

    print("=== paired comparisons (figure-5-3) ===")
    for _, r in paired.iterrows():
        print(r["comparison"], "| med_diff_ms=", round(r["median_difference_ms"], 3),
              "mean_diff_ms=", round(r["mean_difference_ms"], 3),
              "ci=[" , round(r["ci95_mean_low_ms"],3), round(r["ci95_mean_high_ms"],3), "]",
              "improved=", r["improved_fraction"], "degraded=", r["degraded_fraction"])


if __name__ == "__main__":
    main()
