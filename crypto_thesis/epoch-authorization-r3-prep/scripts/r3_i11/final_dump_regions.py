# -*- coding: utf-8 -*-
"""Dump M7 source regions relevant to the FINAL-CLEAN edits."""
from __future__ import annotations

import io
import sys


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = r"D:\Research\crypto_thesis\epoch-authorization-r3-prep\docs\midterm-report\m7\M7-MIDTERM-SOURCE.md"
    s = io.open(p, encoding="utf-8").read()
    lines = s.split("\n")
    # Print full lines matching any of these anchors (line-numbered)
    anchors = [
        "访问控制列表",
        "普通令牌通常只包含",
        "即五元组",
        "冗余度",
        "operatorname{Ed25519.Sign}",
        "operatorname{Encode}",
        "数据库控制面",
        "共同保证系统",
        "从计划管理角度看",
        "论文初稿围绕",
        "公开账本",
        "公开事实源",
        "公开状态",
        "阶段性学术论文",
        "同一确认区块",
        "确认区块读取",
        "SHA-256 内容寻址为完整性权威",
        "Kubo 仅作为隔离副本定位",
        "版本状态机由",
        "算法2 二进制",
        "算法4 上下文",
        "算法6 仅密文头",
        "算法8 对象恢复",
        "仅依靠",
        "为授权状态提供",
        "许可联盟链作为授权状态",
        "共同保证系统在正常路径",
    ]
    for i, ln in enumerate(lines, 1):
        for a in anchors:
            if a in ln:
                print(f"{i:03d}| {ln}")
                break


if __name__ == "__main__":
    main()
