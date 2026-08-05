"""Development-only P9-A evidence acceptance rehearsal; performs no I/O to pilot raw."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from epoch_auth_r3.pilot.p9a_evidence_contract import P9ADryRunAcceptanceV1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cases = {
        name: decision.to_dict()
        for name, decision in P9ADryRunAcceptanceV1.evaluate_cases().items()
    }
    result = {
        "schemaVersion": "P9ADryRunAcceptanceV1",
        "classification": [
            "DEVELOPMENT_ONLY", "NOT_PILOT_EVIDENCE",
            "NOT_FOR_STATISTICS", "NOT_FOR_THESIS_RESULTS",
        ],
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "cases": cases,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise SystemExit("DRY_RUN_OUTPUT_EXISTS")
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True), "utf-8")
    print(json.dumps({name: value["accepted"] for name, value in cases.items()}, sort_keys=True))


if __name__ == "__main__":
    main()
