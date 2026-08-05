from __future__ import annotations

from dataclasses import dataclass

from .models import RecoveryDisposition


@dataclass(frozen=True)
class IndexRebuildResult:
    disposition: RecoveryDisposition
    entries: tuple[tuple[str, str, int], ...]
    complete: bool


class RecipientIndexRebuilder:
    def rebuild(self, *, anchor_matches: bool, header_verified: bool, recipients):
        if not anchor_matches or not header_verified:
            return IndexRebuildResult(
                RecoveryDisposition.FAIL_CLOSED_MISSING_OBJECT, (), False
            )
        entries = tuple(sorted(
            (item["userId"], item["recipientKeyId"], int(item["userVersion"]))
            for item in recipients
        ))
        return IndexRebuildResult(RecoveryDisposition.AUTO_RECOVERABLE, entries, True)
