# -*- coding: utf-8 -*-
"""M6: regenerate all experiment figures from frozen data with academic labels.

Internal experiment codes (E1-A, RC2, HEADER_ONLY, LOCAL_ONLY, ...) are removed
from titles, axes and legends. Figure numbers are left to the Word captions.
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
OUT = ROOT / "docs/midterm-report/m6/figures"
OUT.mkdir(parents=True, exist_ok=True)

RC1_PROC = Path(r"D:\Research\crypto_thesis\time-policy\experiments\runs\e1_20260727_ec8b193_r3\processed")
RC2_SRC = Path(r"D:\Research\crypto_thesis\epoch-authorization\docs\thesis-drafts\research-content-2-final\figure-sources")
RC3_ANA = ROOT / "experiments/r3/formal/analysis"
MATRIX = ROOT / "docs/research-content-3-implementation/i11/formal-config-matrix.json"

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["axes.edgecolor"] = "#333333"
plt.rcParams["axes.linewidth"] = 0.8

COLORS = ["#2f5b8f", "#3a8f6f", "#c07a2f", "#7a4fa0", "#b04a4a"]
METHODS = ["B0", "B1", "C0", "C1"]
METHOD_LABEL = {
    "B0": "规范区间基线",
    "B1": "规范区间基线＋区间缓存",
    "C0": "层次覆盖执行",
    "C1": "层次覆盖执行＋节点缓存",
}
METHOD_COLOR = {"B0": "#2f5b8f", "B1": "#3a8f6f", "C0": "#c07a2f", "C1": "#7a4fa0"}
REP_LABEL = {"dyadic": "层次覆盖", "interval": "规范区间", "enumerated": "时间槽枚举"}


def save(fig, name):
    fig.savefig(OUT / name, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", name)


def fig_match_latency():
    df = pd.read_csv(RC1_PROC / "figure_4_4_data.csv")
    sub = df[df["metric"] == "match_per_query_ns"].copy()
    sub["方法"] = sub["method"].map(REP_LABEL)
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.0), sharey=True)
    for ax, cov in zip(axes, sorted(sub["actual_coverage"].unique())):
        d = sub[sub["actual_coverage"] == cov]
        data = [d[d["方法"] == m]["median"] for m in REP_LABEL.values()]
        bp = ax.boxplot(data, patch_artist=True, widths=0.5, showfliers=False,
                        medianprops=dict(color="black", lw=1.2))
        for patch, c in zip(bp["boxes"], COLORS[:3]):
            patch.set_facecolor(c)
            patch.set_alpha(0.45)
        ax.set_xticks(range(1, 4), list(REP_LABEL.values()), fontsize=9)
        ax.set_title(f"覆盖率 {cov:.0%}", fontsize=11)
        ax.grid(axis="y", ls="--", alpha=0.4)
    axes[0].set_ylabel("匹配中位时延（ns）")
    fig.suptitle("匹配查询中位时延（按覆盖率分组）", fontsize=12.5)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    save(fig, "m6-exp-fig4-match.png")


def fig_rep_size():
    df = pd.read_csv(RC1_PROC / "figure_4_2_data.csv")
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.0), sharey=True)
    cols = [("dyadic", "层次覆盖", "#2f5b8f"), ("interval", "规范区间", "#3a8f6f"),
            ("enumerated", "时间槽枚举", "#c07a2f")]
    for ax, cov in zip(axes, sorted(df["actual_coverage"].unique())):
        d = df[df["actual_coverage"] == cov]
        data = [d[c] for c, _, _ in cols]
        bp = ax.boxplot(data, patch_artist=True, widths=0.5, showfliers=True,
                        flierprops=dict(marker=".", ms=3, alpha=0.4),
                        medianprops=dict(color="black", lw=1.2))
        for patch, (_, _, c) in zip(bp["boxes"], cols):
            patch.set_facecolor(c)
            patch.set_alpha(0.45)
        ax.set_xticks(range(1, 4), [x[1] for x in cols], fontsize=9)
        ax.set_title(f"覆盖率 {cov:.0%}", fontsize=11)
        ax.grid(axis="y", ls="--", alpha=0.4)
    axes[0].set_ylabel("逻辑字节数（对数坐标）")
    axes[0].set_yscale("log")
    fig.suptitle("三种表示的逻辑规模（按覆盖率分组）", fontsize=12.5)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    save(fig, "m6-exp-fig5-rep-size.png")


def fig_boundary():
    df = pd.read_csv(RC1_PROC / "figure_4_5_data.csv")
    fig, ax = plt.subplots(figsize=(8.6, 4.2))
    pairs = [("CR_enum_interval", "枚举 vs 区间", COLORS[0]),
             ("CR_enum_cover", "枚举 vs 覆盖", COLORS[1]),
             ("CR_interval_cover", "区间 vs 覆盖", COLORS[2])]
    covs = sorted(df["actual_coverage"].unique())
    positions, labels = [], []
    for ci, cov in enumerate(covs):
        d = df[df["actual_coverage"] == cov]
        base = ci * 4
        for k, (col, _, c) in enumerate(pairs):
            bp = ax.boxplot(d[col], positions=[base + k], widths=0.6, patch_artist=True,
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
    ax.set_title("表示压缩比与适用边界（按覆盖率分组）", fontsize=12.5)
    save(fig, "m6-exp-fig6-boundary.png")


def fig_stage_share():
    df = pd.read_csv(RC2_SRC / "figure-5-7-stage-share.csv")
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    cats = ["chain_read", "verify", "issue", "match", "other"]
    labels = {"chain_read": "链读取", "verify": "验证", "issue": "签发", "match": "匹配", "other": "其他"}
    bottom = np.zeros(len(df))
    for k, c in enumerate(cats):
        ax.bar(df["method"].map(METHOD_LABEL), df[c], bottom=bottom, label=labels[c],
               color=COLORS[k], alpha=0.75, edgecolor="#333333", linewidth=0.7)
        bottom += df[c].to_numpy()
    ax.set_ylabel("端到端时延占比（%）")
    ax.set_ylim(96, 100)
    ax.legend(fontsize=8.5, frameon=False, ncol=5, loc="lower center")
    ax.set_title("端到端时延的阶段占比（中位数）", fontsize=12.5)
    save(fig, "m6-exp-fig12-stage.png")


def fig_run_latency():
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
    ax.set_xticks(range(1, 5), [METHOD_LABEL[m] for m in METHODS], fontsize=8.5)
    ax.set_ylabel("运行级端到端中位时延（ms）")
    ax.grid(axis="y", ls="--", alpha=0.4)
    ax.set_title("四种授权执行方法的运行级端到端时延分布", fontsize=12.5)
    save(fig, "m6-exp-fig10-latency.png")


def fig_paired():
    df = pd.read_csv(RC2_SRC / "figure-5-3-paired-effects.csv")
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    x = np.arange(len(df))
    means = df["mean_difference_ms"].to_numpy()
    low = df["ci95_mean_low_ms"].to_numpy()
    high = df["ci95_mean_high_ms"].to_numpy()
    ax.errorbar(x, means, yerr=[means - low, high - means], fmt="o-", color="#2f5b8f",
                capsize=4, lw=1.2, ms=6, mfc="white", mec="#2f5b8f")
    ax.axhline(0, color="#666666", ls="--", lw=0.9)
    ax.set_xticks(x, df["comparison"], fontsize=8.5)
    ax.set_ylabel("均值差（ms，Bootstrap 95% CI）")
    ax.grid(axis="y", ls="--", alpha=0.4)
    ax.set_title("自然配对比较与运行级 Bootstrap 置信区间", fontsize=12.5)
    save(fig, "m6-exp-fig13-paired.png")


def fig_concurrency():
    df = pd.read_csv(RC2_SRC / "figure-5-4-concurrency.csv")
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    for m in METHODS:
        d = df[df["method"] == m].sort_values("concurrency")
        ax.plot(d["concurrency"], d["median_end_to_end_ms"], marker="o", ms=6, lw=1.4,
                color=METHOD_COLOR[m], label=METHOD_LABEL[m])
    ax.set_xlabel("并发度（运行级）")
    ax.set_ylabel("端到端中位时延（ms）")
    ax.legend(fontsize=8.5, frameon=False)
    ax.grid(axis="y", ls="--", alpha=0.4)
    ax.set_title("并发度对端到端时延的影响", fontsize=12.5)
    save(fig, "m6-exp-fig9-concurrency.png")


def fig_fragmentation():
    df = pd.read_csv(RC2_SRC / "figure-5-5-fragmentation.csv")
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    for m in METHODS:
        d = df[df["method"] == m].sort_values("fragmentation")
        ax.plot(d["fragmentation"], d["median_match_us"], marker="s", ms=6, lw=1.4,
                color=METHOD_COLOR[m], label=METHOD_LABEL[m])
    ax.set_xlabel("碎片率")
    ax.set_ylabel("匹配中位时延（μs）")
    ax.legend(fontsize=8.5, frameon=False)
    ax.grid(axis="y", ls="--", alpha=0.4)
    ax.set_title("碎片率对局部匹配时延的影响", fontsize=12.5)
    save(fig, "m6-exp-fig14-frag.png")


def fig_locality():
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
            ax.bar(x + (k - 0.5) * w, vals, width=w, label=METHOD_LABEL[m],
                   color=METHOD_COLOR[m], alpha=0.75, edgecolor="#333333", linewidth=0.7)
        ax.set_xticks(x, ["区间热点", "节点热点", "均匀"])
        ax.set_ylabel(ylab)
        ax.legend(fontsize=8, frameon=False)
        ax.grid(axis="y", ls="--", alpha=0.4)
    axes[0].set_title("缓存命中率", fontsize=11)
    axes[1].set_title("端到端时延", fontsize=11)
    fig.suptitle("请求局部性与缓存的影响", fontsize=12.5)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    save(fig, "m6-exp-fig11-locality.png")


def _rc3_duration(cfg_keys, names, ylab, title, fname):
    d = json.loads((RC3_ANA / "descriptive-statistics.json").read_text(encoding="utf-8"))
    b = json.loads((RC3_ANA / "bootstrap-results.json").read_text(encoding="utf-8"))
    fig, ax = plt.subplots(figsize=(8.2, 4.2))
    x = np.arange(len(cfg_keys))
    meds = [d[k]["median"] for k in cfg_keys]
    lo = [b[k]["percentile"][0] for k in cfg_keys]
    hi = [b[k]["percentile"][1] for k in cfg_keys]
    ax.errorbar(x, meds, yerr=[np.array(meds) - np.array(lo), np.array(hi) - np.array(meds)],
                fmt="o-", color="#2f5b8f", capsize=4, lw=1.2, ms=6, mfc="white", mec="#2f5b8f")
    ax.set_xticks(x, names, fontsize=9)
    ax.set_ylabel(ylab)
    ax.grid(axis="y", ls="--", alpha=0.4)
    ax.set_title(title, fontsize=12.5)
    save(fig, fname)


def fig_e1_paths():
    _rc3_duration(
        ["E1-C1", "E1-C2", "E1-C3", "E1-C4"],
        ["初始发布", "密文主体与密钥轮换", "撤销闭合", "副本恢复"],
        "端到端中位时延（ms，Bootstrap 95% CI）",
        "四类生命周期路径端到端时延",
        "m6-exp-fig17-e1-paths.png",
    )


def fig_e2_header():
    desc = json.loads((RC3_ANA / "descriptive-statistics.json").read_text(encoding="utf-8"))
    boot = json.loads((RC3_ANA / "bootstrap-results.json").read_text(encoding="utf-8"))
    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))["measured"]
    e2 = [c for c in matrix if c["experimentId"] == "E2"]
    groups = {"1": [c for c in e2 if c["affectedResourceCount"] == 1],
              "4": [c for c in e2 if c["affectedResourceCount"] == 4]}
    fig, ax = plt.subplots(figsize=(8.2, 4.2))
    x = np.array([2, 8, 32])
    w = 6
    for k, (aff, cfgs) in enumerate(groups.items()):
        def key(c):
            return f"E2-C{c['configIndex']}"
        sorted_cfgs = sorted(cfgs, key=lambda c: c["recipientCount"])
        meds = [desc[key(c)]["median"] for c in sorted_cfgs]
        lo = [boot[key(c)]["percentile"][0] for c in sorted_cfgs]
        hi = [boot[key(c)]["percentile"][1] for c in sorted_cfgs]
        xx = x + (k - 0.5) * w
        ax.errorbar(xx, meds, yerr=[np.array(meds) - np.array(lo), np.array(hi) - np.array(meds)],
                    fmt="o-", color=COLORS[k], capsize=4, lw=1.4, ms=6,
                    label=f"受影响资源数 {aff}")
    ax.set_xticks(x, ["2", "8", "32"])
    ax.set_xlabel("接收者数")
    ax.set_ylabel("端到端中位时延（ms，Bootstrap 95% CI）")
    ax.legend(fontsize=9, frameon=False)
    ax.grid(axis="y", ls="--", alpha=0.4)
    ax.set_title("仅密文头更新的规模影响（接收者×受影响资源）", fontsize=12)
    save(fig, "m6-exp-fig18-e2-header.png")


def fig_e3_body():
    desc = json.loads((RC3_ANA / "descriptive-statistics.json").read_text(encoding="utf-8"))
    boot = json.loads((RC3_ANA / "bootstrap-results.json").read_text(encoding="utf-8"))
    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))["measured"]
    e3 = [c for c in matrix if c["experimentId"] == "E3"]
    sizes = {65536: "64 KiB", 1048576: "1 MiB", 8388608: "8 MiB"}
    fig, ax = plt.subplots(figsize=(8.4, 4.2))
    x = np.arange(3)
    w = 0.26
    for k, recv in enumerate([2, 8, 32]):
        cfgs = sorted([c for c in e3 if c["recipientCount"] == recv], key=lambda c: c["bodySizeBytes"])
        def key(c):
            return f"E3-C{c['configIndex']}"
        meds = [desc[key(c)]["median"] for c in cfgs]
        lo = [boot[key(c)]["percentile"][0] for c in cfgs]
        hi = [boot[key(c)]["percentile"][1] for c in cfgs]
        ax.errorbar(x + (k - 1) * w, meds, yerr=[np.array(meds) - np.array(lo), np.array(hi) - np.array(meds)],
                    fmt="o-", color=COLORS[k], capsize=4, lw=1.4, ms=6, label=f"接收者 {recv}")
    ax.set_xticks(x, ["64 KiB", "1 MiB", "8 MiB"])
    ax.set_xlabel("密文主体规模")
    ax.set_ylabel("端到端中位时延（ms，Bootstrap 95% CI）")
    ax.legend(fontsize=9, frameon=False)
    ax.grid(axis="y", ls="--", alpha=0.4)
    ax.set_title("密文主体与密钥轮换的规模影响（密文主体规模×接收者）", fontsize=12)
    save(fig, "m6-exp-fig19-e3-body.png")


def fig_e5_recovery():
    desc = json.loads((RC3_ANA / "descriptive-statistics.json").read_text(encoding="utf-8"))
    boot = json.loads((RC3_ANA / "bootstrap-results.json").read_text(encoding="utf-8"))
    keys = ["E5-C1", "E5-C2", "E5-C3", "E5-C4"]
    names = ["仅本地对象\n无故障", "隔离副本\n无故障", "仅本地对象\n对象损坏", "隔离副本\n对象损坏"]
    fig, ax = plt.subplots(figsize=(8.0, 4.2))
    x = np.arange(len(keys))
    meds = [desc[k]["median"] for k in keys]
    lo = [boot[k]["percentile"][0] for k in keys]
    hi = [boot[k]["percentile"][1] for k in keys]
    colors = [COLORS[0], COLORS[1], COLORS[3], COLORS[4]]
    ax.bar(x, meds, yerr=[np.array(meds) - np.array(lo), np.array(hi) - np.array(meds)],
           color=colors, alpha=0.75, edgecolor="#333333", linewidth=0.8,
           capsize=4, error_kw={"elinewidth": 1.0, "ecolor": "#333333"})
    ax.set_xticks(x, names, fontsize=9)
    ax.set_ylabel("恢复端到端中位时延（ms，Bootstrap 95% CI）")
    ax.grid(axis="y", ls="--", alpha=0.4)
    ax.set_title("故障恢复端到端时延对比（对象来源×故障场景）", fontsize=12.5)
    save(fig, "m6-exp-fig20-e5-recovery.png")


def main():
    fig_match_latency()
    fig_rep_size()
    fig_boundary()
    fig_stage_share()
    fig_run_latency()
    fig_paired()
    fig_concurrency()
    fig_fragmentation()
    fig_locality()
    fig_e1_paths()
    fig_e2_header()
    fig_e3_body()
    fig_e5_recovery()
    print("all M6 experiment figures written")


if __name__ == "__main__":
    main()
