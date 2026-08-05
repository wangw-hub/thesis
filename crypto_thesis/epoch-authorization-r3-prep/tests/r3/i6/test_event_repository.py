import uuid
import pytest

from epoch_auth_r3.revocation.repository import (
    AuthorizationEventRepository, ConflictingAuthorizationEvent,
)
from test_event_normalizer import make


def test_event_idempotent_insert(db):
    repo = AuthorizationEventRepository(db)
    first, inserted = repo.insert(make())
    second, duplicate = repo.insert(make())
    assert inserted and not duplicate and first == second


def test_event_conflicting_duplicate(db):
    repo = AuthorizationEventRepository(db)
    repo.insert(make())
    changed = make(args={"resourceId": b"\x04" * 32, "newEpoch": 3})
    with pytest.raises(ConflictingAuthorizationEvent):
        repo.insert(changed)


def test_database_has_i6_tables(db):
    for table in ("authorization_event", "resource_recipient_index", "content_key_record"):
        assert db.execute("select to_regclass(%s)", (f"r3_control.{table}",)).fetchone()[0]
