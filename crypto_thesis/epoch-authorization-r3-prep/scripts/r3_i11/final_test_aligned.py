# -*- coding: utf-8 -*-
"""Test latex2mathml aligned/eqarray variants for formula (10)."""
from __future__ import annotations

import re
import sys

from lxml import etree
from latex2mathml.converter import convert as latex_to_mathml


MML_XSL = r"C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    variants = {
        "aligned1": r"\begin{aligned}\operatorname{headerCoreDigest}&=\operatorname{SHA\text{-}256}(D_H\Vert\operatorname{JCS}(HeaderCore))\\ \operatorname{headerObjectDigest}&=\operatorname{SHA\text{-}256}(signedHeader)\end{aligned}",
        "aligned2": r"\begin{aligned}a&=b\\ c&=d\end{aligned}",
        "array": r"\begin{array}{l}\operatorname{headerCoreDigest}=\operatorname{SHA\text{-}256}(D_H\Vert\operatorname{JCS}(HeaderCore))\\ \operatorname{headerObjectDigest}=\operatorname{SHA\text{-}256}(signedHeader)\end{array}",
    }
    xsl = etree.XSLT(etree.parse(MML_XSL))
    for name, latex in variants.items():
        try:
            mathml = latex_to_mathml(latex, display="block")
            tree = etree.fromstring(mathml.encode("utf-8"))
            res = xsl(tree)
            xml = etree.tostring(res.getroot(), encoding="unicode")
            has_m_e = "<m:e/>" in xml
            has_m = "<m:m>" in xml or "<m:eqArr>" in xml
            print(f"{name}: ok, empty_m_e={has_m_e}, matrix/eqarr={has_m}, len={len(xml)}")
            if "<m:eqArr>" in xml or "<m:m>" in xml:
                idx = xml.find("<m:eqArr>") if "<m:eqArr>" in xml else xml.find("<m:m>")
                print("   ...", xml[max(0, idx - 80): idx + 260])
        except Exception as exc:
            print(name, "ERR", exc)


if __name__ == "__main__":
    main()
