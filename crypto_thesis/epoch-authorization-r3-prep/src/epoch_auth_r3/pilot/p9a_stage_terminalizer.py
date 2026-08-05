from __future__ import annotations

import hashlib
import json
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from epoch_auth_r3.pilot.attempt import PilotAttemptIdV1
from epoch_auth_r3.pilot.bootstrap import AtomicJsonWriterV1
from epoch_auth_r3.pilot.p9a_evidence_contract import P9AAcceptanceDecisionV1


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class P9AStageTerminalizerV1:
    def __init__(self, gate_path: Path, attempt_id: str):
        self.gate_path = gate_path
        self.attempt_id = PilotAttemptIdV1.validate(attempt_id).serialize()
        self.evidence_path = gate_path.parent / "p9a-stage-gate-evidence.json"
        self._expected_sha: str | None = None

    def _read(self) -> dict:
        value = json.loads(self.gate_path.read_text("utf-8"))
        if value.get("attemptId") != self.attempt_id:
            raise ValueError("P9A_GATE_ATTEMPT_MISMATCH")
        return value

    def _cas_write(self, value: dict) -> str:
        if self._expected_sha is not None and _sha(self.gate_path) != self._expected_sha:
            raise RuntimeError("P9A_GATE_CAS_MISMATCH")
        digest = AtomicJsonWriterV1.write(self.gate_path, value)
        self._expected_sha = digest
        if self._read() != value or _sha(self.gate_path) != digest:
            raise RuntimeError("P9A_GATE_READBACK_FAILED")
        return digest

    def start(self) -> dict:
        gate = self._read()
        if gate.get("state") not in {"P9_A_READY", "P9_A_NOT_STARTED"}:
            raise ValueError("PILOT_STAGE_GATE_BLOCKED")
        self._expected_sha = _sha(self.gate_path)
        gate["revision"] = int(gate.get("revision", 0)) + 1
        gate["state"] = "P9_A_RUNNING"
        gate.setdefault("history", []).append({
            "stage": "P9-A", "transition": "P9_A_RUNNING", "at": datetime.now(UTC).isoformat()
        })
        self._cas_write(gate)
        return gate

    def finish(
        self,
        *,
        decision: P9AAcceptanceDecisionV1,
        planned: int,
        actual: int,
        valid: int,
        failure_scope: str | None = None,
        failed_scenario: str | None = None,
        run_created: bool = False,
        business_side_effects: bool = False,
        error: BaseException | None = None,
    ) -> dict:
        gate = self._read()
        if gate.get("state") != "P9_A_RUNNING":
            raise ValueError("P9A_GATE_NOT_RUNNING")
        if (
            decision.plannedRunCount != planned
            or decision.actualRunCount != actual
            or decision.validRunCount != valid
        ):
            raise ValueError("P9A_ACCEPTANCE_DECISION_COUNT_MISMATCH")
        gate["revision"] = int(gate.get("revision", 0)) + 1
        passed = decision.accepted
        gate["state"] = "P9_A_PASSED" if passed else "P9_A_FAILED"
        gate.update({"planned": planned, "actual": actual, "valid": valid})
        gate["acceptanceDecision"] = decision.to_dict()
        if not passed:
            gate.update({
                "failureScope": failure_scope or "ATTEMPT_ORCHESTRATION",
                "failedScenario": failed_scenario or "A1",
                "runCreated": run_created,
                "businessSideEffects": business_side_effects,
                "errorClass": type(error).__name__ if error else None,
                "errorMessage": str(error) if error else None,
            })
        gate.setdefault("history", []).append({
            "stage": "P9-A", "transition": gate["state"], "planned": planned,
            "actual": actual, "valid": valid, "at": datetime.now(UTC).isoformat(),
        })
        digest = self._cas_write(gate)
        evidence = {
            "schemaVersion": 1, "attemptId": self.attempt_id, "state": gate["state"],
            "gateRevision": gate["revision"], "gateSha256": digest,
            "readbackVerified": True, "p9BTasksCreated": gate.get("p9BTasksCreated", False),
        }
        AtomicJsonWriterV1.write(self.evidence_path, evidence)
        return evidence

    @contextmanager
    def guard(self, *, failed_scenario: str = "A1"):
        self.start()
        try:
            yield self
        except BaseException as exc:
            self.finish(
                decision=P9AAcceptanceDecisionV1.evaluate(
                    planned=8, actual=0, valid=0, major=1
                ), planned=8, actual=0, valid=0,
                failure_scope="ATTEMPT_ORCHESTRATION", failed_scenario=failed_scenario,
                run_created=False, business_side_effects=False, error=exc,
            )
            raise
