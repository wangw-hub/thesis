# -*- coding: utf-8 -*-
"""M6: scan for residual artifacts (spacing, double terms, odd leftovers)."""
from __future__ import annotations

import io
import re
import sys
from pathlib import Path


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
M6 = ROOT / "docs/midterm-report/m6/M6-MIDTERM-SOURCE.md"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    t = io.open(M6, encoding="utf-8").read()
    patterns = [
        "能力凭证 能力", "能力凭证 采用", "能力凭证 以", "实现中称",
        "重跑 重跑", " 的 的", " 与 与", "（（", "））", "  。", "，  ",
        " 能力结构", "设计了 上下文", "撤销闭合 管理", "重注册后的正式重跑 重跑",
        "Issuer 执行", "Verifier 执行", " 运行 为", " 预实验 ",
    ]
    for pat in patterns:
        hits = [m.start() for m in re.finditer(re.escape(pat), t)]
        if hits:
            print(pat, "->", len(hits))
            for h in hits[:5]:
                print("   ", t[max(0, h - 40):h + 60].replace("\n", " "))
    # double spaces
    ds = re.findall(r"[^ ]  +[^ ]", t)
    print("double-space instances:", len(ds))
    # standalone english words in Chinese text that look like leftovers
    for w in ["REVOCATION", "INITIAL", "RESTORE", "CAP2", "HEADER", "BODY_ROTATION", "LOCAL", "KUBO"]:
        n = t.count(w)
        if n:
            print(w, n)


if __name__ == "__main__":
    main()
