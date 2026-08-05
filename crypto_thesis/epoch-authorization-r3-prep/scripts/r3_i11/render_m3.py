"""Render the M3 midterm DOCX to PDF via Word COM."""
from __future__ import annotations

import sys
import time
from pathlib import Path


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
OUT = ROOT / "docs/midterm-report/m3/output"
STEM = "王威-专业学位研究生学位论文中期考评表-M3候选稿"
DOCX = OUT / f"{STEM}.docx"
PDF = OUT / f"{STEM}.pdf"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
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
