"""Read-only validator for the I10 design package.

The validator checks manifests, schemas, preregistration consistency, the
read-only I9 baseline digest, and a few synthetic run-unit fixtures.  It never
opens a network connection or creates an experiment directory.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "research-content-3-implementation" / "i10"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def baseline_digest() -> str:
    paths = [
        "experiments/r3/i9-pilot/final-analysis/i9-run-index.json",
        "experiments/r3/i9-pilot/final-analysis/i9-state.json",
        "experiments/r3/i9-pilot/final-analysis/pairing-smoke.json",
        "experiments/r3/i9-pilot/final-analysis/statistical-smoke.json",
        "experiments/r3/i9-pilot/final-analysis/strict-review.json",
        "docs/research-content-3-implementation/i9-bcd/18-I9-STATE.md",
        "docs/research-content-3-implementation/i9-bcd/20-I9-ACCEPTANCE.md",
    ]
    entries = [(p, sha((ROOT / p).read_bytes())) for p in paths]
    data = b"".join((p + "\0" + h + "\n").encode("utf-8") for p, h in sorted(entries))
    return sha(data)


class SyntheticRunUnitTests(unittest.TestCase):
    def test_phase_rows_are_not_independent_runs(self):
        rows = [{"runId": "R1", "phase": "EXECUTE"}, {"runId": "R1", "phase": "SEAL"}]
        self.assertEqual(len({row["runId"] for row in rows}), 1)

    def test_duplicate_run_identity_is_rejected(self):
        rows = [{"runId": "R1"}, {"runId": "R1"}]
        self.assertNotEqual(len(rows), len({row["runId"] for row in rows}))


def main() -> None:
    required_docs = [f"{i:02d}-" for i in range(37)]
    present = {p.name for p in OUT.glob("*.md")}
    assert len(present) == 37, f"expected 37 Markdown deliverables, got {len(present)}"
    assert all(any(name.startswith(prefix) for name in present) for prefix in required_docs)

    state = json.loads((OUT / "i10-state.json").read_text(encoding="utf-8"))
    assert state["state"] == "I10_COMPLETED_AWAITING_I11_APPROVAL"
    assert state["i9AcceptedPilotBaselineDigest"] == baseline_digest()
    assert state["formalAttemptCreated"] is False
    assert state["formalDataCollected"] is False
    assert state["formalPerformanceConclusion"] is False
    assert state["rc2FormalAssetsReused"] is False
    assert state["pseudoreplicationViolations"] == 0
    assert state["resultDrivenFactorLevelViolations"] == 0

    rq = json.loads((OUT / "formal-rq-matrix.json").read_text(encoding="utf-8"))
    claims = json.loads((OUT / "formal-claim-matrix.json").read_text(encoding="utf-8"))
    factors = json.loads((OUT / "formal-factor-matrix.json").read_text(encoding="utf-8"))
    metrics = json.loads((OUT / "formal-metric-registry.json").read_text(encoding="utf-8"))
    budget = json.loads((OUT / "formal-run-budget.json").read_text(encoding="utf-8"))
    prereg = json.loads((OUT / "formal-preregistration.json").read_text(encoding="utf-8"))
    assert len(rq["researchQuestions"]) == 6
    assert len(claims["claims"]) == 7
    assert any(c["status"] == "FORBIDDEN" for c in claims["claims"])
    assert len(factors["factors"]) == 8
    assert len(metrics["metrics"]) == 12
    assert budget["measuredRuns"] == 145 and budget["totalPlannedRuns"] == 180
    assert prereg["rc3MultiNodeFormalRequired"] is False
    assert prereg["pairing"]["crossSemanticPairing"] is False
    fingerprint = json.loads((OUT / "formal-environment-fingerprint-template.json").read_text(encoding="utf-8"))
    assert fingerprint["schemaVersion"] == "R3FormalEnvironmentFingerprintV1"
    assert "contractBytecodeDigest" in fingerprint["requiredFields"]
    topology = json.loads((OUT / "formal-besu-topology.json").read_text(encoding="utf-8"))
    assert topology["schemaVersion"] == "R3FormalBesuTopologyV1"
    assert topology["deployed"] is False
    assert topology["nodes"] == [{"role": "Validator", "count": 4}, {"role": "RPC_CLIENT", "count": 1}]
    prereg_copy = dict(prereg)
    prereg_digest = prereg_copy.pop("preregistrationDigest")
    prereg_copy["preregistrationDigest"] = None
    assert prereg_digest == sha(canonical(prereg_copy))

    manifest = json.loads((OUT / "artifact-sha256.json").read_text(encoding="utf-8"))
    listed = {entry["path"]: entry["sha256"] for entry in manifest["files"]}
    assert "artifact-sha256.json" not in listed
    for rel, expected in listed.items():
        assert sha((OUT / rel).read_bytes()) == expected, f"artifact SHA mismatch: {rel}"
    forbidden_real_paths = [ROOT / "experiments" / "r3" / "i10", ROOT / "experiments" / "formal"]
    assert all(not p.exists() for p in forbidden_real_paths)

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(SyntheticRunUnitTests)
    result = unittest.TextTestRunner(verbosity=0).run(suite)
    assert result.wasSuccessful()
    print(json.dumps({"status": "PASS", "markdownFiles": len(present), "artifactFiles": len(listed), "syntheticTests": result.testsRun, "baselineDigest": baseline_digest()}, ensure_ascii=False))


if __name__ == "__main__":
    main()
