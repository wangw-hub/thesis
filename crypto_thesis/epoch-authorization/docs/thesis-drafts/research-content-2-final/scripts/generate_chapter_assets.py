#!/usr/bin/env python3
"""Generate Chapter 5 figures and tables from frozen V13 evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[4]
RUN = (
    REPO
    / "experiments/runs"
    / "formal_auth_multihost_rerun_v13_20260729T073007Z_8a3d795"
)
OUT = Path(__file__).resolve().parents[1]
FIGURES = OUT / "figures"
TABLES = OUT / "tables"
SOURCES = OUT / "figure-sources"

REQUEST_SHA = "00dbdc62c21a7c12143394118df5dc00bbe7108d822a4af41bd6a96aa89cc4ce"
RAW_INDEX_SHA = "3cb273c3d1938fb4af2dee4d9f0c78f69033380efd0c37f68ae3258990720680"
METHODS = ["B0", "B1", "C0", "C1"]
COLORS = {
    "B0": "#2F5597",
    "B1": "#70AD47",
    "C0": "#C55A11",
    "C1": "#8064A2",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def save_figure(fig: plt.Figure, stem: str) -> None:
    fig.tight_layout()
    fig.savefig(FIGURES / f"{stem}.png", dpi=220, bbox_inches="tight")
    fig.savefig(FIGURES / f"{stem}.pdf", bbox_inches="tight")
    plt.close(fig)


def setup_style() -> None:
    plt.rcParams.update(
        {
            "font.sans-serif": [
                "Microsoft YaHei",
                "SimHei",
                "Noto Sans CJK SC",
                "DejaVu Sans",
            ],
            "axes.unicode_minus": False,
            "font.size": 10,
            "axes.grid": True,
            "grid.alpha": 0.22,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )


def write_tables(
    method: pd.DataFrame, paired: pd.DataFrame, factors: pd.DataFrame
) -> None:
    table1 = method.copy()
    for col in [
        "median_end_to_end_ns",
        "mean_end_to_end_ns",
        "median_match_ns",
        "median_chain_read_ns",
        "median_issue_ns",
        "median_verify_ns",
    ]:
        table1[col.replace("_ns", "_ms")] = table1[col] / 1e6
    table1["chain_read_percent"] = table1["chain_read_share"] * 100
    table1[
        [
            "method",
            "runs",
            "median_end_to_end_ms",
            "mean_end_to_end_ms",
            "median_throughput_rps",
            "median_cache_hit_rate",
            "chain_read_percent",
        ]
    ].to_csv(TABLES / "table-5-1-method-overall.csv", index=False)

    table2 = paired.copy()
    for col in [
        "mean_difference_ns",
        "median_difference_ns",
        "ci95_mean_low_ns",
        "ci95_mean_high_ns",
        "engineering_threshold_ns",
    ]:
        table2[col.replace("_ns", "_ms")] = table2[col] / 1e6
    table2[
        [
            "comparison",
            "paired_runs",
            "median_difference_ms",
            "mean_difference_ms",
            "ci95_mean_low_ms",
            "ci95_mean_high_ms",
            "robust_effect",
            "improved_fraction",
            "degraded_fraction",
            "no_material_change_fraction",
            "engineering_threshold_ms",
        ]
    ].to_csv(TABLES / "table-5-2-paired-comparisons.csv", index=False)

    concurrency = factors[factors["factor"] == "concurrency"].copy()
    concurrency["median_end_to_end_ms"] = concurrency["median_end_to_end_ns"] / 1e6
    concurrency[
        [
            "method",
            "level",
            "runs",
            "median_end_to_end_ms",
            "median_throughput_rps",
        ]
    ].rename(columns={"level": "concurrency"}).to_csv(
        TABLES / "table-5-3-concurrency.csv", index=False
    )

    fragmentation = factors[factors["factor"] == "fragmentation"].copy()
    fragmentation["fragmentation"] = fragmentation["level"].map(
        lambda value: 0.5 if 0.49 < float(value) < 0.50 else float(value)
    )
    fragmentation["median_match_us"] = fragmentation["median_match_ns"] / 1e3
    fragmentation["median_end_to_end_ms"] = (
        fragmentation["median_end_to_end_ns"] / 1e6
    )
    fragmentation[
        [
            "method",
            "fragmentation",
            "runs",
            "median_match_us",
            "median_end_to_end_ms",
        ]
    ].to_csv(TABLES / "table-5-4-fragmentation.csv", index=False)

    locality = factors[factors["factor"] == "locality"].copy()
    locality["median_end_to_end_ms"] = locality["median_end_to_end_ns"] / 1e6
    locality[
        [
            "method",
            "level",
            "runs",
            "median_cache_hit_rate",
            "median_end_to_end_ms",
        ]
    ].rename(columns={"level": "locality"}).to_csv(
        TABLES / "table-5-5-locality-cache.csv", index=False
    )

    stage = method[
        [
            "method",
            "median_end_to_end_ns",
            "median_chain_read_ns",
            "median_match_ns",
            "median_issue_ns",
            "median_verify_ns",
        ]
    ].copy()
    for metric in ["chain_read", "match", "issue", "verify"]:
        stage[f"{metric}_percent"] = (
            stage[f"median_{metric}_ns"] / stage["median_end_to_end_ns"] * 100
        )
    stage["other_percent"] = (
        100
        - stage[
            [
                "chain_read_percent",
                "match_percent",
                "issue_percent",
                "verify_percent",
            ]
        ].sum(axis=1)
    ).clip(lower=0)
    stage[
        [
            "method",
            "chain_read_percent",
            "match_percent",
            "issue_percent",
            "verify_percent",
            "other_percent",
        ]
    ].to_csv(TABLES / "table-5-6-stage-share.csv", index=False)


def figure_design() -> None:
    source = pd.DataFrame(
        [
            ["方法", 4, "B0、B1、C0、C1"],
            ["碎片率", 3, "0、0.5、1"],
            ["局部性", 3, "均匀、区间热点、节点热点"],
            ["并发度", 3, "1、4、16"],
            ["随机种子", 3, "固定3个"],
            ["正式重复", 30, "每个含seed配置30次"],
        ],
        columns=["factor", "levels", "values"],
    )
    source.to_csv(SOURCES / "figure-5-1-design.csv", index=False)
    fig, ax = plt.subplots(figsize=(9.0, 4.8))
    ax.axis("off")
    boxes = [
        (0.02, 0.62, 0.19, 0.24, "因素矩阵\n4×3×3×3=108"),
        (0.27, 0.62, 0.19, 0.24, "固定种子\n108×3=324"),
        (0.52, 0.62, 0.19, 0.24, "正式重复\n324×30=9,720"),
        (0.77, 0.62, 0.19, 0.24, "请求与链读取\n77,760 / 233,280"),
    ]
    for x, y, w, h, label in boxes:
        ax.add_patch(
            plt.Rectangle((x, y), w, h, facecolor="#EAF0F8", edgecolor="#365F91")
        )
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center")
    for x in [0.22, 0.47, 0.72]:
        ax.annotate("", xy=(x + 0.04, 0.74), xytext=(x, 0.74),
                    arrowprops={"arrowstyle": "->", "color": "#444444"})
    ax.text(
        0.5,
        0.36,
        "自然配对键：workload_id × seed × repetition",
        ha="center",
        va="center",
        fontsize=11,
    )
    ax.text(
        0.5,
        0.20,
        "主要推断单位：运行块；请求级观测仅用于运行内描述与完整性审计",
        ha="center",
        va="center",
        fontsize=10,
    )
    ax.set_title("图5-1  V13正式实验因素与运行级配对结构", pad=12)
    save_figure(fig, "figure-5-1-design")


def figure_latency(runs: pd.DataFrame) -> None:
    source = runs[["method", "median_end_to_end_ns"]].copy()
    source["median_end_to_end_ms"] = source["median_end_to_end_ns"] / 1e6
    source.to_csv(SOURCES / "figure-5-2-run-latency.csv", index=False)
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    values = [
        source.loc[source["method"] == method, "median_end_to_end_ms"]
        for method in METHODS
    ]
    parts = ax.violinplot(values, showmeans=False, showmedians=True, showextrema=False)
    for body, method in zip(parts["bodies"], METHODS):
        body.set_facecolor(COLORS[method])
        body.set_alpha(0.55)
    ax.boxplot(values, widths=0.16, showfliers=False, patch_artist=True,
               boxprops={"facecolor": "white", "alpha": 0.8},
               medianprops={"color": "black"})
    ax.set_xticks(range(1, 5), METHODS)
    ax.set_ylabel("运行级端到端中位时延（ms）")
    ax.set_title("图5-2  四种方法的运行级端到端时延分布")
    save_figure(fig, "figure-5-2-run-latency")


def figure_pairs(paired: pd.DataFrame) -> None:
    source = paired.copy()
    for col in ["mean_difference_ns", "median_difference_ns",
                "ci95_mean_low_ns", "ci95_mean_high_ns"]:
        source[col.replace("_ns", "_ms")] = source[col] / 1e6
    source.to_csv(SOURCES / "figure-5-3-paired-effects.csv", index=False)
    fig, ax = plt.subplots(figsize=(7.8, 4.8))
    x = np.arange(len(source))
    means = source["mean_difference_ms"].to_numpy()
    low = source["ci95_mean_low_ms"].to_numpy()
    high = source["ci95_mean_high_ms"].to_numpy()
    ax.errorbar(x, means, yerr=[means - low, high - means], fmt="o",
                color="#2F5597", capsize=5, label="均值差及95% Bootstrap CI")
    ax.scatter(x, source["median_difference_ms"], marker="D", color="#C55A11",
               label="配对中位差", zorder=4)
    ax.axhline(0, color="black", linewidth=0.9)
    ax.axhspan(-1, 1, color="#A9D18E", alpha=0.18, label="±1 ms工程阈值")
    ax.set_xticks(x, source["comparison"])
    ax.set_ylabel("左方法－右方法（ms）")
    ax.set_title("图5-3  运行级配对差值与95%置信区间")
    ax.legend(frameon=False, fontsize=8)
    save_figure(fig, "figure-5-3-paired-effects")


def figure_concurrency(factors: pd.DataFrame) -> None:
    source = factors[factors["factor"] == "concurrency"].copy()
    source["concurrency"] = source["level"].astype(int)
    source["median_end_to_end_ms"] = source["median_end_to_end_ns"] / 1e6
    source.to_csv(SOURCES / "figure-5-4-concurrency.csv", index=False)
    fig, ax = plt.subplots(figsize=(7.8, 4.8))
    for method in METHODS:
        part = source[source["method"] == method].sort_values("concurrency")
        ax.plot(part["concurrency"], part["median_end_to_end_ms"], marker="o",
                label=method, color=COLORS[method])
    ax.set_xticks([1, 4, 16])
    ax.set_xlabel("并发度")
    ax.set_ylabel("运行级端到端中位时延（ms）")
    ax.set_title("图5-4  并发度对端到端时延的影响")
    ax.legend(frameon=False, ncol=4)
    save_figure(fig, "figure-5-4-concurrency")


def figure_fragmentation(factors: pd.DataFrame) -> None:
    source = factors[factors["factor"] == "fragmentation"].copy()
    source["fragmentation"] = source["level"].map(
        lambda value: 0.5 if 0.49 < float(value) < 0.50 else float(value)
    )
    source["median_match_us"] = source["median_match_ns"] / 1e3
    source.to_csv(SOURCES / "figure-5-5-fragmentation.csv", index=False)
    fig, ax = plt.subplots(figsize=(7.8, 4.8))
    for method in METHODS:
        part = source[source["method"] == method].sort_values("fragmentation")
        ax.plot(part["fragmentation"], part["median_match_us"], marker="o",
                label=method, color=COLORS[method])
    ax.set_xticks([0, 0.5, 1])
    ax.set_xlabel("碎片率 F")
    ax.set_ylabel("局部匹配中位耗时（μs）")
    ax.set_title("图5-5  碎片率对局部策略匹配耗时的影响")
    ax.legend(frameon=False, ncol=4)
    save_figure(fig, "figure-5-5-fragmentation")


def figure_locality(factors: pd.DataFrame) -> None:
    order = ["UNIFORM", "INTERVAL_HOTSPOT", "NODE_HOTSPOT"]
    labels = ["均匀", "区间热点", "节点热点"]
    source = factors[
        (factors["factor"] == "locality") & factors["method"].isin(["B1", "C1"])
    ].copy()
    source.to_csv(SOURCES / "figure-5-6-locality-cache.csv", index=False)
    fig, ax = plt.subplots(figsize=(7.8, 4.8))
    x = np.arange(3)
    width = 0.34
    for offset, method in [(-width / 2, "B1"), (width / 2, "C1")]:
        part = source[source["method"] == method].set_index("level").loc[order]
        ax.bar(x + offset, part["median_cache_hit_rate"], width,
               label=method, color=COLORS[method], alpha=0.82)
    ax.set_xticks(x, labels)
    ax.set_ylim(0, 1)
    ax.set_ylabel("运行级缓存命中率中位数")
    ax.set_title("图5-6  请求局部性对缓存命中率的影响")
    ax.legend(frameon=False)
    save_figure(fig, "figure-5-6-locality-cache")


def figure_stage(method: pd.DataFrame) -> None:
    source = method[["method", "median_end_to_end_ns", "median_chain_read_ns",
                     "median_match_ns", "median_issue_ns", "median_verify_ns"]].copy()
    for metric in ["chain_read", "match", "issue", "verify"]:
        source[metric] = source[f"median_{metric}_ns"] / source["median_end_to_end_ns"] * 100
    source["other"] = (
        100 - source[["chain_read", "match", "issue", "verify"]].sum(axis=1)
    ).clip(lower=0)
    source.to_csv(SOURCES / "figure-5-7-stage-share.csv", index=False)
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    bottom = np.zeros(len(source))
    palette = {
        "chain_read": "#4472C4",
        "match": "#70AD47",
        "issue": "#ED7D31",
        "verify": "#A5A5A5",
        "other": "#FFD966",
    }
    labels = {
        "chain_read": "链读取",
        "match": "策略匹配",
        "issue": "签发净开销",
        "verify": "验证净开销",
        "other": "调度等其他开销",
    }
    for metric in ["chain_read", "match", "issue", "verify", "other"]:
        ax.bar(source["method"], source[metric], bottom=bottom,
               label=labels[metric], color=palette[metric])
        bottom += source[metric].to_numpy()
    ax.set_ylim(0, 100)
    ax.set_ylabel("端到端时延占比（%）")
    ax.set_title("图5-7  端到端时延构成")
    ax.legend(frameon=False, ncol=3, fontsize=8, loc="lower center")
    save_figure(fig, "figure-5-7-stage-share")


def figure_chain_stability(requests: pd.DataFrame, reads: pd.DataFrame) -> None:
    request_time = requests[["request_id", "timestamp_utc"]].drop_duplicates("request_id")
    source = reads[["request_id", "block_number", "block_hash", "rpc_error"]].merge(
        request_time, on="request_id", how="left", validate="many_to_one"
    )
    source["timestamp_utc"] = pd.to_datetime(source["timestamp_utc"], utc=True)
    source = source.sort_values("timestamp_utc")
    sampled = source.iloc[:: max(1, len(source) // 4000)].copy()
    sampled.to_csv(SOURCES / "figure-5-8-chain-stability.csv", index=False)
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.4), gridspec_kw={"width_ratios": [3, 1]})
    axes[0].plot(sampled["timestamp_utc"], sampled["block_number"],
                 color="#2F5597", linewidth=1)
    axes[0].set_xlabel("UTC时间")
    axes[0].set_ylabel("读取区块高度")
    axes[0].set_title("V13链读取区块高度")
    axes[0].tick_params(axis="x", rotation=25)
    axes[1].bar(["准入/终验"], [4], color="#70AD47", width=0.55)
    axes[1].set_ylim(0, 5)
    axes[1].set_ylabel("peerCount")
    axes[1].set_title("冻结健康检查")
    axes[1].text(0, 4.15, "4", ha="center")
    fig.suptitle("图5-8  正式实验链状态稳定性", y=1.02)
    save_figure(fig, "figure-5-8-chain-stability")


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    SOURCES.mkdir(parents=True, exist_ok=True)
    if sha256(RUN / "raw/requests.jsonl") != REQUEST_SHA:
        raise SystemExit("V13 requests hash mismatch")
    frozen_index = json.loads(
        (RUN / "formal-artifact-sha256.json").read_text(encoding="utf-8")
    )
    if frozen_index["raw_index_sha256"] != RAW_INDEX_SHA:
        raise SystemExit("V13 raw artifact index hash mismatch")

    method = pd.read_csv(RUN / "analysis/method-summary.csv")
    paired = pd.read_csv(RUN / "analysis/paired-method-comparisons.csv")
    factors = pd.read_csv(RUN / "analysis/factor-effects.csv")
    runs = pd.read_csv(RUN / "analysis/run_level_metrics.csv")
    requests = pd.read_json(RUN / "raw/requests.jsonl", lines=True)
    reads = pd.read_json(RUN / "raw/chain-reads.jsonl", lines=True)
    setup_style()
    write_tables(method, paired, factors)
    figure_design()
    figure_latency(runs)
    figure_pairs(paired)
    figure_concurrency(factors)
    figure_fragmentation(factors)
    figure_locality(factors)
    figure_stage(method)
    figure_chain_stability(requests, reads)
    print(f"generated figures={len(list(FIGURES.glob('*.png')))} tables={len(list(TABLES.glob('*.csv')))}")


if __name__ == "__main__":
    main()
