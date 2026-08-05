# -*- coding: utf-8 -*-
"""M3: seven grayscale academic method/architecture figures (no new mechanisms)."""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


OUT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep\docs\midterm-report\m3\figures")
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False

BLACK = "#111111"
GRAY = "#555555"
F_LIGHT = "#f2f2f2"
F_MID = "#dcdcdc"
F_DARK = "#b8b8b8"
F_NONE = "#ffffff"


def box(ax, x, y, w, h, text, fc=F_NONE, ec=BLACK, fs=10.5, lw=1.2, ls="-", bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.015",
                                linewidth=lw, edgecolor=ec, facecolor=fc, linestyle=ls))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs, color=BLACK, fontweight="bold" if bold else "normal")


def arrow(ax, x1, y1, x2, y2, label=None, fs=8.5, lx=None, ly=None, ha="center", va="bottom",
          ls="-", color=BLACK, lw=1.2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=12, linewidth=lw, color=color, linestyle=ls))
    if label:
        ax.text(lx if lx is not None else (x1 + x2) / 2,
                ly if ly is not None else (y1 + y2) / 2 + 0.03,
                label, ha=ha, va=va, fontsize=fs, color=GRAY)


def _canvas(w=9.0, h=5.2, xlim=(0, 10), ylim=(0, 6)):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axis("off")
    return fig, ax


def save(fig, name, title):
    fig.savefig(OUT / name, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", name, "|", title)


def fig1_route() -> None:
    fig, ax = _canvas(w=9.0, h=4.6, ylim=(0, 5))
    ax.set_title("图1 论文总体技术路线与三项研究内容递进关系", fontsize=12, pad=10)
    box(ax, 0.5, 3.6, 2.7, 1.0, "研究内容一\n非连续时间策略确定性表示与编译", fc=F_LIGHT, bold=True)
    box(ax, 3.9, 3.6, 2.7, 1.0, "研究内容二\n许可联盟链状态锚定的可信授权执行", fc=F_MID, bold=True)
    box(ax, 7.3, 3.6, 2.7, 1.0, "研究内容三\n版本化密文头部与前瞻性撤销闭环", fc=F_DARK, bold=True)
    box(ax, 0.5, 1.7, 2.7, 0.9, "输出：I*、C(P)、\n规范编码 B 与摘要 pd", fc=F_NONE)
    box(ax, 3.9, 1.7, 2.7, 0.9, "输出：资源/用户状态、\nCAP2 能力与共享 Nonce", fc=F_NONE)
    box(ax, 7.3, 1.7, 2.7, 0.9, "输出：版本化 Header、\n任务状态与恢复对象", fc=F_NONE)
    box(ax, 3.2, 0.2, 4.6, 0.9, "共享基础：半开区间时间语义 + 策略摘要（policyDigest）", fc=F_LIGHT)
    arrow(ax, 3.2, 4.1, 3.9, 4.1, "摘要进入状态绑定", ly=4.22)
    arrow(ax, 6.6, 4.1, 7.3, 4.1, "状态驱动头部更新", ly=4.22)
    arrow(ax, 1.85, 3.6, 1.85, 2.6, "语义与编码", ly=3.05)
    arrow(ax, 5.25, 3.6, 5.25, 2.6, "可验证状态", ly=3.05)
    arrow(ax, 8.65, 3.6, 8.65, 2.6, "版本与恢复", ly=3.05)
    arrow(ax, 1.85, 1.7, 3.0, 1.1, "", ls="--")
    arrow(ax, 5.25, 1.7, 5.25, 1.1, "", ls="--")
    arrow(ax, 8.65, 1.7, 7.15, 1.1, "", ls="--")
    save(fig, "m3-fig1-technical-route.png", "图1 总体技术路线")


def fig2_compile() -> None:
    fig, ax = _canvas(w=8.6, h=4.4, ylim=(0, 5))
    ax.set_title("图2 非连续时间策略确定性编译流程", fontsize=12, pad=10)
    box(ax, 0.3, 3.9, 2.3, 0.8, "输入策略 P\n（任意书写形式）", fc=F_LIGHT)
    box(ax, 3.0, 3.9, 2.0, 0.8, "时区归一化\nUTC 起点 t0 / Δ / U", fc=F_NONE)
    box(ax, 5.4, 3.9, 2.0, 0.8, "Normalize\n（排序 + 线性合并）", fc=F_NONE)
    box(ax, 7.8, 3.9, 1.9, 0.8, "I* 规范区间序列\n（唯一语义表示）", fc=F_LIGHT)
    box(ax, 3.0, 2.4, 2.0, 0.8, "Cover\n（最大对齐块）", fc=F_NONE)
    box(ax, 5.4, 2.4, 2.0, 0.8, "C(P) 层次执行表示\n（可再生成）", fc=F_LIGHT)
    box(ax, 7.8, 2.4, 1.9, 0.8, "NTP1 规范编码 B\n（固定头部 + 区间列表）", fc=F_NONE)
    box(ax, 5.4, 0.7, 2.0, 0.8, "pd = SHA256(B)\n策略摘要", fc=F_DARK, bold=True)
    box(ax, 2.4, 0.7, 2.4, 0.8, "验证：语义等价\n性质测试 + 15120 条记录", fc=F_NONE, fs=9)
    arrow(ax, 2.6, 4.3, 3.0, 4.3)
    arrow(ax, 5.0, 4.3, 5.4, 4.3)
    arrow(ax, 7.4, 4.3, 7.8, 4.3)
    arrow(ax, 4.0, 3.9, 4.0, 3.2)
    arrow(ax, 6.4, 3.9, 6.4, 3.2)
    arrow(ax, 8.75, 3.9, 8.75, 3.2)
    arrow(ax, 6.4, 2.4, 6.4, 1.5)
    arrow(ax, 4.0, 2.4, 3.6, 1.5)
    arrow(ax, 8.0, 0.7, 7.4, 0.7)
    save(fig, "m3-fig2-compile-flow.png", "图2 编译流程")


def fig3_ir_relation() -> None:
    fig, ax = _canvas(w=8.2, h=3.8, ylim=(0, 4))
    ax.set_title("图3 语义主表示—摘要—派生执行 IR 关系", fontsize=12, pad=10)
    box(ax, 0.4, 1.5, 2.6, 1.1, "I* 语义主表示\n（唯一、规范）", fc=F_LIGHT, bold=True)
    box(ax, 3.8, 1.5, 2.4, 1.1, "pd = SHA256(Canonical(I*))\n（策略标识）", fc=F_MID)
    box(ax, 7.0, 1.5, 2.6, 1.1, "C(P) 派生执行表示\n（可再生成）", fc=F_NONE)
    box(ax, 2.4, 0.2, 5.2, 0.8, "摘要由语义表示决定，不随书写形式/执行表示变化", fc=F_LIGHT, fs=9.5)
    arrow(ax, 3.0, 2.05, 3.8, 2.05, "确定性映射")
    arrow(ax, 6.2, 2.05, 7.0, 2.05, "编译可复现")
    arrow(ax, 5.0, 1.5, 5.0, 1.0, "表示层变化不引起摘要变化", ly=1.28, fs=8.5)
    save(fig, "m3-fig3-ir-relation.png", "图3 IR 关系")


def fig4_arch() -> None:
    fig, ax = _canvas(w=9.2, h=5.6, ylim=(0, 6.2))
    ax.set_title("图4 许可联盟链可信授权系统总体架构", fontsize=12, pad=10)
    ax.add_patch(plt.Rectangle((0.2, 4.5), 9.4, 1.4, fill=False, ec=BLACK, lw=1.0, ls="--"))
    ax.text(0.35, 5.72, "许可联盟链（Besu QBFT）：四 Validator + 一 RPC/客户端节点", fontsize=9, color=GRAY)
    box(ax, 0.5, 4.7, 1.7, 0.6, "Validator 1", fc=F_NONE)
    box(ax, 2.4, 4.7, 1.7, 0.6, "Validator 2", fc=F_NONE)
    box(ax, 4.3, 4.7, 1.7, 0.6, "Validator 3", fc=F_NONE)
    box(ax, 6.2, 4.7, 1.7, 0.6, "Validator 4", fc=F_NONE)
    box(ax, 8.1, 4.7, 1.7, 0.6, "RPC / 客户端", fc=F_LIGHT)
    box(ax, 0.5, 3.3, 2.6, 0.9, "AuthorizationState\n资源/用户状态 + policyDigest", fc=F_MID)
    box(ax, 3.6, 3.3, 2.6, 0.9, "HeaderRegistry\n版本 + 摘要登记", fc=F_MID)
    box(ax, 6.7, 3.3, 2.6, 0.9, "共享数据库 PostgreSQL\n跨实例原子 Nonce", fc=F_LIGHT)
    box(ax, 0.5, 1.7, 2.6, 0.9, "Issuer 能力签发\n（初读/复读 + Ed25519）", fc=F_NONE)
    box(ax, 3.6, 1.7, 2.6, 0.9, "Verifier 验证\n（逐项绑定复核）", fc=F_NONE)
    box(ax, 6.7, 1.7, 2.6, 0.9, "材料释放判定\nAccessMaterialReleaseGuard", fc=F_NONE)
    box(ax, 2.1, 0.3, 5.8, 0.9, "链下对象层：LocalObjectStore + Kubo 隔离副本（SHA-256 权威）", fc=F_LIGHT, bold=True)
    arrow(ax, 1.85, 4.7, 1.85, 4.2, "共识状态")
    arrow(ax, 4.9, 4.7, 4.9, 4.2, "共识状态")
    arrow(ax, 1.8, 3.3, 1.8, 2.6, "读取状态")
    arrow(ax, 4.9, 3.3, 4.9, 2.6, "读取/登记")
    arrow(ax, 8.0, 3.3, 8.0, 2.6, "原子消费")
    arrow(ax, 3.3, 2.15, 6.7, 2.15, "签发→验证")
    arrow(ax, 6.0, 1.7, 7.3, 1.2, "释放/拒绝", ls="--")
    save(fig, "m3-fig4-arch.png", "图4 系统总体架构")


def fig5_cap2_swimlane() -> None:
    fig, ax = _canvas(w=10.0, h=7.2, ylim=(0, 8))
    ax.set_title("图5 CAP2 签发与验证双泳道流程", fontsize=12, pad=10)
    ax.add_patch(plt.Rectangle((0.1, 0.4), 4.7, 6.6, fill=True, fc="#f7f7f7", ec=BLACK, lw=1.0))
    ax.add_patch(plt.Rectangle((5.0, 0.4), 4.8, 6.6, fill=True, fc="#efefef", ec=BLACK, lw=1.0))
    ax.text(2.45, 6.8, "签发阶段（Issuer）", fontsize=11, ha="center", fontweight="bold")
    ax.text(7.4, 6.8, "验证阶段（Verifier）", fontsize=11, ha="center", fontweight="bold")
    steps_i = [
        (6.15, "请求：资源 + 用户 + 操作"),
        (5.15, "确认块初读：资源/用户状态"),
        (4.15, "校验 ACTIVE、policyDigest、\n时间窗口、公钥哈希"),
        (3.15, "签名前复读同一确认状态"),
        (2.15, "两次快照一致"),
        (1.15, "规范化编码 + Ed25519 签名\n→ CAP2 能力"),
    ]
    steps_v = [
        (6.15, "解析规范编码 + 验签"),
        (5.15, "读取确认链上状态"),
        (4.15, "逐项绑定复核：链/合约/策略/\nepoch/版本/操作/时间"),
        (3.15, "重新执行 I* 时间策略检查"),
        (2.15, "原子消费共享 Nonce"),
        (1.15, "全部通过 → ACCEPT\n任一失败 → 对应拒绝码"),
    ]
    for y, s in steps_i:
        box(ax, 0.35, y, 4.2, 0.72, s, fc=F_NONE, fs=9.5)
    for y, s in steps_v:
        box(ax, 5.25, y, 4.2, 0.72, s, fc=F_NONE, fs=9.5)
    for i in range(5):
        arrow(ax, 2.45, steps_i[i][0] - 0.02, 2.45, steps_i[i + 1][0] + 0.74)
        arrow(ax, 7.35, steps_v[i][0] - 0.02, 7.35, steps_v[i + 1][0] + 0.74)
    arrow(ax, 4.55, 1.51, 5.25, 1.51, "提交使用")
    arrow(ax, 2.45, 4.87, 2.45, 4.2, "状态变化？拒绝", ly=4.6, fs=8)
    save(fig, "m3-fig5-cap2-swimlane.png", "图5 CAP2 双泳道")


def fig6_object_structure() -> None:
    fig, ax = _canvas(w=8.8, h=4.6, ylim=(0, 5))
    ax.set_title("图6 版本化密文对象结构（Header / Body / CK）", fontsize=12, pad=10)
    box(ax, 0.3, 3.9, 2.2, 0.8, "HeaderCore\n资源/版本/摘要/信封", fc=F_LIGHT)
    box(ax, 3.0, 3.9, 2.2, 0.8, "SignedVersionedHeader\nJCS + Ed25519 签名", fc=F_MID)
    box(ax, 5.7, 3.9, 2.2, 0.8, "HeaderRegistry\n(hdrHash, objHash)", fc=F_DARK)
    box(ax, 0.3, 2.4, 2.2, 0.8, "RecipientEnvelope\nHPKE 封装 CK", fc=F_NONE)
    box(ax, 3.0, 2.4, 2.2, 0.8, "EncryptedCKRecord\n(接收者, EK_R)", fc=F_NONE)
    box(ax, 5.7, 2.4, 2.2, 0.8, "Body\nAES-256-GCM 分块密文", fc=F_LIGHT)
    box(ax, 0.3, 0.7, 7.6, 0.9, "版本三元组 (headerVersion, bodyVersion, keyVersion)：HEADER_ONLY 仅 h+1；BODY_ROTATION 三者均 +1", fc=F_LIGHT, fs=9.5)
    arrow(ax, 2.5, 4.3, 3.0, 4.3, "序列化")
    arrow(ax, 5.2, 4.3, 5.7, 4.3, "摘要登记")
    arrow(ax, 1.4, 3.9, 1.4, 3.2, "逐接收者")
    arrow(ax, 4.1, 2.4, 4.1, 1.6, "内容密钥绑定", ly=1.9)
    save(fig, "m3-fig6-object-structure.png", "图6 密文对象结构")


def fig7_three_layer() -> None:
    fig, ax = _canvas(w=9.6, h=5.8, ylim=(0, 6.4))
    ax.set_title("图7 链上可信状态—控制协调—链下密文对象三层闭环架构", fontsize=12, pad=10)
    ax.add_patch(plt.Rectangle((0.15, 4.7), 9.5, 1.45, fill=True, fc="#f2f2f2", ec=BLACK, lw=1.0))
    ax.text(0.35, 5.92, "① 链上可信状态层", fontsize=10, fontweight="bold")
    box(ax, 0.5, 4.85, 2.7, 0.8, "AuthorizationState\n（资源/用户状态 + policyDigest）", fc=F_NONE, fs=9.5)
    box(ax, 3.6, 4.85, 2.7, 0.8, "HeaderRegistry\n（版本 + 摘要登记）", fc=F_NONE, fs=9.5)
    box(ax, 6.7, 4.85, 2.7, 0.8, "共享 Nonce 原子消费\n（PostgreSQL）", fc=F_NONE, fs=9.5)
    ax.add_patch(plt.Rectangle((0.15, 2.6), 9.5, 1.45, fill=True, fc="#e6e6e6", ec=BLACK, lw=1.0))
    ax.text(0.35, 3.82, "② 控制协调层", fontsize=10, fontweight="bold")
    box(ax, 0.5, 2.75, 2.7, 0.8, "数据库任务状态机\n（operationId 幂等）", fc=F_NONE, fs=9.5)
    box(ax, 3.6, 2.75, 2.7, 0.8, "材料释放判定\nAccessMaterialReleaseGuard", fc=F_NONE, fs=9.5)
    box(ax, 6.7, 2.75, 2.7, 0.8, "RecoveryCoordinator\n（摘要验证 + 原子恢复）", fc=F_NONE, fs=9.5)
    ax.add_patch(plt.Rectangle((0.15, 0.5), 9.5, 1.45, fill=True, fc="#d9d9d9", ec=BLACK, lw=1.0))
    ax.text(0.35, 1.72, "③ 链下密文对象层", fontsize=10, fontweight="bold")
    box(ax, 0.5, 0.65, 4.2, 0.8, "LocalObjectStore\n（不可变对象，SHA-256 内容寻址）", fc=F_NONE, fs=9.5)
    box(ax, 5.2, 0.65, 4.2, 0.8, "Kubo 隔离副本\n（CID 定位，不替代摘要权威）", fc=F_NONE, fs=9.5)
    arrow(ax, 1.85, 4.85, 1.85, 3.55, "状态驱动任务", ly=4.25, fs=8.5)
    arrow(ax, 4.95, 4.85, 4.95, 3.55, "Header 更新意图", ly=4.25, fs=8.5)
    arrow(ax, 7.9, 2.75, 7.9, 1.45, "恢复候选/对象", ly=2.15, fs=8.5)
    arrow(ax, 2.6, 2.75, 2.6, 1.45, "释放判定/读取", ly=2.15, fs=8.5)
    arrow(ax, 5.2, 0.65, 4.6, 1.45, "", ls="--")
    arrow(ax, 9.4, 0.65, 9.4, 2.6, "恢复结果", ly=1.6, fs=8.5)
    save(fig, "m3-fig7-three-layer-closure.png", "图7 三层闭环架构")


def main() -> None:
    fig1_route()
    fig2_compile()
    fig3_ir_relation()
    fig4_arch()
    fig5_cap2_swimlane()
    fig6_object_structure()
    fig7_three_layer()
    print("all 7 method figures written to", OUT)


if __name__ == "__main__":
    main()
