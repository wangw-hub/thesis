# -*- coding: utf-8 -*-
"""Dump exact M7 source blocks for algorithms/references/section 7."""
from __future__ import annotations

import sys


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = r"D:\Research\crypto_thesis\epoch-authorization-r3-prep\docs\midterm-report\m7\M7-MIDTERM-SOURCE.md"
    lines = open(p, encoding="utf-8").read().split("\n")
    ranges = [(90, 116), (178, 208), (258, 306), (316, 345), (363, 380), (383, 460)]
    for a, b in ranges:
        print("=" * 40, f"LINES {a}-{b}", "=" * 40)
        for j in range(a, min(b, len(lines)) + 1):
            print(f"{j:03d}| {lines[j-1]}")


if __name__ == "__main__":
    main()
