"""Draw two structural schematics (no new mechanisms) for the M2 report."""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


OUT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep\docs\midterm-report\m2\figures")
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False


def box(ax, x, y, w, h, text, fc="#eef4fb", ec="#2f5597", fs=11):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02",
                                linewidth=1.2, edgecolor=ec, facecolor=fc))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)


def arrow(ax, x1, y1, x2, y2, label=None, fs=9):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=14, linewidth=1.2, color="#444444"))
    if label:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.03, label, ha="center", va="bottom", fontsize=fs)


def cap2_flow() -> None:
    fig, ax = plt.subplots(figsize=(9, 5.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    box(ax, 0.4, 4.6, 2.2, 1.0, "Issuer\n(能力签发)", fc="#eaf3ea")
    box(ax, 3.6, 4.6, 2.4, 1.0, "链上授权状态\nAuthorizationState", fc="#fdf3e3")
    box(ax, 7.2, 4.6, 2.4, 1.0, "资源/用户状态\npolicyDigest/版本", fc="#fdf3e3")
    box(ax, 0.4, 2.4, 2.2, 1.0, "CAP2 能力\n(Ed25519 签名)", fc="#eaf3ea")
    box(ax, 3.6, 2.4, 2.4, 1.0, "Verifier\n(验证实例)", fc="#eaf3ea")
    box(ax, 7.2, 2.4, 2.4, 1.0, "PostgreSQL\n共享原子 Nonce", fc="#fdeaea")
    box(ax, 3.6, 0.3, 2.4, 1.0, "材料释放判定\nAccessMaterialReleaseGuard", fc="#eef4fb")
    arrow(ax, 2.6, 5.1, 3.6, 5.1, "初读状态")
    arrow(ax, 6.0, 5.1, 7.2, 5.1, "确认快照")
    arrow(ax, 6.0, 4.6, 4.8, 3.4, "状态一致")
    arrow(ax, 2.6, 2.9, 3.6, 2.9, "能力验证")
    arrow(ax, 6.0, 2.9, 7.2, 2.9, "原子消费 Nonce")
    arrow(ax, 4.8, 2.4, 4.8, 1.3, "全部通过后")
    arrow(ax, 6.0, 0.8, 7.2, 0.8, "释放密文材料")
    ax.set_title("图 CAP2 能力签发与验证流程（依据冻结协议绘制）", fontsize=12)
    fig.tight_layout()
    fig.savefig(OUT / "schematic-cap2-flow.png", dpi=200)
    plt.close(fig)


def closure_arch() -> None:
    fig, ax = plt.subplots(figsize=(9, 5.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    box(ax, 0.3, 4.8, 2.6, 1.0, "策略编译\n(I* / C(P) / 摘要)", fc="#eaf3ea")
    box(ax, 3.7, 4.8, 2.6, 1.0, "许可联盟链\nAuthorizationState", fc="#fdf3e3")
    box(ax, 7.1, 4.8, 2.6, 1.0, "HeaderRegistry\n(版本/摘要)", fc="#fdf3e3")
    box(ax, 3.7, 3.0, 2.6, 1.0, "数据库任务状态机\n(operationId 幂等)", fc="#fdeaea")
    box(ax, 7.1, 3.0, 2.6, 1.0, "版本化密文头部\nHeader/Body/CK", fc="#eef4fb")
    box(ax, 0.3, 3.0, 2.6, 1.0, "材料释放判定\nFail-Closed", fc="#eef4fb")
    box(ax, 0.3, 1.0, 2.6, 1.0, "LocalObjectStore\n(不可变对象)", fc="#f4f0ec")
    box(ax, 3.7, 1.0, 2.6, 1.0, "Kubo 隔离副本\n(恢复来源)", fc="#f4f0ec")
    box(ax, 7.1, 1.0, 2.6, 1.0, "RecoveryCoordinator\n(摘要验证/恢复)", fc="#eef4fb")
    arrow(ax, 2.9, 5.3, 3.7, 5.3, "摘要/状态注册")
    arrow(ax, 6.3, 5.3, 7.1, 5.3, "版本/摘要登记")
    arrow(ax, 4.8, 4.8, 4.8, 4.0, "状态读取")
    arrow(ax, 8.4, 4.8, 8.4, 4.0, "Header 提交")
    arrow(ax, 2.9, 3.5, 3.7, 3.5, "复合状态判定")
    arrow(ax, 6.3, 3.5, 7.1, 3.5, "释放/更新指令")
    arrow(ax, 2.9, 1.5, 3.7, 1.5, "对象读取/恢复")
    arrow(ax, 8.4, 1.5, 8.4, 2.2, "摘要校验")
    ax.set_title("图 链上授权状态、任务状态与链下对象闭环架构（依据冻结方案绘制）", fontsize=12)
    fig.tight_layout()
    fig.savefig(OUT / "schematic-closure-arch.png", dpi=200)
    plt.close(fig)


def main() -> None:
    cap2_flow()
    closure_arch()
    print("schematics written to", OUT)


if __name__ == "__main__":
    main()
