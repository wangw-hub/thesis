# -*- coding: utf-8 -*-
"""M7: count English term occurrences in M7 source and print their contexts."""
from __future__ import annotations

import re
import sys


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = r"D:\Research\crypto_thesis\epoch-authorization-r3-prep\docs\midterm-report\m7\M7-MIDTERM-SOURCE.md"
    s = open(p, encoding="utf-8").read()
    terms = [
        "AuthorizationState",
        "HeaderRegistry",
        "AccessMaterialReleaseGuard",
        "LocalObjectStore",
        "RecoveryCoordinator",
        "operationId",
        "policyDigest",
        "HeaderCore",
        "SignedVersionedHeader",
        "EncryptedCKRecord",
    ]
    for t in terms:
        hits = [m.start() for m in re.finditer(re.escape(t), s)]
        print(f"{t}: {len(hits)}")
        for h in hits:
            print("    ...", s[max(0, h - 45): h + len(t) + 20].replace("\n", " "))

    print("\nstandalone Header/Body/CK (word boundaries, excluding first parens):")
    for t in ("Header", "Body", "CK"):
        hits = [m.start() for m in re.finditer(rf"\b{t}\b", s)]
        print(f"{t}: {len(hits)}")
        for h in hits:
            print("    ...", s[max(0, h - 45): h + len(t) + 20].replace("\n", " "))


if __name__ == "__main__":
    main()
