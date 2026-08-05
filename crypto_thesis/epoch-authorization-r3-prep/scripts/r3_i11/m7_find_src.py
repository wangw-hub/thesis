# -*- coding: utf-8 -*-
"""M7: locate RC3 python sources for header/hpke/aes/material-release."""
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")


def walk_dirs():
    for name in ["scripts", "contracts", "blockchain", "tests", "docs/research-content-3-implementation"]:
        p = ROOT / name
        if p.exists():
            for f in p.rglob("*.py"):
                if f.stat().st_size < 300_000:
                    yield f


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    pats = ["HeaderCore", "header_digest", "headerDigest", "hpke", "HPKE", "AES-256", "aes", "material", "release", "obj_hash", "objHash", "DOMAIN_HEADER", "domain", "info", "aad", "AAD"]
    hits = {p: [] for p in []}
    for f in walk_dirs():
        try:
            t = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        found = [pat for pat in pats if pat.lower() in t.lower()]
        if len(found) >= 3:
            print(f.relative_to(ROOT), "|", ", ".join(found))


if __name__ == "__main__":
    main()
