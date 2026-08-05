"""Synthetic-only I10 design checks; no live services or Formal data."""
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs" / "research-content-3-implementation" / "i10"


class FormalDesignContractTests(unittest.TestCase):
    def test_run_is_the_only_statistical_unit(self):
        prereg = json.loads((OUT / "formal-preregistration.json").read_text(encoding="utf-8"))
        self.assertEqual(prereg["statistics"]["unit"], "RUN")
        self.assertFalse(prereg["pairing"]["crossSemanticPairing"])

    def test_no_execution_is_admitted(self):
        state = json.loads((OUT / "i10-state.json").read_text(encoding="utf-8"))
        self.assertFalse(state["formalAttemptCreated"])
        self.assertFalse(state["formalDataCollected"])
        self.assertFalse(state["formalPerformanceConclusion"])

    def test_forbidden_consensus_claim_is_explicit(self):
        matrix = json.loads((OUT / "formal-claim-matrix.json").read_text(encoding="utf-8"))
        forbidden = [c for c in matrix["claims"] if c["status"] == "FORBIDDEN"]
        self.assertEqual([c["claimId"] for c in forbidden], ["C-07"])


if __name__ == "__main__":
    unittest.main()
