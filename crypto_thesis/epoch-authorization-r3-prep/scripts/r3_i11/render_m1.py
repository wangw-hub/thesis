"""Render a midterm form DOCX to PDF via Word COM (stem selectable)."""
from __future__ import annotations

import sys
import time
from pathlib import Path


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
OUT = ROOT / "docs/midterm-report/output"
M2_OUT = ROOT / "docs/midterm-report/m2/output"
STEM = sys.argv[1] if len(sys.argv) > 1 else "王威-专业学位研究生学位论文中期考评表-候选稿"
base = M2_OUT if STEM.endswith("M2候选稿") else OUT
DOCX = base / f"{STEM}.docx"
PDF = base / f"{STEM}.pdf"


def main() -> None:
    import win32com.client
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        t0 = time.time()
        d = word.Documents.Open(str(DOCX), ReadOnly=False, AddToRecentFiles=False,
                                ConfirmConversions=False, Revert=False)
        print(f"opened in {time.time() - t0:.1f}s")
        d.Fields.Update()
        d.ExportAsFixedFormat(str(PDF), 17)
        print(f"exported in {time.time() - t0:.1f}s pages={d.ComputeStatistics(2)}")
        d.Close(False)
    finally:
        word.Quit()


if __name__ == "__main__":
    main()
