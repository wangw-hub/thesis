"""I16: render DOCX -> PDF via Word COM, then pages -> PNG contact sheets."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PIL import Image


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
OUT = ROOT / "docs/final-manuscript/output"
STEM = sys.argv[2] if len(sys.argv) > 2 else "THESIS-FORMAT-CANDIDATE-V1"
DOCX = OUT / f"{STEM}.docx"
PDF = OUT / f"{STEM}.pdf"
PNGDIR = ROOT / "docs/final-manuscript/qa/pages"
PROBE = ROOT / "docs/final-manuscript/qa/contact-sheets"


def docx_to_pdf() -> None:
    import win32com.client

    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        d = word.Documents.Open(str(DOCX), ReadOnly=False)
        try:
            d.Fields.Update()
        except Exception:
            pass
        try:
            for toc in d.TablesOfContents:
                toc.Update()
        except Exception:
            pass
        d.Repaginate()
        d.Save()
        d.ExportAsFixedFormat(str(PDF), 17)
        pages = d.ComputeStatistics(2)  # wdStatisticPages
        d.Close(False)
        print("PDF pages:", pages)
    finally:
        word.Quit()


def pdf_to_pngs() -> None:
    PNGDIR.mkdir(parents=True, exist_ok=True)
    pdftoppm = Path(r"C:\Users\wangw\.cache\codex-runtimes\codex-primary-runtime\dependencies\bin\fallback\pdftoppm.cmd")
    try:
        subprocess.run([str(pdftoppm), "-png", "-r", "90", str(PDF), str(PNGDIR / "page")], check=True)
    except Exception:
        helper = ROOT / "scripts/r3_i11/render_pages_pdfium.py"
        helper.write_text(
            "import pypdfium2 as pdfium, sys, pathlib\n"
            "pdf = pathlib.Path(sys.argv[1])\n"
            "outdir = pathlib.Path(sys.argv[2])\n"
            "doc = pdfium.PdfDocument(str(pdf))\n"
            "scale = 90 / 72.0\n"
            "for i in range(len(doc)):\n"
            "    page = doc[i]\n"
            "    img = page.render(scale=scale).to_pil()\n"
            "    img.save(outdir / ('page-%03d.png' % (i + 1)))\n"
            "print('pages', len(doc))\n",
            encoding="utf-8")
        bundle = Path(r"C:\Users\wangw\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe")
        subprocess.run([str(bundle), str(helper), str(PDF), str(PNGDIR)], check=True)
    files = sorted(PNGDIR.glob("page-*.png"))
    print("rendered pages:", len(files))


def contact_sheets(pages_per=4) -> None:
    PROBE.mkdir(parents=True, exist_ok=True)
    files = sorted(PNGDIR.glob("page-*.png"))
    for si, start in enumerate(range(0, len(files), pages_per), 1):
        batch = files[start:start + pages_per]
        imgs = [Image.open(f) for f in batch]
        w, h = imgs[0].size
        canvas = Image.new("RGB", (w * 2, h * 2), "white")
        for idx, im in enumerate(imgs):
            canvas.paste(im, ((idx % 2) * w, (idx // 2) * h))
        out = PROBE / f"sheet-{si:02d}.png"
        canvas.save(out)
        print(out, [f.name for f in batch])


def main() -> None:
    step = sys.argv[1] if len(sys.argv) > 1 else "all"
    if step in ("all", "pdf"):
        docx_to_pdf()
    if step in ("all", "png"):
        pdf_to_pngs()
    if step in ("all", "sheets"):
        contact_sheets()


if __name__ == "__main__":
    main()
