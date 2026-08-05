# -*- coding: utf-8 -*-
"""M4: high-quality color academic method/architecture figures."""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


OUT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep\docs\midterm-report\m4\figures")
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False

# academic palette: light fills + black text
BLUE = "#dbe7f4"
BLUE_E = "#2f5b8f"
GREEN = "#dceadc"
GREEN_E = "#3a6b3a"
ORANGE = "#fbe8d6"
ORANGE_E = "#b0601f"
PURPLE = "#e6ddf0"
PURPLE_E = "#5d3f8f"
GREY = "#ececec"
GREY_E = "#555555"
RED = "#f6dcdc"
RED_E = "#8f2f2f"
TEXT = "#111111"


def box(ax, x, y, w, h, text, fc=GREY, ec=GREY_E, fs=10.5, lw=1.3, bold=False, ls="-"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.015",
                                linewidth=lw, edgecolor=ec, facecolor=fc, linestyle=ls))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs, color=TEXT, fontweight="bold" if bold else "normal")


def arrow(ax, x1, y1, x2, y2, label=None, fs=8.5, color="#444444", lw=1.3,
          lx=None, ly=None, ha="center", va="bottom", ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=13, linewidth=lw, color=color, linestyle=ls))
    if label:
        ax.text(lx if lx is not None else (x1 + x2) / 2,
                ly if ly is not None else (y1 + y2) / 2 + 0.03,
                label, ha=ha, va=va, fontsize=fs, color="#333333")


def _canvas(w=9.0, h=5.0, xlim=(0, 10), ylim=(0, 6)):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axis("off")
    return fig, ax


def save(fig, name, title):
    fig.savefig(OUT / name, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", name)


def fig1_route():
    fig, ax = _canvas(w=9.2, h=4.8, ylim=(0, 5.2))
    ax.set_title("图1 论文总体技术路线与三项研究内容递进关系", fontsize=13, pad=12)
    box(ax, 0.4, 3.8, 2.8, 1.0, "研究内容一\n非连续时间策略确定性表示与编译", fc=BLUE, ec=BLUE_E, bold=True)
    box(ax, 3.8, 3.8, 2.8, 1.0, "研究内容二\n许可联盟链可信授权执行", fc=GREEN, ec=GREEN_E, bold=True)
    box(ax, 7.2, 3.8, 2.8, 1.0, "研究内容三\n版本化密文头部与前瞻性撤销", fc=ORANGE, ec=ORANGE_E, bold=True)
    box(ax, 0.4, 1.9, 2.8, 0.95, "语义输出\nI* / C(P) / 规范编码 B / 摘要 pd", fc=BLUE, ec=BLUE_E)
    box(ax, 3.8, 1.9, 2.8, 0.95, "状态输出\n资源/用户状态 / CAP2 / 共享 Nonce", fc=GREEN, ec=GREEN_E)
    box(ax, 7.2, 1.9, 2.8, 0.95, "对象输出\n版本化 Header / 任务状态 / 恢复对象", fc=ORANGE, ec=ORANGE_E)
    box(ax, 2.9, 0.2, 4.6, 0.85, "共享基础：半开区间时间语义 + 策略摘要 policyDigest", fc=PURPLE, ec=PURPLE_E, bold=True)
    arrow(ax, 3.2, 4.3, 3.8, 4.3, "摘要进入状态绑定", ly=4.52)
    arrow(ax, 6.6, 4.3, 7.2, 4.3, "状态驱动头部更新", ly=4.52)
    arrow(ax, 1.8, 3.8, 1.8, 2.85, "语义与编码", ly=3.32)
    arrow(ax, 5.2, 3.8, 5.2, 2.85, "可验证状态", ly=3.32)
    arrow(ax, 8.6, 3.8, 8.6, 2.85, "版本与恢复", ly=3.32)
    arrow(ax, 1.8, 1.9, 3.0, 1.2, "", ls="--")
    arrow(ax, 5.2, 1.9, 5.2, 1.15, "", ls="--")
    arrow(ax, 8.6, 1.9, 7.4, 1.2, "", ls="--")
    save(fig, "m4-fig1-route.png", "图1")


def fig2_compile():
    fig, ax = _canvas(w=8.8, h=4.4, ylim=(0, 5))
    ax.set_title("图3 非连续时间策略确定性编译流程", fontsize=13, pad=12)
    box(ax, 0.3, 3.9, 2.3, 0.8, "输入策略 P\n（任意书写形式）", fc=GREY, ec=GREY_E)
    box(ax, 3.0, 3.9, 2.1, 0.8, "时区归一化与离散化\nUTC(t0) / Δ / U", fc=BLUE, ec=BLUE_E)
    box(ax, 5.5, 3.9, 2.0, 0.8, "Normalize\n（排序 + 线性合并）", fc=BLUE, ec=BLUE_E)
    box(ax, 7.9, 3.9, 1.9, 0.8, "I* 规范区间序列\n（唯一语义表示）", fc=GREEN, ec=GREEN_E, bold=True)
    box(ax, 3.0, 2.3, 2.1, 0.8, "Cover\n（最大 2 幂对齐块）", fc=BLUE, ec=BLUE_E)
    box(ax, 5.5, 2.3, 2.0, 0.8, "C(P) 层次执行表示\n（可再生成）", fc=GREEN, ec=GREEN_E)
    box(ax, 7.9, 2.3, 1.9, 0.8, "NTP1 规范编码 B\n（固定宽度序列化）", fc=ORANGE, ec=ORANGE_E)
    box(ax, 5.5, 0.6, 2.0, 0.8, "pd = SHA-256(B)\n策略摘要", fc=PURPLE, ec=PURPLE_E, bold=True)
    box(ax, 2.3, 0.6, 2.5, 0.8, "验证：语义等价 + 性质测试\n15120 条正式记录", fc=GREY, ec=GREY_E, fs=9)
    arrow(ax, 2.6, 4.3, 3.0, 4.3)
    arrow(ax, 5.1, 4.3, 5.5, 4.3)
    arrow(ax, 7.5, 4.3, 7.9, 4.3)
    arrow(ax, 4.05, 3.9, 4.05, 3.1)
    arrow(ax, 6.5, 3.9, 6.5, 3.1)
    arrow(ax, 8.85, 3.9, 8.85, 3.1)
    arrow(ax, 6.5, 2.3, 6.5, 1.4)
    arrow(ax, 4.05, 2.3, 3.55, 1.4)
    arrow(ax, 6.5, 1.4, 6.5, 1.0, "", ls="--")
    save(fig, "m4-fig3-compile.png", "图3")


def fig3_ir():
    fig, ax = _canvas(w=8.4, h=3.8, ylim=(0, 4))
    ax.set_title("图2 语义主表示—摘要—派生执行 IR 关系", fontsize=13, pad=12)
    box(ax, 0.4, 1.6, 2.6, 1.1, "I* 语义主表示\n（唯一、规范、摘要基础）", fc=GREEN, ec=GREEN_E, bold=True)
    box(ax, 3.8, 1.6, 2.4, 1.1, "pd = SHA-256(Canonical(I*))\n策略摘要（链上绑定）", fc=PURPLE, ec=PURPLE_E, bold=True)
    box(ax, 7.0, 1.6, 2.6, 1.1, "C(P) 派生执行表示\n（可再生成，节点级接口）", fc=BLUE, ec=BLUE_E)
    box(ax, 2.4, 0.2, 5.4, 0.8, "摘要由语义表示决定，不随书写形式或执行表示变化", fc=GREY, ec=GREY_E, fs=9.5)
    arrow(ax, 3.0, 2.15, 3.8, 2.15, "确定性映射")
    arrow(ax, 6.2, 2.15, 7.0, 2.15, "编译可复现")
    arrow(ax, 5.0, 1.6, 5.0, 1.0, "表示层变化不引起摘要变化", ly=1.32, fs=8.5)
    save(fig, "m4-fig2-ir.png", "图2")


def fig4_arch():
    fig, ax = _canvas(w=9.4, h=5.8, ylim=(0, 6.4))
    ax.set_title("图4 许可联盟链可信授权系统总体架构", fontsize=13, pad=12)
    ax.add_patch(plt.Rectangle((0.15, 4.6), 9.7, 1.5, fill=True, fc=BLUE, ec=BLUE_E, lw=1.0, alpha=0.35))
    ax.text(0.35, 5.9, "许可联盟链（Besu QBFT）", fontsize=10, fontweight="bold", color=BLUE_E)
    box(ax, 0.5, 4.8, 1.8, 0.65, "Validator 1", fc="white", ec=BLUE_E)
    box(ax, 2.5, 4.8, 1.8, 0.65, "Validator 2", fc="white", ec=BLUE_E)
    box(ax, 4.5, 4.8, 1.8, 0.65, "Validator 3", fc="white", ec=BLUE_E)
    box(ax, 6.5, 4.8, 1.8, 0.65, "Validator 4", fc="white", ec=BLUE_E)
    box(ax, 8.5, 4.8, 1.5, 0.65, "RPC/客户端", fc=GREY, ec=GREY_E)
    box(ax, 0.5, 3.3, 2.7, 0.9, "AuthorizationState\n资源/用户状态 + policyDigest", fc=GREEN, ec=GREEN_E)
    box(ax, 3.7, 3.3, 2.7, 0.9, "HeaderRegistry\n版本 + 摘要登记", fc=GREEN, ec=GREEN_E)
    box(ax, 6.9, 3.3, 2.7, 0.9, "共享数据库 PostgreSQL\n跨实例原子 Nonce", fc=ORANGE, ec=ORANGE_E)
    box(ax, 0.5, 1.7, 2.7, 0.9, "Issuer 能力签发\n（初读/复读 + Ed25519）", fc=BLUE, ec=BLUE_E)
    box(ax, 3.7, 1.7, 2.7, 0.9, "Verifier 验证\n（逐项绑定复核）", fc=BLUE, ec=BLUE_E)
    box(ax, 6.9, 1.7, 2.7, 0.9, "材料释放判定\nAccessMaterialReleaseGuard", fc=RED, ec=RED_E)
    box(ax, 2.1, 0.3, 5.8, 0.85, "链下对象层：LocalObjectStore + Kubo 隔离副本（SHA-256 权威）", fc=PURPLE, ec=PURPLE_E, bold=True, fs=9.5)
    arrow(ax, 1.9, 4.8, 1.9, 4.2, "共识状态")
    arrow(ax, 5.4, 4.8, 5.4, 4.2, "共识状态")
    arrow(ax, 1.85, 3.3, 1.85, 2.6, "读取")
    arrow(ax, 5.05, 3.3, 5.05, 2.6, "读取/登记")
    arrow(ax, 8.25, 3.3, 8.25, 2.6, "原子消费")
    arrow(ax, 3.2, 2.15, 3.7, 2.15, "签发→验证")
    arrow(ax, 6.4, 2.15, 6.9, 2.15, "释放/拒绝", ls="--")
    save(fig, "m4-fig4-arch.png", "图4")


def fig5_cap2():
    fig, ax = _canvas(w=10.2, h=7.4, ylim=(0, 8))
    ax.set_title("图5 CAP2 能力签发与验证双泳道流程", fontsize=13, pad=12)
    ax.add_patch(plt.Rectangle((0.1, 0.4), 4.8, 6.7, fill=True, fc=BLUE, ec=BLUE_E, lw=1.0, alpha=0.25))
    ax.add_patch(plt.Rectangle((5.1, 0.4), 4.9, 6.7, fill=True, fc=GREEN, ec=GREEN_E, lw=1.0, alpha=0.25))
    ax.text(2.5, 6.9, "签发阶段（Issuer）", fontsize=11.5, ha="center", fontweight="bold", color=BLUE_E)
    ax.text(7.55, 6.9, "验证阶段（Verifier）", fontsize=11.5, ha="center", fontweight="bold", color=GREEN_E)
    steps_i = [
        (6.2, "请求：资源 + 用户 + 操作"),
        (5.2, "确认块初读：资源/用户状态"),
        (4.2, "校验 ACTIVE、policyDigest、时间窗口、公钥哈希"),
        (3.2, "签名前复读同一确认状态"),
        (2.2, "两次快照一致 → 规范化编码"),
        (1.2, "Ed25519 签名 → CAP2 能力"),
    ]
    steps_v = [
        (6.2, "解析规范编码 + 验签"),
        (5.2, "读取确认链上状态"),
        (4.2, "逐项绑定复核（链/合约/策略/epoch/版本/操作/时间）"),
        (3.2, "重新执行 I* 时间策略检查"),
        (2.2, "原子消费共享 Nonce"),
        (1.2, "全部通过 → ACCEPT；否则返回拒绝码"),
    ]
    for y, s in steps_i:
        box(ax, 0.35, y, 4.3, 0.72, s, fc="white", ec=BLUE_E, fs=9.5)
    for y, s in steps_v:
        box(ax, 5.4, y, 4.3, 0.72, s, fc="white", ec=GREEN_E, fs=9.5)
    for i in range(5):
        arrow(ax, 2.5, steps_i[i][0] - 0.02, 2.5, steps_i[i + 1][0] + 0.74)
        arrow(ax, 7.55, steps_v[i][0] - 0.02, 7.55, steps_v[i + 1][0] + 0.74)
    arrow(ax, 4.65, 1.56, 5.4, 1.56, "提交使用")
    arrow(ax, 2.5, 4.92, 2.5, 4.2, "状态变化则拒绝", ly=4.62, fs=8)
    save(fig, "m4-fig5-cap2.png", "图5")


def fig6_object():
    fig, ax = _canvas(w=9.0, h=4.6, ylim=(0, 5))
    ax.set_title("图6 版本化密文对象结构与生命周期关系", fontsize=13, pad=12)
    box(ax, 0.3, 3.9, 2.2, 0.8, "HeaderCore\n资源/版本/摘要/信封", fc=BLUE, ec=BLUE_E)
    box(ax, 3.0, 3.9, 2.2, 0.8, "SignedVersionedHeader\nJCS + Ed25519 签名", fc=BLUE, ec=BLUE_E)
    box(ax, 5.7, 3.9, 2.2, 0.8, "HeaderRegistry\n(hdrHash, objHash)", fc=GREEN, ec=GREEN_E)
    box(ax, 0.3, 2.4, 2.2, 0.8, "RecipientEnvelope\nHPKE 封装 CK", fc=ORANGE, ec=ORANGE_E)
    box(ax, 3.0, 2.4, 2.2, 0.8, "EncryptedCKRecord\n(接收者, EK_R)", fc=ORANGE, ec=ORANGE_E)
    box(ax, 5.7, 2.4, 2.2, 0.8, "Body\nAES-256-GCM 分块密文", fc=PURPLE, ec=PURPLE_E)
    box(ax, 0.3, 0.7, 7.6, 0.9, "版本三元组 (headerVersion, bodyVersion, keyVersion)：HEADER_ONLY 仅 h+1；BODY_ROTATION 三者均 +1", fc=GREY, ec=GREY_E, fs=9.5)
    arrow(ax, 2.5, 4.3, 3.0, 4.3, "序列化")
    arrow(ax, 5.2, 4.3, 5.7, 4.3, "摘要登记")
    arrow(ax, 1.4, 3.9, 1.4, 3.2, "逐接收者")
    arrow(ax, 4.1, 2.4, 4.1, 1.6, "内容密钥绑定", ly=1.9)
    save(fig, "m4-fig6-object.png", "图6")


def fig7_closure():
    fig, ax = _canvas(w=9.8, h=6.0, ylim=(0, 6.6))
    ax.set_title("图7 链上可信状态—控制协调—链下密文对象三层闭环架构", fontsize=13, pad=12)
    ax.add_patch(plt.Rectangle((0.12, 4.85), 9.76, 1.5, fill=True, fc=GREEN, ec=GREEN_E, lw=1.0, alpha=0.3))
    ax.text(0.32, 6.12, "① 链上可信状态层", fontsize=10.5, fontweight="bold", color=GREEN_E)
    box(ax, 0.5, 5.0, 2.8, 0.85, "AuthorizationState\n（资源/用户状态 + policyDigest）", fc="white", ec=GREEN_E, fs=9.5)
    box(ax, 3.7, 5.0, 2.8, 0.85, "HeaderRegistry\n（版本 + 摘要登记）", fc="white", ec=GREEN_E, fs=9.5)
    box(ax, 6.9, 5.0, 2.8, 0.85, "共享 Nonce 原子消费\n（PostgreSQL）", fc="white", ec=GREEN_E, fs=9.5)
    ax.add_patch(plt.Rectangle((0.12, 2.7), 9.76, 1.5, fill=True, fc=BLUE, ec=BLUE_E, lw=1.0, alpha=0.3))
    ax.text(0.32, 3.97, "② 控制协调层", fontsize=10.5, fontweight="bold", color=BLUE_E)
    box(ax, 0.5, 2.85, 2.8, 0.85, "数据库任务状态机\n（operationId 幂等）", fc="white", ec=BLUE_E, fs=9.5)
    box(ax, 3.7, 2.85, 2.8, 0.85, "材料释放判定\nAccessMaterialReleaseGuard", fc="white", ec=BLUE_E, fs=9.5)
    box(ax, 6.9, 2.85, 2.8, 0.85, "RecoveryCoordinator\n（摘要验证 + 原子恢复）", fc="white", ec=BLUE_E, fs=9.5)
    ax.add_patch(plt.Rectangle((0.12, 0.55), 9.76, 1.5, fill=True, fc=ORANGE, ec=ORANGE_E, lw=1.0, alpha=0.3))
    ax.text(0.32, 1.82, "③ 链下密文对象层", fontsize=10.5, fontweight="bold", color=ORANGE_E)
    box(ax, 0.5, 0.7, 4.3, 0.85, "LocalObjectStore\n（不可变对象，SHA-256 内容寻址）", fc="white", ec=ORANGE_E, fs=9.5)
    box(ax, 5.3, 0.7, 4.3, 0.85, "Kubo 隔离副本\n（CID 定位，不替代摘要权威）", fc="white", ec=ORANGE_E, fs=9.5)
    arrow(ax, 1.9, 5.0, 1.9, 3.7, "状态驱动任务", ly=4.4, fs=8.5)
    arrow(ax, 5.1, 5.0, 5.1, 3.7, "Header 更新意图", ly=4.4, fs=8.5)
    arrow(ax, 8.3, 2.85, 8.3, 1.55, "恢复候选/对象", ly=2.25, fs=8.5)
    arrow(ax, 2.65, 2.85, 2.65, 1.55, "释放判定/读取", ly=2.25, fs=8.5)
    arrow(ax, 4.8, 0.7, 4.6, 1.55, "", ls="--")
    arrow(ax, 9.6, 0.7, 9.6, 2.7, "恢复结果", ly=1.7, fs=8.5)
    save(fig, "m4-fig7-closure.png", "图7")


def main():
    fig1_route()
    fig2_compile()
    fig3_ir()
    fig4_arch()
    fig5_cap2()
    fig6_object()
    fig7_closure()
    print("all 7 M4 method figures written")


if __name__ == "__main__":
    main()
