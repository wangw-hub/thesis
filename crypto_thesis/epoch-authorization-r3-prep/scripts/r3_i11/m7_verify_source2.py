# -*- coding: utf-8 -*-
"""M7: plain-substring spot checks on the generated M7 source."""
from __future__ import annotations

import sys


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = r"D:\Research\crypto_thesis\epoch-authorization-r3-prep\docs\midterm-report\m7\M7-MIDTERM-SOURCE.md"
    s = open(p, encoding="utf-8").read()
    absent = [
        "release}\\Rightarrow status=ACTIVE",  # eq10 deleted
        "Header 存在且摘要一致",
        "Body 与 CK 不变",
        "新 CK 与新 Body",
        "撤销后的 Header 闭合",
        "Header 闭合前",
        "仅更新 Header",
        "旧 CK",
        "新 Body",
        "AuthorizationState",
        "HeaderRegistry",
        "AccessMaterialReleaseGuard",
        "LocalObjectStore",
        "RecoveryCoordinator",
        "operationId",
        "policyDigest",
        "天然的技术基础",
        "不可篡改账本",
        "中国, [P]",
        "已投稿",
        "已申请",
        "受理号",
        "申请号",
        "对齐上界 L=2",
        "cur ← []",
        "l ≤ cur.right 或 l = cur.right",
        "算法结束]",
        "算法结束]",
        "Header 更新",
        "Header 闭合",
        "Header 对象",
        "Header 版本",
    ]
    present = [
        "\\left\\{x\\in T\\mid l_i\\le x<r_i\\right\\}",
        "\\left(C(I)\\right)",
        "headerCoreDigest",
        "HPKE.Seal(pk_R,CK,\\operatorname{Info}(ctx),\\operatorname{AAD}(ctx))",
        "C_j=\\operatorname{AES\\text{-}256\\text{-}GCM}",
        "ReleaseAllowed(ctx)\\Rightarrow",
        "CandidateAcceptable(candidate)\\Leftrightarrow",
        "if P 为空 then",
        "if l ≤ cur.right then",
        "for 每个规范区间 I ∈ I* do",
        "算法6 仅密文头更新算法（HeaderOnlyUpdate）",
        "算法7 密文主体与密钥轮换算法（BodyRotation）",
        "[公式：(h,b,k)\\mapsto(h+1,b,k).]",
        "规范序列化[33]并以 Ed25519 签名",
        "性质测试方法[26]",
        "[14] Zhang Q",
        "[16] Ruan C",
        "[22] Li K",
        "[33] Rundgren",
        "阶段性学术论文：《基于许可联盟链状态锚定与共享 Nonce 的授权执行方法》。论文初稿已完成，拟投稿《软件学报》。",
        "拟申请发明专利：《一种非连续时间访问策略的确定性编译方法及系统》。专利文本撰写中。",
        "在不改变当前冻结实验结论的前提下开展必要的针对性补充验证",
        "多副本一致、可审计、可追溯的共享状态基础",
        "在仅依赖无状态离线令牌校验",
        "授权状态合约（AuthorizationState）",
        "密文头部注册合约（HeaderRegistry）",
        "材料释放判定模块（AccessMaterialReleaseGuard）",
        "本地不可变对象存储（LocalObjectStore）",
        "恢复协调器（RecoveryCoordinator）",
        "操作标识（operationId）",
        "策略摘要（policyDigest）",
        "密文头部核心摘要（headerCoreDigest）",
        "如式（13）、式（14）所示",
    ]
    print("--- absent (should all be absent) ---")
    for x in sorted(set(absent)):
        print(f"{'OK-absent' if x not in s else 'STILL-PRESENT'} | {x}")
    print("--- present (should all be present) ---")
    for x in sorted(set(present)):
        print(f"{'OK-present' if x in s else 'MISSING'} | {x}")


if __name__ == "__main__":
    main()
