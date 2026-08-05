# -*- coding: utf-8 -*-
"""M3: redraw experiment figures (12) from frozen evidence, grayscale style."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
OUT = ROOT / "docs/midterm-report/m3/figures"
OUT.mkdir(parents=True, exist_ok=True)

RC1_PROC = Path(r"D:\Research\crypto_thesis\time-policy\experiments\runs\e1_20260727_ec8b193_r3\processed")
RC2_SRC = Path(r"D:\Research\crypto_thesis\epoch-authorization\docs\thesis-drafts\research-content-2-final\figure-sources")
RC2_TAB = Path(r"D:\Research\crypto_thesis\epoch-authorization\docs\thesis-drafts\research-content-2-final\tables")
RC3_ANA = ROOT / "experiments/r3/formal/analysis"

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["axes.edgecolor"] = "#333333"
plt.rcParams["axes.linewidth"] = 0.8

BLACK = "#111111"
GRAY = "#666666"
METHOD_ORDER = ["B0", "B1", "C0", "C1"]
HATCHES = ["", "//", "xx", "..", "\\\\"]
GREYS = ["#ffffff", "#d9d9d9", "#b0b0b0", "#808080", "#666666"]


def save(fig, name, title):
    fig.savefig(OUT / name, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", name, "|", title)


def fig_rep_size() -> None:
    df = pd.read_csv(RC1_PROC / "figure_4_2_data.csv")
    fig, ax = plt.subplots(figsize=(7.6, 4.4))
    x = np.arange(len(df))
    w = 0.26
    cols = [("dyadic", "层次覆盖 C(P)"), ("interval", "规范区间列表 I*"), ("enumerated", "时间槽枚举")]
    for k, (col, lab) in enumerate(cols):
        ax.bar(x + (k - 1) * w, df[col], width=w, label=lab, color=GREYS[k],
               edgecolor=BLACK, hatch=HATCHES[k], linewidth=0.8)
    ax.set_yscale("log")
    ax.set_xticks(x, [f"E1-A-{i:04d}" for i in range(len(df))], rotation=55, fontsize=7.5)
    ax.set_ylabel("逻辑字节数（对数坐标）")
    ax.set_xlabel("样本（按覆盖率/碎片率排序）")
    ax.legend(fontsize=9, frameon=False)
    ax.set_title("图8 匹配查询中位时延（E1-A 正式实验，数据冻结）", fontsize=11.5)
    save(fig, "m3-exp-fig8-rep-size.png", "图8 表示规模比较")


def fig_compile_time() -> None:
    df = pd.read_csv(RC1_PROC / "figure_4_3_data.csv")
    sub = df[df["metric"] == "compile_ns"].copy()
    sub["median_us"] = sub["median"] / 1e3
    sub["lo"] = sub["ci95_low"] / 1e3
    sub["hi"] = sub["ci95_high"] / 1e3
    fig, ax = plt.subplots(figsize=(7.6, 4.4))
    x = np.arange(len(sub))
    ax.errorbar(x, sub["median_us"], yerr=[sub["median_us"] - sub["lo"], sub["hi"] - sub["median_us"]],
                fmt="o-", color=BLACK, capsize=3, linewidth=1.0, markersize=4)
    ax.set_yscale("log")
    ax.set_xticks(x, [f"{r.experiment_group}-{r.sample_id.split('-')[-1]}" for r in sub.itertuples()], rotation=55, fontsize=7.5)
    ax.set_ylabel("编译中位时延（μs，对数坐标）")
    ax.set_title("图9 三种表示的逻辑规模比较（E1-A 正式实验，数据冻结）", fontsize=11.5)
    save(fig, "m3-exp-fig9-compile.png", "图9 编译时延")


def fig_match_latency() -> None:
    df = pd.read_csv(RC1_PROC / "figure_4_4_data.csv")
    sub = df[df["metric"] == "match_per_query_ns"].copy()
    sub["median_ns"] = sub["median"]
    fig, ax = plt.subplots(figsize=(7.6, 4.4))
    for k, method in enumerate(["dyadic", "interval", "enumerated"]):
        d = sub[sub["method"] == method]
        x = np.arange(len(d))
        ax.plot(x, d["median_ns"], marker="o", ms=3.5, lw=1.0, color=GREYS[k],
                label={"dyadic": "层次覆盖", "interval": "规范区间", "enumerated": "时间槽枚举"}[method],
                markeredgecolor=BLACK, markerfacecolor=GREYS[k])
    ax.set_xticks(range(len(sub[sub["method"] == "dyadic"])),
                  [f"{r.experiment_group}-{r.sample_id.split('-')[-1]}" for r in sub[sub["method"] == "dyadic"].itertuples()],
                  rotation=55, fontsize=7.5)
    ax.set_ylabel("单次匹配中位时延（ns）")
    ax.legend(fontsize=9, frameon=False)
    ax.set_title("图10 表示的压缩比与适用边界（E1-A）", fontsize=11.5)
    save(fig, "m3-exp-fig10-match.png", "图10 匹配时延")


def fig_boundary() -> None:
    df = pd.read_csv(RC1_PROC / "figure_4_5_data.csv")
    fig, ax = plt.subplots(figsize=(7.6, 4.4))
    x = np.arange(len(df))
    w = 0.26
    for k, (col, lab) in enumerate([("CR_enum_interval", "枚举 vs 区间"), ("CR_enum_cover", "枚举 vs 覆盖"), ("CR_interval_cover", "区间 vs 覆盖")]):
        ax.bar(x + (k - 1) * w, df[col], width=w, label=lab, color=GREYS[k],
               edgecolor=BLACK, hatch=HATCHES[k], linewidth=0.8)
    ax.axhline(1.0, color=BLACK, ls="--", lw=0.8)
    ax.set_xticks(x, [f"{r.experiment_group}-{r.sample_id.split('-')[-1]}" for r in df.itertuples()], rotation=55, fontsize=7.5)
    ax.set_ylabel("压缩比（基准表示 / 目标表示）")
    ax.legend(fontsize=8.5, frameon=False)
    ax.set_title("图11 端到端时延的阶段占比（中位数，RC2）", fontsize=11.5)
    save(fig, "m3-exp-fig11-boundary.png", "图11 适用边界")


def fig_run_latency() -> None:
    df = pd.read_csv(RC2_SRC / "figure-5-2-run-latency.csv")
    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    values = [df.loc[df["method"] == m, "median_end_to_end_ms"] for m in METHOD_ORDER]
    parts = ax.violinplot(values, showmeans=False, showmedians=True, showextrema=False)
    for k, body in enumerate(parts["bodies"]):
        body.set_facecolor(GREYS[k])
        body.set_alpha(0.6)
        body.set_edgecolor(BLACK)
    ax.boxplot(values, widths=0.14, showfliers=False, patch_artist=True,
               boxprops={"facecolor": "white", "edgecolor": BLACK},
               medianprops={"color": BLACK}, whiskerprops={"color": BLACK},
               capprops={"color": BLACK})
    ax.set_xticks(range(1, 5), METHOD_ORDER)
    ax.set_ylabel("运行级端到端中位时延（ms）")
    ax.set_title("图12 四种方法的运行级端到端时延分布（RC2 正式实验）", fontsize=11.5)
    save(fig, "m3-exp-fig12-run-latency.png", "图12 端到端时延分布")


def fig_stage_share() -> None:
    df = pd.read_csv(RC2_SRC / "figure-5-7-stage-share.csv")
    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    cats = ["chain_read", "verify", "issue", "match", "other"]
    labels = {"chain_read": "链读取", "verify": "验证", "issue": "签发", "match": "匹配", "other": "其他"}
    bottom = np.zeros(len(df))
    for k, c in enumerate(cats):
        ax.bar(df["method"], df[c], bottom=bottom, label=labels[c], color=GREYS[k],
               edgecolor=BLACK, hatch=HATCHES[k], linewidth=0.8)
        bottom += df[c].to_numpy()
    ax.set_ylabel("端到端时延占比（%）")
    ax.set_ylim(96, 100)
    ax.legend(fontsize=8.5, frameon=False, ncol=3, loc="lower center")
    ax.set_title("图13 自然配对比较与运行级 Bootstrap 置信区间（RC2）", fontsize=11.5)
    save(fig, "m3-exp-fig13-stage-share.png", "图13 阶段占比")


def fig_paired_effects() -> None:
    df = pd.read_csv(RC2_SRC / "figure-5-3-paired-effects.csv")
    fig, ax = plt.subplots(figsize=(7.6, 4.4))
    x = np.arange(len(df))
    means = df["mean_difference_ms"].to_numpy()
    low = df["ci95_mean_low_ms"].to_numpy()
    high = df["ci95_mean_high_ms"].to_numpy()
    ax.errorbar(x, means, yerr=[means - low, high - means], fmt="o-", color=BLACK,
                capsize=4, lw=1.0, ms=5, mfc="white", mec=BLACK)
    ax.axhline(0, color=GRAY, ls="--", lw=0.8)
    ax.set_xticks(x, df["comparison"])
    ax.set_ylabel("均值差（ms，Bootstrap 95% CI）")
    ax.set_title("图14 并发度对端到端时延的影响（RC2）", fontsize=11.5)
    save(fig, "m3-exp-fig14-paired.png", "图14 配对效应")


def fig_concurrency() -> None:
    df = pd.read_csv(RC2_SRC / "figure-5-4-concurrency.csv")
    fig, ax = plt.subplots(figsize=(7.6, 4.4))
    for k, m in enumerate(METHOD_ORDER):
        d = df[df["method"] == m].sort_values("concurrency")
        ax.plot(d["concurrency"], d["median_end_to_end_ms"], marker="o", ms=4, lw=1.0,
                color=GREYS[k], label=m, markeredgecolor=BLACK)
    ax.set_xlabel("并发度（运行级）")
    ax.set_ylabel("端到端中位时延（ms）")
    ax.legend(fontsize=9, frameon=False)
    ax.set_title("图15 碎片率对匹配时延的影响（RC2，局部匹配）", fontsize=11.5)
    save(fig, "m3-exp-fig15-concurrency.png", "图15 并发影响")


def fig_fragmentation() -> None:
    df = pd.read_csv(RC2_SRC / "figure-5-5-fragmentation.csv")
    fig, ax = plt.subplots(figsize=(7.6, 4.4))
    for k, m in enumerate(METHOD_ORDER):
        d = df[df["method"] == m].sort_values("fragmentation")
        ax.plot(d["fragmentation"], d["median_match_us"], marker="s", ms=4, lw=1.0,
                color=GREYS[k], label=m, markeredgecolor=BLACK)
    ax.set_xlabel("碎片率")
    ax.set_ylabel("匹配中位时延（μs）")
    ax.legend(fontsize=9, frameon=False)
    ax.set_title("图16 请求局部性与缓存的影响（RC2）", fontsize=11.5)
    save(fig, "m3-exp-fig16-fragmentation.png", "图16 碎片率影响")


def fig_locality() -> None:
    df = pd.read_csv(RC2_SRC / "figure-5-6-locality-cache.csv")
    methods = [m for m in METHOD_ORDER if m in set(df["method"])]
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.2))
    for ax, metric, ylab, title in [
        (axes[0], "median_cache_hit_rate", "缓存命中率中位数", "局部性×缓存命中率"),
        (axes[1], "median_end_to_end_ns", "端到端中位时延（ms）", "局部性×端到端时延"),
    ]:
        x = np.arange(3)
        w = 0.2
        for k, m in enumerate(methods):
            d = df[df["method"] == m].sort_values("level")
            vals = d[metric] / 1e6 if metric.endswith("_ns") else d[metric]
            ax.bar(x + (k - (len(methods) - 1) / 2) * w, vals, width=w, label=m, color=GREYS[k],
                   edgecolor=BLACK, hatch=HATCHES[k], linewidth=0.8)
        ax.set_xticks(x, ["区间热点", "节点热点", "均匀"])
        ax.set_ylabel(ylab)
        ax.set_title(title, fontsize=10.5)
        ax.legend(fontsize=8, frameon=False)
    fig.suptitle("图16 请求局部性与缓存的影响（RC2）", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    save(fig, "m3-exp-fig17-locality.png", "图17 局部性与缓存")


def rc3_duration(cfg_keys, names, ylab, title, fname, ylim=None) -> None:
    d = json.loads((RC3_ANA / "descriptive-statistics.json").read_text(encoding="utf-8"))
    b = json.loads((RC3_ANA / "bootstrap-results.json").read_text(encoding="utf-8"))
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    x = np.arange(len(cfg_keys))
    meds = [d[k]["median"] for k in cfg_keys]
    lo = [b[k]["percentile"][0] for k in cfg_keys]
    hi = [b[k]["percentile"][1] for k in cfg_keys]
    ax.errorbar(x, meds, yerr=[np.array(meds) - np.array(lo), np.array(hi) - np.array(meds)],
                fmt="o-", color=BLACK, capsize=4, lw=1.0, ms=5, mfc="white", mec=BLACK)
    ax.set_xticks(x, names, fontsize=9)
    ax.set_ylabel(ylab)
    if ylim:
        ax.set_ylim(*ylim)
    ax.set_title(title, fontsize=11.5)
    save(fig, fname, title)


def fig_rc3_operations() -> None:
    rc3_duration(
        ["E1-C1", "E1-C2", "E1-C3", "E1-C4"],
        ["HEADER_ONLY\n规模 1", "HEADER_ONLY\n规模 2", "HEADER_ONLY\n规模 3", "HEADER_ONLY\n规模 4"],
        "端到端中位时延（ms，Bootstrap 95% CI）",
        "图17 HEADER_ONLY 操作端到端时延（RC3 正式实验）",
        "m3-exp-fig18-header-only.png", ylim=(2900, 3400),
    )
    rc3_duration(
        ["E2-C1", "E2-C2", "E2-C3", "E2-C4", "E2-C5", "E2-C6"],
        ["BODY_ROTATION\n规模 1", "BODY_ROTATION\n规模 2", "BODY_ROTATION\n规模 3",
         "BODY_ROTATION\n规模 4", "BODY_ROTATION\n规模 5", "BODY_ROTATION\n规模 6"],
        "端到端中位时延（ms，Bootstrap 95% CI）",
        "图18 BODY_ROTATION 操作端到端时延（RC3 正式实验）",
        "m3-exp-fig19-body-rotation.png",
    )


def fig_rc3_recovery() -> None:
    d = json.loads((RC3_ANA / "descriptive-statistics.json").read_text(encoding="utf-8"))
    b = json.loads((RC3_ANA / "bootstrap-results.json").read_text(encoding="utf-8"))
    cfg = ["E5-C1", "E5-C2", "E5-C3", "E5-C4"]
    names = ["LOCAL_ONLY\n无故障", "KUBO_REPLICA\n无故障", "LOCAL_ONLY\n对象损坏", "KUBO_REPLICA\n对象损坏"]
    fig, ax = plt.subplots(figsize=(7.8, 4.2))
    x = np.arange(len(cfg))
    meds = [d[k]["median"] for k in cfg]
    lo = [b[k]["percentile"][0] for k in cfg]
    hi = [b[k]["percentile"][1] for k in cfg]
    colors = ["white", "#d9d9d9", "white", "#d9d9d9"]
    ax.bar(x, meds, yerr=[np.array(meds) - np.array(lo), np.array(hi) - np.array(meds)],
           color=colors, edgecolor=BLACK, hatch=["", "//", "", "//"], linewidth=0.9,
           capsize=4, error_kw={"elinewidth": 1.0, "ecolor": BLACK})
    ax.set_xticks(x, names, fontsize=9)
    ax.set_ylabel("恢复端到端中位时延（ms，Bootstrap 95% CI）")
    ax.set_ylim(2800, 3600)
    ax.set_title("图19 LOCAL_ONLY 与 KUBO_REPLICA 恢复时延对比（RC3 E5）", fontsize=11.5)
    save(fig, "m3-exp-fig20-recovery.png", "图20 恢复对比")


def main() -> None:
    fig_rep_size()
    fig_compile_time()
    fig_match_latency()
    fig_boundary()
    fig_run_latency()
    fig_stage_share()
    fig_paired_effects()
    fig_concurrency()
    fig_fragmentation()
    fig_locality()
    fig_rc3_operations()
    fig_rc3_recovery()
    print("all 12 experiment figures written to", OUT)


if __name__ == "__main__":
    main()
