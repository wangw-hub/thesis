# -*- coding: utf-8 -*-
"""M7: dump MathML for union formula."""
from __future__ import annotations

import re
import sys

from latex2mathml.converter import convert as latex_to_mathml


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    v = r"\bigcup_{i=1}^{n}\{x\in T\mid l_i\le x<r_i\}"
    mathml = latex_to_mathml(v, display="block")
    print(mathml[:3000])
    print("---nary base check---")
    # find the munderover/underoveryet
    for tag in ["munderover", "munder", "mo"]:
        for m in re.finditer(rf"<{tag}[^>]*>.*?</{tag}>", mathml, re.S):
            print(m.group(0)[:300])
            print()


if __name__ == "__main__":
    main()
