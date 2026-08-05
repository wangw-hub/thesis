from epoch_auth_r3.revocation.events import AUTHORIZATION_EVENT_MANIFEST, EventClass


def test_all_frozen_events_are_classified():
    assert set(AUTHORIZATION_EVENT_MANIFEST) == {
        "ResourceRegistered", "PolicyUpdated", "EpochAdvanced",
        "ResourceStatusChanged", "UserRegistered", "UserKeyRotated",
        "UserStatusChanged", "RoleGranted", "RoleRevoked",
    }


def test_direct_events():
    assert {k for k, v in AUTHORIZATION_EVENT_MANIFEST.items() if v == EventClass.DIRECT_RESOURCE} == {
        "PolicyUpdated", "EpochAdvanced", "ResourceStatusChanged"
    }


def test_user_scope_events():
    assert {k for k, v in AUTHORIZATION_EVENT_MANIFEST.items() if v == EventClass.USER_SCOPE} == {
        "UserKeyRotated", "UserStatusChanged"
    }


def test_audit_only_events():
    assert {k for k, v in AUTHORIZATION_EVENT_MANIFEST.items() if v == EventClass.AUDIT_ONLY} == {
        "ResourceRegistered", "UserRegistered", "RoleGranted", "RoleRevoked"
    }
