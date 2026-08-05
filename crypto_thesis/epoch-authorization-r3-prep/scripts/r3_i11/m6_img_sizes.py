# -*- coding: utf-8 -*-
"""M6: report PNG dimensions for all source images."""
from __future__ import annotations

import os
import struct
import sys
from pathlib import Path


def png_size(p):
    with open(p, "rb") as f:
        head = f.read(24)
    w, h = struct.unpack(">II", head[16:24])
    return w, h


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    dirs = [
        Path(r"D:\Users\wangw\Desktop\中期和小论文\系统结构图"),
        Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep\docs\midterm-report\m6\figures"),
    ]
    for d in dirs:
        print("=== ", d)
        for p in sorted(d.glob("*.png")):
            w, h = png_size(p)
            print(f"{p.name}: {w}x{h}  ratio={w/h:.3f}  size={os.path.getsize(p)//1024}KB")


if __name__ == "__main__":
    main()
