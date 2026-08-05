# -*- coding: utf-8 -*-
"""M5: RC3 experiment figures rebuilt from frozen config matrix + statistics."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
OUT = ROOT / "docs/midterm-report/m5/figures"
OUT.mkdir(parents=True, exist_ok=True)
ANA = ROOT / "experiments/r3/formal/analysis"
MATRIX = ROOT / "docs/research-content-3-implementation/i11/formal-config-matrix.json"

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False

COLORS = ["#2f5b8f", "#3a8f6f", "#c07a2f"]


def save(fig, name, title):
    fig.savefig(OUT / name, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", name)


def load_stats():
    desc = json.loads((ANA / "descriptive-statistics.json").read_text(encoding="utf-8"))
    boot = json.loads((ANA / "bootstrap-results.json").read_text(encoding="utf-8"))
    return desc, boot


def fig17_e1_paths():
    desc, boot = load_stats()
    keys = ["E1-C1", "E1-C2", "E1-C3", "E1-C4"]
    names = ["INITIAL", "BODY_ROTATION", "REVOCATION", "RESTORE"]
    fig, ax = plt.subplots(figsize=(8.0, 4.2))
    x = np.arange(len(keys))
    meds = [desc[k]["median"] for k in keys]
    lo = [boot[k]["percentile"][0] for k in keys]
    hi = [boot[k]["percentile"][1] for k in keys]
    ax.errorbar(x, meds, yerr=[np.array(meds) - np.array(lo), np.array(hi) - np.array(meds)],
                fmt="o-", color="#2f5b8f", capsize=4, lw=1.4, ms=7, mfc="white", mec="#2f5b8f")
    ax.set_xticks(x, names, fontsize=10)
    ax.set_ylabel("端到端中位时延（ms，Bootstrap 95% CI）")
    ax.grid(axis="y", ls="--", alpha=0.4)
    ax.set_title("图17 E1 四类生命周期路径端到端时延（RC3 正式实验）", fontsize=12.5)
    save(fig, "m5-rc3-fig17-e1-paths.png", "图17")


def fig18_e2_header():
    desc, boot = load_stats()
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
    ax.set_title("图18 E2 HEADER_ONLY 规模影响（接收者×受影响资源，RC3 正式实验）", fontsize=12)
    save(fig, "m5-rc3-fig18-e2-header.png", "图18")


def fig19_e3_body():
    desc, boot = load_stats()
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
                    fmt="o-", color=COLORS[k], capsize=4, lw=1.4, ms=6,
                    label=f"接收者 {recv}")
    ax.set_xticks(x, ["64 KiB", "1 MiB", "8 MiB"])
    ax.set_xlabel("Body 规模")
    ax.set_ylabel("端到端中位时延（ms，Bootstrap 95% CI）")
    ax.legend(fontsize=9, frameon=False)
    ax.grid(axis="y", ls="--", alpha=0.4)
    ax.set_title("图19 E3 BODY_ROTATION 规模影响（Body 规模×接收者，RC3 正式实验）", fontsize=12)
    save(fig, "m5-rc3-fig19-e3-body.png", "图19")


def fig20_e5_recovery():
    desc, boot = load_stats()
    keys = ["E5-C1", "E5-C2", "E5-C3", "E5-C4"]
    names = ["LOCAL_ONLY\n无故障", "KUBO_REPLICA\n无故障", "LOCAL_ONLY\n对象损坏", "KUBO_REPLICA\n对象损坏"]
    fig, ax = plt.subplots(figsize=(8.0, 4.2))
    x = np.arange(len(keys))
    meds = [desc[k]["median"] for k in keys]
    lo = [boot[k]["percentile"][0] for k in keys]
    hi = [boot[k]["percentile"][1] for k in keys]
    colors = ["#2f5b8f", "#3a8f6f", "#7a4fa0", "#b04a4a"]
    ax.bar(x, meds, yerr=[np.array(meds) - np.array(lo), np.array(hi) - np.array(meds)],
           color=colors, alpha=0.75, edgecolor="#333333", linewidth=0.8,
           capsize=4, error_kw={"elinewidth": 1.0, "ecolor": "#333333"})
    ax.set_xticks(x, names, fontsize=8.5)
    ax.set_ylabel("恢复端到端中位时延（ms，Bootstrap 95% CI）")
    ax.grid(axis="y", ls="--", alpha=0.4)
    ax.set_title("图20 LOCAL_ONLY 与 KUBO_REPLICA 恢复时延对比（RC3 E5）", fontsize=12.5)
    save(fig, "m5-rc3-fig20-e5-recovery.png", "图20")


def main():
    fig17_e1_paths()
    fig18_e2_header()
    fig19_e3_body()
    fig20_e5_recovery()
    print("M5 RC3 figures written")


if __name__ == "__main__":
    main()
