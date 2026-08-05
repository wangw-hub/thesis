# -*- coding: utf-8 -*-
"""M4: readable colored experiment figures, regrouped/faceted from frozen data."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
OUT = ROOT / "docs/midterm-report/m4/figures"
OUT.mkdir(parents=True, exist_ok=True)

RC1_PROC = Path(r"D:\Research\crypto_thesis\time-policy\experiments\runs\e1_20260727_ec8b193_r3\processed")
RC2_SRC = Path(r"D:\Research\crypto_thesis\epoch-authorization\docs\thesis-drafts\research-content-2-final\figure-sources")
RC3_ANA = ROOT / "experiments/r3/formal/analysis"

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["axes.edgecolor"] = "#333333"
plt.rcParams["axes.linewidth"] = 0.8

COLORS = ["#2f5b8f", "#3a8f6f", "#c07a2f", "#7a4fa0", "#b04a4a"]
METHODS = ["B0", "B1", "C0", "C1"]
METHOD_COLOR = {"B0": "#2f5b8f", "B1": "#3a8f6f", "C0": "#c07a2f", "C1": "#7a4fa0"}


def save(fig, name, title):
    fig.savefig(OUT / name, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", name)


def fig8_match_latency():
    df = pd.read_csv(RC1_PROC / "figure_4_4_data.csv")
    sub = df[df["metric"] == "match_per_query_ns"].copy()
    sub["median_ns"] = sub["median"]
    order = {"dyadic": "层次覆盖", "interval": "规范区间", "enumerated": "时间槽枚举"}
    sub["方法"] = sub["method"].map(order)
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.0), sharey=True)
    for ax, cov in zip(axes, sorted(sub["actual_coverage"].unique())):
        d = sub[sub["actual_coverage"] == cov]
        data = [d[d["方法"] == m]["median_ns"] for m in order.values()]
        bp = ax.boxplot(data, patch_artist=True, widths=0.5, showfliers=False,
                        medianprops=dict(color="black", lw=1.2))
        for patch, c in zip(bp["boxes"], COLORS[:3]):
            patch.set_facecolor(c)
            patch.set_alpha(0.45)
        ax.set_xticks(range(1, 4), list(order.values()), fontsize=9)
        ax.set_title(f"覆盖率 {cov:.0%}", fontsize=11)
        ax.grid(axis="y", ls="--", alpha=0.4)
    axes[0].set_ylabel("匹配中位时延（ns）")
    fig.suptitle("图8 匹配查询中位时延按覆盖率分组（E1-A 正式实验）", fontsize=12.5)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    save(fig, "m4-exp-fig8-match.png", "图8")


def fig9_rep_size():
    df = pd.read_csv(RC1_PROC / "figure_4_2_data.csv")
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.0), sharey=True)
    cols = [("dyadic", "层次覆盖", "#2f5b8f"), ("interval", "规范区间", "#3a8f6f"), ("enumerated", "时间槽枚举", "#c07a2f")]
    for ax, cov in zip(axes, sorted(df["actual_coverage"].unique())):
        d = df[df["actual_coverage"] == cov]
        data = [d[c] for c, _, _ in cols]
        bp = ax.boxplot(data, patch_artist=True, widths=0.5, showfliers=True, flierprops=dict(marker=".", ms=3, alpha=0.4),
                        medianprops=dict(color="black", lw=1.2))
        for patch, (_, _, c) in zip(bp["boxes"], cols):
            patch.set_facecolor(c)
            patch.set_alpha(0.45)
        ax.set_xticks(range(1, 4), [x[1] for x in cols], fontsize=9)
        ax.set_title(f"覆盖率 {cov:.0%}", fontsize=11)
        ax.grid(axis="y", ls="--", alpha=0.4)
    axes[0].set_ylabel("逻辑字节数（对数坐标）")
    axes[0].set_yscale("log")
    fig.suptitle("图9 三种表示的逻辑规模按覆盖率分组（E1-A 正式实验）", fontsize=12.5)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    save(fig, "m4-exp-fig9-rep-size.png", "图9")


def fig10_boundary():
    df = pd.read_csv(RC1_PROC / "figure_4_5_data.csv")
    fig, ax = plt.subplots(figsize=(8.6, 4.2))
    pairs = [("CR_enum_interval", "枚举 vs 区间", COLORS[0]),
             ("CR_enum_cover", "枚举 vs 覆盖", COLORS[1]),
             ("CR_interval_cover", "区间 vs 覆盖", COLORS[2])]
    covs = sorted(df["actual_coverage"].unique())
    positions = []
    labels = []
    for ci, cov in enumerate(covs):
        d = df[df["actual_coverage"] == cov]
        base = ci * 4
        for k, (col, lab, c) in enumerate(pairs):
            pos = base + k
            bp = ax.boxplot(d[col], positions=[pos], widths=0.6, patch_artist=True,
                            showfliers=True, flierprops=dict(marker=".", ms=3, alpha=0.35),
                            medianprops=dict(color="black", lw=1.2))
            bp["boxes"][0].set_facecolor(c)
            bp["boxes"][0].set_alpha(0.55)
        positions.append(base + 1)
        labels.append(f"覆盖率 {cov:.0%}")
    for ci in range(len(covs)):
        ax.axvline(ci * 4 + 3.5, color="#999999", ls=":", lw=0.8)
    ax.set_xticks(positions, labels)
    ax.set_ylabel("压缩比（基准表示 / 目标表示）")
    ax.set_ylim(0, 8)
    ax.axhline(1.0, color="#333333", ls="--", lw=0.9)
    handles = [plt.Line2D([0], [0], color=c, lw=6, alpha=0.55, label=lab) for _, lab, c in pairs]
    ax.legend(handles=handles, fontsize=9, frameon=False, ncol=3, loc="upper left")
    ax.grid(axis="y", ls="--", alpha=0.4)
    ax.set_title("图10 表示压缩比与适用边界（按覆盖率分组，E1-A）", fontsize=12.5)
    save(fig, "m4-exp-fig10-boundary.png", "图10")


def fig11_stage_share():
    df = pd.read_csv(RC2_SRC / "figure-5-7-stage-share.csv")
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    cats = ["chain_read", "verify", "issue", "match", "other"]
    labels = {"chain_read": "链读取", "verify": "验证", "issue": "签发", "match": "匹配", "other": "其他"}
    bottom = np.zeros(len(df))
    for k, c in enumerate(cats):
        ax.bar(df["method"], df[c], bottom=bottom, label=labels[c], color=COLORS[k], alpha=0.75,
               edgecolor="#333333", linewidth=0.7)
        bottom += df[c].to_numpy()
    ax.set_ylabel("端到端时延占比（%）")
    ax.set_ylim(96, 100)
    ax.legend(fontsize=8.5, frameon=False, ncol=5, loc="lower center")
    ax.set_title("图11 端到端时延的阶段占比（中位数，RC2）", fontsize=12.5)
    save(fig, "m4-exp-fig11-stage.png", "图11")


def fig12_run_latency():
    df = pd.read_csv(RC2_SRC / "figure-5-2-run-latency.csv")
    fig, ax = plt.subplots(figsize=(7.6, 4.4))
    values = [df.loc[df["method"] == m, "median_end_to_end_ms"] for m in METHODS]
    parts = ax.violinplot(values, showmeans=False, showmedians=True, showextrema=False)
    for k, body in enumerate(parts["bodies"]):
        body.set_facecolor(METHOD_COLOR[METHODS[k]])
        body.set_alpha(0.5)
        body.set_edgecolor("#333333")
    ax.boxplot(values, widths=0.14, showfliers=False, patch_artist=True,
               boxprops=dict(facecolor="white", edgecolor="#333333"),
               medianprops=dict(color="black"), whiskerprops=dict(color="#333333"),
               capprops=dict(color="#333333"))
    ax.set_xticks(range(1, 5), METHODS)
    ax.set_ylabel("运行级端到端中位时延（ms）")
    ax.grid(axis="y", ls="--", alpha=0.4)
    ax.set_title("图12 四种方法的运行级端到端时延分布（RC2 正式实验）", fontsize=12.5)
    save(fig, "m4-exp-fig12-latency.png", "图12")


def fig13_paired():
    df = pd.read_csv(RC2_SRC / "figure-5-3-paired-effects.csv")
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    x = np.arange(len(df))
    means = df["mean_difference_ms"].to_numpy()
    low = df["ci95_mean_low_ms"].to_numpy()
    high = df["ci95_mean_high_ms"].to_numpy()
    ax.errorbar(x, means, yerr=[means - low, high - means], fmt="o-", color="#2f5b8f",
                capsize=4, lw=1.2, ms=6, mfc="white", mec="#2f5b8f")
    ax.axhline(0, color="#666666", ls="--", lw=0.9)
    ax.set_xticks(x, df["comparison"])
    ax.set_ylabel("均值差（ms，Bootstrap 95% CI）")
    ax.grid(axis="y", ls="--", alpha=0.4)
    ax.set_title("图13 自然配对比较与运行级 Bootstrap 置信区间（RC2）", fontsize=12.5)
    save(fig, "m4-exp-fig13-paired.png", "图13")


def fig14_concurrency():
    df = pd.read_csv(RC2_SRC / "figure-5-4-concurrency.csv")
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    for m in METHODS:
        d = df[df["method"] == m].sort_values("concurrency")
        ax.plot(d["concurrency"], d["median_end_to_end_ms"], marker="o", ms=6, lw=1.4,
                color=METHOD_COLOR[m], label=m)
    ax.set_xlabel("并发度（运行级）")
    ax.set_ylabel("端到端中位时延（ms）")
    ax.legend(fontsize=9, frameon=False)
    ax.grid(axis="y", ls="--", alpha=0.4)
    ax.set_title("图14 并发度对端到端时延的影响（RC2）", fontsize=12.5)
    save(fig, "m4-exp-fig14-concurrency.png", "图14")


def fig15_fragmentation():
    df = pd.read_csv(RC2_SRC / "figure-5-5-fragmentation.csv")
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    for m in METHODS:
        d = df[df["method"] == m].sort_values("fragmentation")
        ax.plot(d["fragmentation"], d["median_match_us"], marker="s", ms=6, lw=1.4,
                color=METHOD_COLOR[m], label=m)
    ax.set_xlabel("碎片率")
    ax.set_ylabel("匹配中位时延（μs）")
    ax.legend(fontsize=9, frameon=False)
    ax.grid(axis="y", ls="--", alpha=0.4)
    ax.set_title("图15 碎片率对局部匹配时延的影响（RC2）", fontsize=12.5)
    save(fig, "m4-exp-fig15-frag.png", "图15")


def fig16_locality():
    df = pd.read_csv(RC2_SRC / "figure-5-6-locality-cache.csv")
    methods = [m for m in METHODS if m in set(df["method"])]
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.0))
    x = np.arange(3)
    w = 0.28
    for ax, metric, ylab in [(axes[0], "median_cache_hit_rate", "缓存命中率中位数"),
                             (axes[1], "median_end_to_end_ns", "端到端中位时延（ms）")]:
        for k, m in enumerate(methods):
            d = df[df["method"] == m].sort_values("level")
            vals = d[metric] / 1e6 if metric.endswith("_ns") else d[metric]
            ax.bar(x + (k - 0.5) * w, vals, width=w, label=m, color=METHOD_COLOR[m], alpha=0.75,
                   edgecolor="#333333", linewidth=0.7)
        ax.set_xticks(x, ["区间热点", "节点热点", "均匀"])
        ax.set_ylabel(ylab)
        ax.legend(fontsize=8.5, frameon=False)
        ax.grid(axis="y", ls="--", alpha=0.4)
    axes[0].set_title("缓存命中率", fontsize=11)
    axes[1].set_title("端到端时延", fontsize=11)
    fig.suptitle("图16 请求局部性与缓存的影响（RC2）", fontsize=12.5)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    save(fig, "m4-exp-fig16-locality.png", "图16")


def rc3_duration(cfg_keys, names, ylab, title, fname):
    d = json.loads((RC3_ANA / "descriptive-statistics.json").read_text(encoding="utf-8"))
    b = json.loads((RC3_ANA / "bootstrap-results.json").read_text(encoding="utf-8"))
    fig, ax = plt.subplots(figsize=(8.2, 4.2))
    x = np.arange(len(cfg_keys))
    meds = [d[k]["median"] for k in cfg_keys]
    lo = [b[k]["percentile"][0] for k in cfg_keys]
    hi = [b[k]["percentile"][1] for k in cfg_keys]
    ax.errorbar(x, meds, yerr=[np.array(meds) - np.array(lo), np.array(hi) - np.array(meds)],
                fmt="o-", color="#2f5b8f", capsize=4, lw=1.2, ms=6, mfc="white", mec="#2f5b8f")
    ax.set_xticks(x, names, fontsize=8.5)
    ax.set_ylabel(ylab)
    ax.grid(axis="y", ls="--", alpha=0.4)
    ax.set_title(title, fontsize=12.5)
    save(fig, fname, title[:6])


def fig17_18_operations():
    rc3_duration(
        ["E1-C1", "E1-C2", "E1-C3", "E1-C4"],
        ["规模1", "规模2", "规模3", "规模4"],
        "端到端中位时延（ms，Bootstrap 95% CI）",
        "图17 HEADER_ONLY 操作端到端时延（RC3 正式实验）",
        "m4-exp-fig17-header.png",
    )
    rc3_duration(
        ["E2-C1", "E2-C2", "E2-C3", "E2-C4", "E2-C5", "E2-C6"],
        ["规模1", "规模2", "规模3", "规模4", "规模5", "规模6"],
        "端到端中位时延（ms，Bootstrap 95% CI）",
        "图18 BODY_ROTATION 操作端到端时延（RC3 正式实验）",
        "m4-exp-fig18-rotation.png",
    )


def fig19_recovery():
    d = json.loads((RC3_ANA / "descriptive-statistics.json").read_text(encoding="utf-8"))
    b = json.loads((RC3_ANA / "bootstrap-results.json").read_text(encoding="utf-8"))
    cfg = ["E5-C1", "E5-C2", "E5-C3", "E5-C4"]
    names = ["LOCAL_ONLY\n无故障", "KUBO_REPLICA\n无故障", "LOCAL_ONLY\n对象损坏", "KUBO_REPLICA\n对象损坏"]
    fig, ax = plt.subplots(figsize=(8.0, 4.2))
    x = np.arange(len(cfg))
    meds = [d[k]["median"] for k in cfg]
    lo = [b[k]["percentile"][0] for k in cfg]
    hi = [b[k]["percentile"][1] for k in cfg]
    colors = [COLORS[0], COLORS[1], COLORS[3], COLORS[4]]
    ax.bar(x, meds, yerr=[np.array(meds) - np.array(lo), np.array(hi) - np.array(meds)],
           color=colors, alpha=0.75, edgecolor="#333333", linewidth=0.8,
           capsize=4, error_kw={"elinewidth": 1.0, "ecolor": "#333333"})
    ax.set_xticks(x, names, fontsize=8.5)
    ax.set_ylabel("恢复端到端中位时延（ms，Bootstrap 95% CI）")
    ax.grid(axis="y", ls="--", alpha=0.4)
    ax.set_title("图19 LOCAL_ONLY 与 KUBO_REPLICA 恢复时延对比（RC3 E5）", fontsize=12.5)
    save(fig, "m4-exp-fig19-recovery.png", "图19")


def main():
    fig8_match_latency()
    fig9_rep_size()
    fig10_boundary()
    fig11_stage_share()
    fig12_run_latency()
    fig13_paired()
    fig14_concurrency()
    fig15_fragmentation()
    fig16_locality()
    fig17_18_operations()
    fig19_recovery()
    print("all M4 experiment figures written")


if __name__ == "__main__":
    main()
