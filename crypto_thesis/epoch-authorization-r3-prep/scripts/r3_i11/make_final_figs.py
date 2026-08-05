# -*- coding: utf-8 -*-
"""Regenerate the three scientifically-fixed experiment figures for FINAL-CLEAN.

* fig12 stage share: full 0-100% stacked scale with a 96-100 inset instead of
  a truncated y-axis (data unchanged);
* fig17 lifecycle paths: discrete dot plot with error bars, no connecting
  line (four independent lifecycle categories);
* fig20 recovery: correct E5 config mapping (NONE/CORRUPT_RESTORE x LOCAL/KUBO)
  and title "可比较故障场景下的恢复端到端时延"; CID-mismatch and both-missing
  are excluded from the recovery-duration comparison by design.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
OUT = ROOT / "docs/midterm-report/final/figures"
OUT.mkdir(parents=True, exist_ok=True)

RC2_SRC = Path(r"D:\Research\crypto_thesis\epoch-authorization\docs\thesis-drafts\research-content-2-final\figure-sources")
RC3_ANA = ROOT / "experiments/r3/formal/analysis"

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["axes.edgecolor"] = "#333333"
plt.rcParams["axes.linewidth"] = 0.8

COLORS = ["#2f5b8f", "#3a8f6f", "#c07a2f", "#7a4fa0", "#b04a4a"]
METHOD_LABEL = {
    "B0": "规范区间基线",
    "B1": "规范区间基线＋区间缓存",
    "C0": "层次覆盖执行",
    "C1": "层次覆盖执行＋节点缓存",
}


def save(fig, name):
    fig.savefig(OUT / name, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", name)


def fig_stage_share():
    """Full 0-100 scale stacked bars + zoomed inset (data unchanged)."""
    df = pd.read_csv(RC2_SRC / "figure-5-7-stage-share.csv")
    cats = ["chain_read", "verify", "issue", "match", "other"]
    labels = {"chain_read": "链读取", "verify": "验证", "issue": "签发", "match": "匹配", "other": "其他"}
    fig, ax = plt.subplots(figsize=(7.8, 4.6))
    methods = df["method"].map(METHOD_LABEL).tolist()
    x = np.arange(len(df))
    bottom = np.zeros(len(df))
    for k, c in enumerate(cats):
        ax.bar(x, df[c], bottom=bottom, label=labels[c],
               color=COLORS[k], alpha=0.75, edgecolor="#333333", linewidth=0.7)
        bottom += df[c].to_numpy()
    ax.set_xticks(x, methods)
    ax.set_ylabel("端到端时延占比（%）")
    ax.set_ylim(0, 100)
    ax.legend(fontsize=8.5, frameon=False, ncol=5, loc="lower center", bbox_to_anchor=(0.5, -0.18))
    ax.set_title("端到端时延的阶段占比（中位数，0–100% 全尺度）", fontsize=12.5)
    ax.grid(axis="y", ls="--", alpha=0.4)
    # zoomed inset: 96-100 region so the small non-chain-read segments are
    # visually comparable without a truncated main axis.
    inset = fig.add_axes([0.52, 0.13, 0.40, 0.42])
    bottom2 = np.zeros(len(df))
    for k, c in enumerate(cats):
        inset.bar(x, df[c], bottom=bottom2, color=COLORS[k], alpha=0.75,
                  edgecolor="#333333", linewidth=0.6)
        bottom2 += df[c].to_numpy()
    inset.set_xticks(x, methods, fontsize=7)
    inset.tick_params(axis="y", labelsize=7)
    inset.set_ylim(96, 100)
    inset.set_title("局部放大（96–100%）", fontsize=9)
    inset.grid(axis="y", ls="--", alpha=0.4)
    save(fig, "m6-exp-fig12-stage.png")


def _rc3_duration(cfg_keys, names, ylab, title, fname, *, dot_only=False):
    d = json.loads((RC3_ANA / "descriptive-statistics.json").read_text(encoding="utf-8"))
    b = json.loads((RC3_ANA / "bootstrap-results.json").read_text(encoding="utf-8"))
    fig, ax = plt.subplots(figsize=(8.2, 4.2))
    x = np.arange(len(cfg_keys))
    meds = [d[k]["median"] for k in cfg_keys]
    lo = [b[k]["percentile"][0] for k in cfg_keys]
    hi = [b[k]["percentile"][1] for k in cfg_keys]
    fmt = "o" if dot_only else "o-"
    ax.errorbar(x, meds, yerr=[np.array(meds) - np.array(lo), np.array(hi) - np.array(meds)],
                fmt=fmt, color="#2f5b8f", capsize=4, lw=1.2, ms=7, mfc="white", mec="#2f5b8f")
    ax.set_xticks(x, names, fontsize=9)
    ax.set_ylabel(ylab)
    ax.grid(axis="y", ls="--", alpha=0.4)
    ax.set_title(title, fontsize=12.5)
    save(fig, fname)


def fig_e1_paths():
    # four discrete lifecycle paths: dot plot with error bars, no connecting line
    _rc3_duration(
        ["E1-C1", "E1-C2", "E1-C3", "E1-C4"],
        ["初始发布", "密文主体与密钥轮换", "撤销闭合", "副本恢复"],
        "端到端中位时延（ms，Bootstrap 95% CI）",
        "四类生命周期路径端到端时延（独立类别）",
        "m6-exp-fig17-e1-paths.png",
        dot_only=True,
    )


def fig_e5_recovery():
    d = json.loads((RC3_ANA / "descriptive-statistics.json").read_text(encoding="utf-8"))
    b = json.loads((RC3_ANA / "bootstrap-results.json").read_text(encoding="utf-8"))
    # Correct frozen mapping: C1/C5 NONE, C2/C6 CORRUPT_RESTORE across sources.
    keys = ["E5-C1", "E5-C5", "E5-C2", "E5-C6"]
    names = ["仅本地对象\n无故障", "隔离副本\n无故障", "仅本地对象\n对象损坏", "隔离副本\n对象损坏"]
    fig, ax = plt.subplots(figsize=(8.4, 4.6))
    x = np.arange(len(keys))
    meds = [d[k]["median"] for k in keys]
    lo = [b[k]["percentile"][0] for k in keys]
    hi = [b[k]["percentile"][1] for k in keys]
    colors = [COLORS[0], COLORS[1], COLORS[3], COLORS[4]]
    ax.bar(x, meds, yerr=[np.array(meds) - np.array(lo), np.array(hi) - np.array(meds)],
           color=colors, alpha=0.75, edgecolor="#333333", linewidth=0.8,
           capsize=4, error_kw={"elinewidth": 1.0, "ecolor": "#333333"})
    ax.set_xticks(x, names, fontsize=9)
    ax.set_ylabel("恢复端到端中位时延（ms，Bootstrap 95% CI）")
    ax.grid(axis="y", ls="--", alpha=0.4)
    ax.set_title("可比较故障场景下的恢复端到端时延", fontsize=12.5)
    ax.text(0.5, -0.28,
            "内容标识不一致与双端缺失场景按 Fail-Closed 终止，不纳入恢复时延比较。",
            transform=ax.transAxes, ha="center", fontsize=8.5)
    save(fig, "m6-exp-fig20-e5-recovery.png")


def main() -> None:
    import sys

    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    fig_stage_share()
    fig_e1_paths()
    fig_e5_recovery()
    print("final experiment figures written")


if __name__ == "__main__":
    main()
