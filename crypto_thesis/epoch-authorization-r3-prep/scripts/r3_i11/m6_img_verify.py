# -*- coding: utf-8 -*-
"""M6: verify DOCX embedded images match the source PNGs (hash compare)."""
from __future__ import annotations

import hashlib
import io
import sys
import zipfile
from pathlib import Path


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
OUT = ROOT / "docs/midterm-report/m6/output/王威-专业学位研究生学位论文中期考评表-M6候选稿.docx"
SYSTEM_FIG = Path(r"D:\Users\wangw\Desktop\中期和小论文\系统结构图")
EXP_FIG = ROOT / "docs/midterm-report/m6/figures"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    srcs = {}
    for p in sorted(SYSTEM_FIG.glob("*.png")):
        srcs[sha(p)] = ("SYSTEM", p.name)
    for p in sorted(EXP_FIG.glob("*.png")):
        srcs[sha(p)] = ("EXP", p.name)

    with zipfile.ZipFile(str(OUT)) as z:
        media = [n for n in z.namelist() if n.startswith("word/media/")]
        print("media files in DOCX:", len(media))
        matched = 0
        unknown = []
        for n in media:
            data = z.read(n)
            h = hashlib.sha256(data).hexdigest()
            if h in srcs:
                matched += 1
            else:
                unknown.append((n, len(data)))
        print("matched source images:", matched)
        print("unknown media:", unknown)


if __name__ == "__main__":
    main()
