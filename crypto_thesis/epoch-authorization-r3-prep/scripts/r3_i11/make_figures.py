"""Pre-registered formal tables/figures (33-FORMAL-FIGURE-TABLE-PLAN)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    analysis = Path(args.analysis)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    index = json.loads((analysis / "accepted-run-index.json").read_text("utf-8"))
    descriptive = json.loads((analysis / "descriptive-statistics.json").read_text("utf-8"))
    effects = json.loads((analysis / "effect-sizes.json").read_text("utf-8"))
    invariants = json.loads((analysis / "formal-invariants.json").read_text("utf-8"))
    eligibility_rows = []
    for run in index["runs"]:
        eligibility_rows.append({
            "runId": run["runId"][:16], "experiment": run["experimentId"],
            "config": f"C{run['configIndex']}", "repeat": run["repeatIndex"],
            "scenario": run["scenarioClass"], "valid": run["valid"],
            "disposition": run["disposition"],
        })
    (out / "table-run-flow-eligibility.json").write_text(
        json.dumps({"schemaVersion": "R3FormalFigureTableV1",
                    "table": "run-flow/eligibility", "rows": eligibility_rows,
                    "counts": {
                        "planned": index["planned"], "executed": index["executed"],
                        "valid": index["valid"], "invalid": index["invalid"],
                    }}, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out / "table-within-class-duration.json").write_text(
        json.dumps({"schemaVersion": "R3FormalFigureTableV1",
                    "table": "within-class duration distributions (descriptive)",
                    "configs": descriptive}, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out / "table-matched-local-kubo-recovery.json").write_text(
        json.dumps({"schemaVersion": "R3FormalFigureTableV1",
                    "table": "matched Local/Kubo recovery (E5)",
                    "effectSizes": effects}, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out / "table-release-decision-outcome.json").write_text(
        json.dumps({"schemaVersion": "R3FormalFigureTableV1",
                    "table": "release-decision outcome",
                    "wrongMaterialRelease": invariants.get("wrongMaterialRelease", 0)},
                   ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({
        "tables": 4, "figures": 0,
        "output": str(out),
        "note": "descriptive tables only; figures require approved plotting stage",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
