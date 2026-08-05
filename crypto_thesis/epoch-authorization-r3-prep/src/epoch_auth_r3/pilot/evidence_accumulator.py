from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class EvidenceAccumulatorV1:
    path: Path
    values: dict = field(default_factory=dict)
    events: list[dict] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._stream = self.path.open("x", encoding="utf-8", newline="\n")

    def record(self, event_type: str, values: dict) -> None:
        for key, value in values.items():
            if key in self.values and self.values[key] != value:
                raise RuntimeError(f"EVIDENCE_CONTEXT_CONFLICT:{key}")
            self.values[key] = value
        event = {
            "sequence": len(self.events) + 1,
            "eventType": event_type,
            "capturedAt": datetime.now(timezone.utc).isoformat(),
            "values": values,
        }
        self.events.append(event)
        self._stream.write(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n")
        self._stream.flush()
        os.fsync(self._stream.fileno())

    def append_transaction(self, category: str, value: dict) -> None:
        current = list(self.values.get(category, []))
        current.append(value)
        self.values[category] = current
        event = {
            "sequence": len(self.events) + 1,
            "eventType": category,
            "capturedAt": datetime.now(timezone.utc).isoformat(),
            "values": value,
        }
        self.events.append(event)
        self._stream.write(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n")
        self._stream.flush()
        os.fsync(self._stream.fileno())

    def snapshot(self) -> dict:
        return {"values": dict(self.values), "events": list(self.events)}

    def close(self) -> None:
        if not self._stream.closed:
            self._stream.flush()
            os.fsync(self._stream.fileno())
            self._stream.close()
