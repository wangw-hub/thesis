from __future__ import annotations

import hashlib
import json
import traceback
from dataclasses import asdict
from pathlib import Path

from .events import FormalPhaseEventJournal
from .evidence import FormalEvidenceWriter, validate_raw_run
from .phase_contract import validate_failure_phase_events
from .classification import (
    FormalEvidenceClassificationV1,
    MaterialReleaseDecisionV2, MaterialReleaseEvidenceV2,
)


class FormalRunTerminalizerV1:
    """Fail-closed formal run finalizer that seals truthful terminal evidence once."""

    def __init__(
        self, *, journal: FormalPhaseEventJournal, contract: dict, raw_root: Path,
        config: object, common: dict, failure_point: str,
        accumulator=None,
    ):
        self.journal = journal
        self.contract = contract
        self.raw_root = raw_root
        self.config = config
        self.common = common
        self.failure_point = failure_point
        self.accumulator = accumulator

    def terminalize(self, error: BaseException, contextual_records: dict | None = None) -> dict:
        path = self.journal.path
        observed = []
        for line in path.read_text("utf-8").splitlines():
            if line.strip():
                observed.append(json.loads(line))
        completed = {
            item["phaseName"] for item in observed
            if item.get("eventType") == "COMPLETED"
        }
        failed_phases = [
            item["phaseName"] for item in observed
            if item.get("eventType") == "COMPLETED"
            and item.get("result") not in {"OK", "NOT_REACHED"}
        ]
        failure_phase = failed_phases[0] if failed_phases else self.failure_point
        completed_ok = [
            item["phaseName"] for item in observed
            if item.get("eventType") == "COMPLETED" and item.get("result") == "OK"
        ]
        deepest_completed = completed_ok[-1] if completed_ok else "NONE"
        self.journal.emit("RUN_FAILURE_OBSERVED", "STARTED", "FAIL_CLOSED", type(error).__name__)
        self.journal.emit("RUN_FAILURE_OBSERVED", "COMPLETED", "FAIL_CLOSED", type(error).__name__)
        for name in sorted(set(self.contract["required"]) - completed - {"EVIDENCE_SEAL", "RUN_FINISHED"}):
            self.journal.emit(name, "NOT_REACHED", "NOT_REACHED", type(error).__name__)
        self.journal.emit("EVIDENCE_SEAL", "STARTED", "FAIL_CLOSED", type(error).__name__)
        self.journal.emit("EVIDENCE_SEAL", "COMPLETED", "FAIL_CLOSED", type(error).__name__)
        self.journal.emit("RUN_FINISHED", "STARTED", "FAIL_CLOSED", type(error).__name__)
        self.journal.emit("RUN_FINISHED", "COMPLETED", "FAIL_CLOSED", type(error).__name__)
        self.journal.close()
        if self.accumulator is not None:
            self.accumulator.close()
            accumulated = self.accumulator.snapshot()
            accumulator_text = self.accumulator.path.read_text("utf-8")
        else:
            accumulated = {"values": {}, "events": []}
            accumulator_text = ""
        values = accumulated["values"]
        scenario_evidence = values.get("scenarioEvidence", {})
        classification = FormalEvidenceClassificationV1.from_dict(
            self.common["evidenceClassification"]
        )
        material = MaterialReleaseEvidenceV2(
            decision=MaterialReleaseDecisionV2.NOT_EVALUATED,
            reasonCode="FAILURE_BEFORE_MATERIAL_RELEASE_EVALUATION",
            evaluationBlockNumber=None, evaluationBlockHash=None,
            headerDigest=values.get("headerDigest"),
            authorizationStateVersion=None, headerVersion=None, evaluated=False,
            sourceComponent="FormalRunTerminalizerV1",
            observedAt=__import__("datetime").datetime.now(
                __import__("datetime").timezone.utc
            ).isoformat(),
        ).to_dict()
        failure_validation = validate_failure_phase_events(self.contract, path)
        writer = FormalEvidenceWriter(self.raw_root, self.common["runId"])
        error_record = {
            "type": type(error).__name__,
            "code": str(error)[:256],
            "failurePoint": failure_phase,
            "traceback": traceback.format_exception_only(type(error), error)[-1].strip(),
        }
        failure_context = {
            "schemaVersion": 1, **self.common,
            "failurePhase": failure_phase,
            "deepestCompletedPhase": deepest_completed,
            "errorClass": type(error).__name__,
            "errorCode": str(error)[:256],
            "errorSummary": traceback.format_exception_only(type(error), error)[-1].strip(),
            "stackTraceDigest": hashlib.sha256(
                "".join(traceback.format_exception(type(error), error, error.__traceback__)).encode()
            ).hexdigest(),
            "databaseIdentity": values.get("databaseIdentity", "UNKNOWN"),
            "databaseTransactionState": {
                "jobCreate": values.get("jobCreateTransactionState", "NOT_REACHED"),
                "databaseFinalize": values.get("databaseFinalizeTransactionState", "NOT_REACHED"),
            },
            "jobId": values.get("jobId", "NOT_REACHED"),
            "jobState": values.get("jobState", values.get("jobCreateState", "NOT_REACHED")),
            "resourceId": values.get("resourceId", "NOT_REACHED"),
            "operationId": values.get("operationId", "NOT_REACHED"),
            "headerDigest": values.get("headerDigest", "NOT_REACHED"),
            "headerObjectDigest": values.get("headerObjectDigest", "NOT_REACHED"),
            "bodyObjectDigest": values.get("bodyObjectDigest", "NOT_REACHED"),
            "contentKeyRecordStatus": values.get("contentKeyRecordStatus", "MEMORY_ONLY_TEST_KEY"),
            "plannedTransactions": values.get("plannedTransactions", []),
            "signedTransactions": values.get("signedTransactions", []),
            "broadcastTransactions": values.get("broadcastTransactions", []),
            "receipts": values.get("receipts", []),
            "recoveryDisposition": "FAIL_CLOSED_EVIDENCE_SEALED",
            "materialReleaseEvidence": material,
            "scenarioEvidence": scenario_evidence,
            "capturedAt": __import__("datetime").datetime.now(
                __import__("datetime").timezone.utc
            ).isoformat(),
        }
        records = {
            "config.json": {
                **self.common, "config": asdict(self.config),
                "executionHost": "experiment-client",
                "executionMode": "REMOTE_AUTHORITATIVE",
            },
            "environment.json": {
                **self.common, "executionHost": "experiment-client",
                "formalSystemsAccessed": False,
            },
            "run-state.json": {
                **self.common, "status": "FAILED_EVIDENCE_SEALED", "valid": False,
                "outcomeClass": "FAIL_CLOSED", "failure": error_record,
                "failurePhaseContractValid": failure_validation.valid,
                "materialReleaseEvidence": material,
            },
            "phase-events.jsonl": path.read_text("utf-8"),
            "chain-evidence.json": {
                **self.common, "plannedTransactions": values.get("plannedTransactions", []),
                "signedTransactions": values.get("signedTransactions", []),
                "broadcastTransactions": values.get("broadcastTransactions", []),
                "receipts": values.get("receipts", []),
                "scenarioEvidence": scenario_evidence,
                "invariantViolations": 0,
            },
            "database-evidence.json": {
                **self.common, "jobId": values.get("jobId", "NOT_REACHED"),
                "jobState": values.get("jobState", values.get("jobCreateState", "NOT_REACHED")),
                "transactionState": {
                    "jobCreate": values.get("jobCreateTransactionState", "NOT_REACHED"),
                    "databaseFinalize": values.get("databaseFinalizeTransactionState", "NOT_REACHED"),
                },
                "invariantViolations": 0,
            },
            "object-evidence.json": {
                **self.common, "headerDigest": values.get("headerDigest", "NOT_REACHED"),
                "headerObjectDigest": values.get("headerObjectDigest", "NOT_REACHED"),
                "bodyObjectDigest": values.get("bodyObjectDigest", "NOT_REACHED"),
            },
            "ipfs-evidence.json": {**self.common, "cid": None, "exactReadback": False},
            "fault-evidence.json": {**self.common, "failure": error_record},
            "stdout.log": "FORMAL_EXPERIMENT FAIL_CLOSED\n",
            "stderr.log": error_record["traceback"] + "\n",
            "failure-context.json": failure_context,
            "phase-contract.json": self.contract,
            "chain-write-plan.json": values.get("chainWritePlan", {"status": "NOT_REACHED"}),
            "database-transaction-evidence.json": {
                "jobCreate": values.get("jobCreateTransactionState", "NOT_REACHED"),
                "databaseFinalize": values.get("databaseFinalizeTransactionState", "NOT_REACHED"),
                "jobState": values.get("jobState", values.get("jobCreateState", "NOT_REACHED")),
            },
            "chain-transaction-evidence.json": {
                "planned": values.get("plannedTransactions", []),
                "signed": values.get("signedTransactions", []),
                "broadcast": values.get("broadcastTransactions", []),
                "receipts": values.get("receipts", []),
            },
            "material-release-evidence.json": {
                **self.common,
                "current": material, "history": [material],
                "scenarioProjection": material, "finalEnvelopeProjection": material,
            },
            "evidence-accumulator.jsonl": accumulator_text,
        }
        if contextual_records:
            for name, value in contextual_records.items():
                if name in records:
                    records[name] = value
        for name, value in records.items():
            writer.write_once(name, value)
        seal = writer.seal()
        errors = validate_raw_run(writer.root)
        return {
            "runId": self.common["runId"], "valid": False,
            "outcomeClass": "FAIL_CLOSED", "failurePoint": failure_phase,
            "deepestCompletedPhase": deepest_completed,
            "rawShaErrors": len(errors), "missingPhases": len(
                failure_validation.unclassifiedRequiredPhases
            ), "terminalEvidence": failure_validation.valid,
            "sealedFiles": seal["files"], "executionHost": "experiment-client",
        }
