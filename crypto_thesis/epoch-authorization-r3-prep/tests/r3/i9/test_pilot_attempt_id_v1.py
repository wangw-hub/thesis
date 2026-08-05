from datetime import UTC, datetime

import pytest

from epoch_auth_r3.pilot.attempt import PilotAttemptIdV1
from epoch_auth_r3.pilot.config import attempt_scoped_run_id
from test_pilot_contracts import config


FAILED_ATTEMPT = "I9_P9_A_20260801T073550Z_793adab"
REVISION_8_ATTEMPT = "I9_REVISION_8_20260730T155554Z_c1d9bbf"


def test_attempt_id_create_parse_roundtrip():
    value = PilotAttemptIdV1.create(
        family="P9A",
        created_at=datetime(2026, 8, 1, 8, 0, 0, tzinfo=UTC),
        git_sha="793adabb955a4ed17eb3df1091d63636caf5a08b",
    )
    assert value.serialize() == "I9_P9A_20260801T080000Z_793adab"
    assert PilotAttemptIdV1.parse(value.serialize()).serialize() == value.serialize()
    assert PilotAttemptIdV1.validate(value.serialize()) == value


def test_attempt_id_generated_value_validates():
    value = PilotAttemptIdV1.create(
        family="REVISION",
        revision=9,
        created_at=datetime(2026, 8, 1, 8, 0, 0, tzinfo=UTC),
        git_sha="a" * 40,
    )
    assert PilotAttemptIdV1.validate(value.serialize()) == value


def test_canary_attempt_id_still_parses():
    assert PilotAttemptIdV1.parse(REVISION_8_ATTEMPT).revision == 8


def test_p9a_attempt_id_parses():
    assert PilotAttemptIdV1.parse("I9_P9A_20260801T080000Z_793adab").family == "P9A"


@pytest.mark.parametrize("family", ("P9B", "P9C", "P9D"))
def test_bcd_attempt_ids_are_stage_scoped(family):
    value = PilotAttemptIdV1.create(
        family=family, created_at=datetime(2026, 8, 1, 8, 0, 0, tzinfo=UTC), git_sha="a" * 40,
    )
    assert PilotAttemptIdV1.validate(value.serialize()).family == family


@pytest.mark.parametrize(
    "value",
    [
        FAILED_ATTEMPT,
        "I9_P9A_20260801T080000Z_793ADA!",
        "I9_P9A_20260801T080000Z_793ADAB",
        "I9_P9A_20260801T080000Z_793adab/child",
        "I9_P9A_20260801T080000Z_793adab\\child",
        "I9_P9A_20260801T080000Z_793adab:child",
        " I9_P9A_20260801T080000Z_793adab",
    ],
)
def test_attempt_id_invalid_chars_or_old_failure_rejected(value):
    with pytest.raises(ValueError, match="INVALID_ATTEMPT_ID"):
        PilotAttemptIdV1.parse(value)


def test_run_id_created_only_after_attempt_validation():
    with pytest.raises(ValueError, match="INVALID_ATTEMPT_ID"):
        attempt_scoped_run_id(FAILED_ATTEMPT, config())
    assert len(attempt_scoped_run_id(REVISION_8_ATTEMPT, config())) == 64
