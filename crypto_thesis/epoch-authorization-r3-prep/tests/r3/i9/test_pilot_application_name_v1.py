import re

import pytest

from epoch_auth_r3.pilot.database import (
    APPLICATION_NAME_DOMAIN, PilotApplicationNameV1,
    PilotDatabaseConnectionRoleV1,
)


def make(**overrides):
    values = {
        "attempt_id": "I9_REVISION_7_20260730T000000Z_abcdef0",
        "run_identity": "1" * 64,
        "role": PilotDatabaseConnectionRoleV1.CANARY,
        "software_commit": "2" * 40,
    }
    values.update(overrides)
    return PilotApplicationNameV1.generate(**values)


def test_pilot_application_name_v1():
    value = make()
    assert value.value == f"r3i9-canary-{value.digestPrefix}"
    assert len(value.digestPrefix) == 32
    assert APPLICATION_NAME_DOMAIN == "EPOCH_AUTH_R3_I9_PG_APPLICATION_NAME_V1"


def test_application_name_ascii_only_and_max_63_bytes():
    value = make().value
    assert value.isascii()
    assert re.fullmatch(r"[a-z0-9-]+", value)
    assert len(value.encode()) <= 63


def test_application_name_deterministic_and_identity_changes():
    base = make().value
    assert make().value == base
    assert make(attempt_id="other").value != base
    assert make(run_identity="3" * 64).value != base
    assert make(role=PilotDatabaseConnectionRoleV1.JOB).value != base
    assert make(software_commit="4" * 40).value != base


def test_application_name_unknown_role_rejected():
    with pytest.raises(ValueError, match="UNKNOWN"):
        make(role="canary")


def test_application_name_full_identities_not_embedded():
    item = make()
    assert "I9_REVISION" not in item.value
    assert "1" * 64 not in item.value


def test_bootstrap_and_canary_names_differ():
    bootstrap = make(
        run_identity="NO_RUN", role=PilotDatabaseConnectionRoleV1.BOOTSTRAP
    )
    assert bootstrap.value != make().value
