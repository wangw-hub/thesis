"""I16: per-page PDF text audit (TOC, page breaks, glyph/placeholder issues)."""
from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
PDF = ROOT / "docs/final-manuscript/output/" / (sys.argv[1] if len(sys.argv) > 1 else "THESIS-FORMAT-CANDIDATE-V1.pdf")


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    import pypdfium2 as pdfium

    doc = pdfium.PdfDocument(str(PDF))
    n = len(doc)
    print("pages:", n)
    issues = []
    toc_page = None
    for i in range(n):
        page = doc[i]
        tp = page.get_textpage()
        text = (tp.get_text_range() or "").replace("\u00ad", "")
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        body = [ln for ln in lines if not re.fullmatch(r"[ivxlcdm]+|\d+", ln)]
        first = body[0][:70] if body else "(footer-only)"
        if not lines:
            issues.append(f"p{i}: EMPTY PAGE")
        if "\ufffd" in text or "□" in text:
            issues.append(f"p{i}: replacement glyphs")
        if "（目录将在打开文档或更新域后自动生成）" in text:
            issues.append(f"p{i}: TOC placeholder not populated")
        if "[图片缺失" in text:
            issues.append(f"p{i}: missing image marker")
        if "Traceback" in text or "Exception" in text:
            issues.append(f"p{i}: error text")
        if i == 1:
            print(f"p{i} [cover]: {first}")
        elif re.match(r"^第[一二三四五六七]章", first) or first in ("中文摘要", "Abstract", "参考文献", "附录A"):
            print(f"p{i} [chapter-start]: {first}")
        elif "目录" in text and "第一章" in text:
            toc_page = i
            print(f"p{i} [TOC page] first lines: {lines[:3]}")
        else:
            print(f"p{i}: {first[:80]}")
    print()
    print("TOC page:", toc_page)
    print("ISSUES:", issues if issues else "none")


if __name__ == "__main__":
    main()
