from __future__ import annotations

import json
import os
import socket
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class FormalPhaseEventV1:
    runId: str
    attemptId: str
    configDigest: str
    phaseName: str
    phaseSequence: int
    component: str
    componentInstanceId: str
    processId: int
    executionHost: str
    eventType: str
    monotonicTimestampNs: int
    wallClockUtc: str
    result: str
    errorCode: str | None = None

    def __post_init__(self) -> None:
        if self.phaseSequence < 1 or self.monotonicTimestampNs < 0:
            raise ValueError("INVALID_PHASE_EVENT")
        if self.executionHost != "experiment-client":
            raise ValueError("NON_AUTHORITATIVE_EXECUTION_HOST")
        if self.eventType not in {"STARTED", "COMPLETED", "NOT_APPLICABLE", "NOT_REACHED"}:
            raise ValueError("INVALID_PHASE_EVENT_TYPE")


class FormalPhaseEventJournal:
    """Append-only event journal written by the remote formal runner."""

    def __init__(self, path: Path, *, run_id: str, attempt_id: str, config_digest: str):
        if socket.gethostname() != "experiment-client":
            raise RuntimeError("REMOTE_EXECUTION_REQUIRED")
        self.path = path
        self.run_id = run_id
        self.attempt_id = attempt_id
        self.config_digest = config_digest
        self.sequence = 0
        path.parent.mkdir(parents=True, exist_ok=True)
        self._stream = path.open("x", encoding="utf-8", newline="\n")

    def emit(self, phase: str, event_type: str, result: str = "OK",
             error_code: str | None = None) -> None:
        self.sequence += 1
        event = FormalPhaseEventV1(
            self.run_id, self.attempt_id, self.config_digest, phase, self.sequence,
            "r3-formal-runner", f"formal-{os.getpid()}", os.getpid(),
            "experiment-client", event_type, time.monotonic_ns(),
            datetime.now(timezone.utc).isoformat(), result, error_code,
        )
        self._stream.write(json.dumps(asdict(event), sort_keys=True, separators=(",", ":")) + "\n")
        self._stream.flush()
        os.fsync(self._stream.fileno())

    def close(self) -> None:
        self._stream.flush()
        os.fsync(self._stream.fileno())
        self._stream.close()
