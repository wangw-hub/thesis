from __future__ import annotations

from .models import RecoveryDisposition


def classify_key_recovery(*, available: bool, permanent_loss: bool = False):
    if available:
        return RecoveryDisposition.CONSISTENT
    if permanent_loss:
        return RecoveryDisposition.IRRECOVERABLE_KEY_LOSS
    return RecoveryDisposition.FAIL_CLOSED_KEY_UNAVAILABLE
