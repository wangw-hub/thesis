# -*- coding: utf-8 -*-
"""M7: test latex2mathml variants for union formulas (empty nary base issue)."""
from __future__ import annotations

import re
import sys

from latex2mathml.converter import convert as latex_to_mathml


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    variants = [
        r"\bigcup_{i=1}^{n}\{x\in T\mid l_i\le x<r_i\}",
        r"\bigcup_{i=1}^{n}{\{x\in T\mid l_i\le x<r_i\}}",
        r"\bigcup_{i=1}^{n}(\{x\in T\mid l_i\le x<r_i\})",
        r"\bigcup_{i=1}^{n}\left(\{x\in T\mid l_i\le x<r_i\}\right)",
        r"\mathop{\bigcup}\limits_{i=1}^{n}\{x\in T\mid l_i\le x<r_i\}",
        r"\bigcup_{i=1}^{n}S(P,i)",
        r"\bigcup_{I\in I^*}C(I)",
        r"\bigcup_{I\in I^*}\left(C(I)\right)",
    ]
    for v in variants:
        try:
            mathml = latex_to_mathml(v, display="block")
            has_empty_nary = re.search(r"<m:oMath[^>]*>(?:(?!</m:oMath>).)*?<m:nary>(?:(?!</m:nary>).)*?<m:e/>", mathml, re.S) is not None
            # simpler: check nary with empty base
            m = re.search(r"<m:nary>(.*?)</m:nary>", mathml, re.S)
            empty = False
            if m:
                inner = m.group(1)
                empty = "<m:e/>" in inner and "<m:e><" not in inner.replace("<m:e/>", "")
            print(f"{'EMPTY' if empty else 'ok   '} | {v[:70]}")
            if empty:
                print("     nary inner:", re.sub(r"\s+", " ", m.group(1))[:160])
        except Exception as exc:
            print("ERR |", v, exc)


if __name__ == "__main__":
    main()
