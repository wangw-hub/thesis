# -*- coding: utf-8 -*-
"""M7: scan M6 source for English class-name / term occurrences."""
from __future__ import annotations

import re
import sys


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = r"D:\Research\crypto_thesis\epoch-authorization-r3-prep\docs\midterm-report\m6\M6-MIDTERM-SOURCE.md"
    lines = open(p, encoding="utf-8").read().split("\n")
    pats = {
        "AuthorizationState": r"AuthorizationState",
        "HeaderRegistry": r"HeaderRegistry",
        "AccessMaterialReleaseGuard": r"AccessMaterialReleaseGuard",
        "LocalObjectStore": r"LocalObjectStore",
        "RecoveryCoordinator": r"RecoveryCoordinator",
        "Issuer": r"\bIssuer\b",
        "Verifier": r"\bVerifier\b",
        "operationId": r"operationId",
        "policyDigest": r"policyDigest",
        "Header": r"\bHeader\b",
        "Body": r"\bBody\b",
        "CK": r"\bCK\b",
        "HeaderCore": r"HeaderCore",
        "SignedVersionedHeader": r"SignedVersionedHeader",
        "EncryptedCKRecord": r"EncryptedCKRecord",
        "Kubo": r"Kubo",
        "Nonce": r"\bNonce\b",
        "hdrHash": r"hdrHash",
        "objHash": r"objHash",
    }
    for name, pat in pats.items():
        hits = []
        for i, ln in enumerate(lines, 1):
            if re.search(pat, ln):
                hits.append(i)
        print(f"{name}: {hits}")


if __name__ == "__main__":
    main()
