# -*- coding: utf-8 -*-
"""M6: test latex2mathml -> OMML conversion for candidate display equations."""
from __future__ import annotations

import copy
import sys
from pathlib import Path

from lxml import etree
from latex2mathml.converter import convert as latex_to_mathml


MML_XSL = r"C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    eqs = {
        1: r"S(P)=\bigcup_{i=1}^{n}\{x\in T\mid l_i\le x<r_i\}",
        2: r"I^*=\operatorname{Normalize}(P)=\langle[a_1,b_1),\ldots,[a_k,b_k)\rangle",
        3: r"C(P)=\bigcup_{I\in I^*}C(I),\qquad c=|C(P)|",
        4: r"pd=\operatorname{SHA\text{-}256}(B(P))",
        5: r"T(n,c)=O(n\log n+c)",
        6: r"B(P)=\operatorname{CanonicalSerialize}(t_0,\Delta,U,I^*)",
        7: r"\sigma=\operatorname{Ed25519.Sign}(sk_I,B)",
        8: r"B=\operatorname{Encode}_{CAP2}(F_1\Vert F_2\Vert\cdots\Vert F_n)",
        9: r"\text{INSERT}(k)=1\Leftrightarrow k\notin consumed,\quad k=(chain,contract,resource,epoch,nonce)",
        10: r"release\Rightarrow status=ACTIVE\wedge dbAvailable",
        11: r"hdrHash=\operatorname{SHA\text{-}256}(\operatorname{Canonical}(Header)),\quad HeaderRegistry\gets(hdrHash,objHash)",
        12: r"EK_R=\operatorname{HPKE.Seal}(pk_R,CK)",
        13: r"C_{body}=\operatorname{AES\text{-}256\text{-}GCM}(K,N,M)",
        14: r"(h,b,k)\mapsto(h+1,b+1,k+1)",
        15: r"(h,b,k)\mapsto(h+1,b,k)",
        16: r"release\Leftrightarrow status=ACTIVE\wedge t\in S(I^*)\wedge hdrValid",
        17: r"restore\Leftrightarrow \operatorname{SHA\text{-}256}(candidate)=objHash\wedge structuralValid",
    }
    xsl = etree.XSLT(etree.parse(MML_XSL))
    ok = True
    for n, latex in eqs.items():
        try:
            mathml = latex_to_mathml(latex, display="block")
            tree = etree.fromstring(mathml.encode("utf-8"))
            res = xsl(tree)
            root = res.getroot()
            xml = etree.tostring(root, encoding="unicode")
            bad = [tok for tok in ("w:placeholder", "MISSING", "NaN", "\ufffd", "□") if tok in xml]
            if bad:
                print(f"EQ {n}: SUSPECT {bad}")
                ok = False
            else:
                print(f"EQ {n}: OK ({len(xml)} chars)")
        except Exception as exc:
            print(f"EQ {n}: ERROR {exc}")
            ok = False
    print("ALL OK" if ok else "HAS ISSUES")


if __name__ == "__main__":
    main()
