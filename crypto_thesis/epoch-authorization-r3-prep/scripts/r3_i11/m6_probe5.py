# -*- coding: utf-8 -*-
"""M6: check citation anchors and leftover issues in M6 source."""
from __future__ import annotations

import io
import re
import sys
from pathlib import Path


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
SRC = ROOT / "docs/midterm-report/m6/M6-MIDTERM-SOURCE.md"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    t = io.open(SRC, encoding="utf-8").read()
    body = t[: t.find("### 参考文献")]
    print("=== remaining single-digit-old citations (anchors with following char check) ===")
    for m in re.finditer(r"\[(\d+)\]", body):
        n = int(m.group(1))
        ctx = body[max(0, m.start() - 30):m.end() + 30].replace("\n", " ")
        print(n, "|", ctx)
    print()
    print("=== table markers ===")
    for m in re.finditer(r"\[表：([^\]]+)\]", body):
        print(repr(m.group(1)))
    print()
    print("=== duplicate E4/E5 paragraph count ===")
    print(body.count("撤销窗口实验覆盖撤销后的"))
    print()
    print("=== CAP2 mentions ===")
    print("CAP2:", t.count("CAP2"))
    print()
    print("=== spacing artifacts ===")
    for pat in [" 与 ", " 的 ", " 为 ", " 在 ", " 运行 ", " 预实验 ", " 能力凭证 ", " 初始发布 ", " 撤销闭合 ", " 副本恢复 ", " 仅本地对象 ", " 隔离副本 ", " 密文主体与密钥轮换 ", " 仅密文头更新 "]:
        hits = [m.start() for m in re.finditer(re.escape(pat), t)]
        if hits:
            print(pat, "->", len(hits), "hits; first ctx:", t[max(0, hits[0]-30):hits[0]+40].replace("\n", " "))


if __name__ == "__main__":
    main()
