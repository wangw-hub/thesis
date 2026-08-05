import pytest

from epoch_auth_r3.revocation.policy import HeaderUpdateKind, decide_update


@pytest.mark.parametrize("event", [
    "PolicyUpdated", "EpochAdvanced", "ResourceStatusChanged",
    "UserKeyRotated", "UserStatusChanged",
])
def test_auth_or_recipient_change_is_header_only(event):
    assert decide_update(event).kind == HeaderUpdateKind.HEADER_ONLY


def test_body_change_is_rotation():
    assert decide_update("EpochAdvanced", body_changed=True).kind == HeaderUpdateKind.BODY_ROTATION


def test_ck_compromise_is_rotation():
    assert decide_update("UserStatusChanged", ck_compromised=True).kind == HeaderUpdateKind.BODY_ROTATION


def test_revoked_resource_has_no_new_header():
    assert decide_update("ResourceStatusChanged", resource_status="REVOKED").kind == HeaderUpdateKind.NO_NEW_HEADER


def test_unknown_trigger_requires_policy_decision():
    assert decide_update("Unknown").kind == HeaderUpdateKind.POLICY_DECISION_REQUIRED
