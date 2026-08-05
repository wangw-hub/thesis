"""Conservative local secret scan for F13-created public artifacts."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
CHAIN = ROOT / "infra" / "besu-qbft-multihost" / "formal-authorization-chain"
TARGETS = [CHAIN, ROOT / "docs" / "project-governance"]
HEX64 = re.compile(r"(?<![0-9a-fA-F])(?:0x)?([0-9a-fA-F]{64})(?![0-9a-fA-F])")
PEM = re.compile(r"BEGIN (?:OPENSSH |EC |RSA )?PRIVATE KEY")
SECRET_ASSIGNMENT = re.compile(
    r"(?i)(?:password|private[_-]?key|mnemonic|database_url)\s*[:=]\s*[\"']([^\"']+)[\"']"
)


def classify(path: Path, text: str, match: re.Match[str]) -> tuple[str, str]:
    relative = path.relative_to(ROOT).as_posix()
    line = text.count("\n", 0, match.start()) + 1
    if "private/" in relative or "secrets/" in relative:
        return "TRUE_SECRET", f"secret-directory candidate at line {line}"
    if any(
        token in relative
        for token in (
            "genesis/",
            "validator-public/",
            "accounts/",
            "contracts/artifact-manifest.json",
            "evidence/",
            "reports/",
            "artifact-sha256.json",
            "project-governance/",
        )
    ):
        return "PUBLIC_CHAIN_VALUE", f"public hash, address, receipt, or evidence value at line {line}"
    if relative.endswith(".py") or relative.endswith(".ps1"):
        return "PUBLIC_CHAIN_VALUE", f"frozen public digest or contract binding in deployment code at line {line}"
    return "UNCLASSIFIED", f"64-hex candidate at line {line}"


def main() -> None:
    candidates = []
    for target in TARGETS:
        for path in sorted(target.rglob("*")):
            if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            relative = path.relative_to(ROOT).as_posix()
            if PEM.search(text):
                candidates.append(
                    {"path": relative, "classification": "TRUE_SECRET", "reason": "private-key header"}
                )
            for match in SECRET_ASSIGNMENT.finditer(text):
                value = match.group(1)
                if value and not any(mark in value for mark in ("placeholder", "example", "path", "/")):
                    candidates.append(
                        {
                            "path": relative,
                            "classification": "UNCLASSIFIED",
                            "reason": "credential-like literal assignment",
                        }
                    )
            for match in HEX64.finditer(text):
                classification, reason = classify(path, text, match)
                candidates.append(
                    {"path": relative, "classification": classification, "reason": reason}
                )
    counts = {}
    for candidate in candidates:
        counts[candidate["classification"]] = counts.get(candidate["classification"], 0) + 1
    report = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "scope": [str(path.relative_to(ROOT)) for path in TARGETS],
        "prior_full_repository_scan": (
            "infra/besu-qbft-multihost/evidence/security-remediation/"
            "final-worktree-secret-scan.json"
        ),
        "counts": counts,
        "TRUE_SECRET": counts.get("TRUE_SECRET", 0),
        "UNCLASSIFIED": counts.get("UNCLASSIFIED", 0),
        "candidates": candidates,
        "accepted": counts.get("TRUE_SECRET", 0) == 0 and counts.get("UNCLASSIFIED", 0) == 0,
    }
    output = CHAIN / "evidence" / "f13" / "final-secret-scan.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"accepted": report["accepted"], "counts": counts}))
    if not report["accepted"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
