# -*- coding: utf-8 -*-
"""M7: verify the generated M7 source (formula/algo/figure/table counts and key edits)."""
from __future__ import annotations

import re
import sys


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = r"D:\Research\crypto_thesis\epoch-authorization-r3-prep\docs\midterm-report\m7\M7-MIDTERM-SOURCE.md"
    s = open(p, encoding="utf-8").read()
    lines = s.split("\n")
    print("LEN:", len(s), "LINES:", len(lines))
    print("formulas:", len(re.findall(r"^\[公式：", s, re.M)))
    print("algorithms:", len(re.findall(r"^\[算法块：", s, re.M)))
    print("figures:", len(re.findall(r"^\[方法图：", s, re.M)))
    print("tables:", len(re.findall(r"^\[表：", s, re.M)))
    for i, ln in enumerate(lines, 1):
        if ln.startswith("[公式："):
            print(f"{i:03d}| {ln}")
    for i, ln in enumerate(lines, 1):
        if ln.startswith("[算法块："):
            print(f"{i:03d}| {ln[:95]}")

    # key edit spot checks
    checks = {
        "eq1 left brace": r"\\left\\{x\\in T",
        "eq3 left paren": r"\\left\(C\(I\)\\right\)",
        "eq10 deleted": r"release}\\\\Rightarrow status=ACTIVE",
        "header digest": r"headerCoreDigest",
        "hpke context": r"HPKE\.Seal\(pk_R,CK,\\operatorname\{Info\}",
        "chunk formula": r"C_j=\\operatorname\{AES",
        "release predicate": r"ReleaseAllowed\(ctx\)\\Rightarrow",
        "restore predicate": r"CandidateAcceptable",
        "algo1 empty": r"if P 为空 then",
        "algo1 merged": r"if l ≤ cur\.right then",
        "algo2 no L": r"对齐上界 L=2",
        "algo3 loop": r"for 每个规范区间 I ∈ I\* do",
        "algo6 title": r"算法6 仅密文头更新算法（HeaderOnlyUpdate）",
        "algo7 title": r"算法7 密文主体与密钥轮换算法（BodyRotation）",
        "version formula first": r"\[公式：\(h,b,k\)\\mapsto\(h\+1,b,k\)\.\]",
        "jcs rc3": r"规范序列化\[33\]",
        "quickcheck": r"性质测试方法\[26\]",
        "zhang ref": r"\[14\] Zhang Q",
        "ruan ref": r"\[16\] Ruan C",
        "zhan ref": r"\[22\] Li K",
        "jcs ref": r"\[33\] Rundgren",
        "stage paper": r"阶段性学术论文",
        "stage patent": r"拟申请发明专利",
        "no 中国[P]": r"中国, \[P\]",
        "problem2 softened": r"在不改变当前冻结实验结论的前提下开展必要的针对性补充验证",
        "blockchain claim": r"多副本一致、可审计、可追溯的共享状态基础",
        "oauth qualifier": r"在仅依赖无状态离线令牌校验",
        "no 天然": r"天然的技术基础",
        "no 不可篡改账本": r"不可篡改账本",
    }
    print("\n--- spot checks ---")
    for name, pat in checks.items():
        found = bool(re.search(pat, s, re.S))
        print(f"{'OK ' if found else 'MISS'} | {name}")


if __name__ == "__main__":
    main()
