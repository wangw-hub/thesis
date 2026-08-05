"""Stepwise Word COM render for V2: open / update / export."""
from __future__ import annotations

import sys
import time
from pathlib import Path


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
OUT = ROOT / "docs/final-manuscript/output"
DOCX = OUT / "THESIS-FORMAT-CANDIDATE-V2.docx"
PDF = OUT / "THESIS-FORMAT-CANDIDATE-V2.pdf"


def main() -> None:
    step = sys.argv[1] if len(sys.argv) > 1 else "open"
    import win32com.client
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        t0 = time.time()
        d = word.Documents.Open(str(DOCX), ReadOnly=False, AddToRecentFiles=False,
                                ConfirmConversions=False, Revert=False)
        print(f"opened in {time.time() - t0:.1f}s")
        if step in ("fields", "all"):
            t0 = time.time()
            d.Fields.Update()
            print(f"fields updated in {time.time() - t0:.1f}s")
            try:
                for toc in d.TablesOfContents:
                    toc.Update()
            except Exception:
                pass
        if step in ("export", "all"):
            d.Repaginate()
            d.Save()
            t0 = time.time()
            d.ExportAsFixedFormat(str(PDF), 17)
            print(f"exported in {time.time() - t0:.1f}s pages={d.ComputeStatistics(2)}")
        if step == "export-only":
            t0 = time.time()
            d.ExportAsFixedFormat(str(PDF), 17)
            print(f"exported in {time.time() - t0:.1f}s pages={d.ComputeStatistics(2)}")
        if step == "fields-export":
            t0 = time.time()
            d.Fields.Update()
            print(f"fields updated in {time.time() - t0:.1f}s")
            try:
                for toc in d.TablesOfContents:
                    toc.Update()
            except Exception:
                pass
            d.ExportAsFixedFormat(str(PDF), 17)
            print(f"exported in {time.time() - t0:.1f}s pages={d.ComputeStatistics(2)}")
        d.Close(False)
    finally:
        word.Quit()


if __name__ == "__main__":
    main()
