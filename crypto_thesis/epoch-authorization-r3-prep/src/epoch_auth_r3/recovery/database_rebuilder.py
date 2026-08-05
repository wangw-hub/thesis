from __future__ import annotations

from dataclasses import dataclass

from .models import RecoveryDisposition


@dataclass(frozen=True)
class DerivedRecoveryState:
    label: str
    disposition: RecoveryDisposition
    current_state_rebuilt: bool
    history_complete: bool


class DatabaseDerivedStateRebuilder:
    """Rebuild only current derived state; never invent missing workflow history."""

    def rebuild(self, *, chain_anchor_verified: bool, header_object_verified: bool):
        if not chain_anchor_verified:
            return DerivedRecoveryState(
                "DERIVED_RECOVERY_STATE",
                RecoveryDisposition.FAIL_CLOSED_CHAIN_UNAVAILABLE,
                False,
                False,
            )
        if not header_object_verified:
            return DerivedRecoveryState(
                "DERIVED_RECOVERY_STATE",
                RecoveryDisposition.FAIL_CLOSED_MISSING_OBJECT,
                False,
                False,
            )
        return DerivedRecoveryState(
            "DERIVED_RECOVERY_STATE",
            RecoveryDisposition.AUTO_RECOVERABLE,
            True,
            False,
        )
