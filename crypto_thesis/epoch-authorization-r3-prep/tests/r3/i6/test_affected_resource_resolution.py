import pytest

from epoch_auth_r3.revocation.resolver import (
    AffectedResourceResolver, IncompleteResourceIndex, RecipientIndexEntry,
)
from test_event_normalizer import make


def test_direct_resource_resolution():
    assert AffectedResourceResolver([], complete=False).resolve(make()) == ("04" * 32,)


def test_user_scope_resolution_is_sorted_and_unique():
    event = make("UserStatusChanged", {"userId": b"\x09" * 32, "newStatus": 3})
    entries = [
        RecipientIndexEntry("bb" * 32, "09" * 32, "11" * 32, 1),
        RecipientIndexEntry("aa" * 32, "09" * 32, "12" * 32, 1),
    ]
    assert AffectedResourceResolver(entries, complete=True).resolve(event) == ("aa" * 32, "bb" * 32)


def test_incomplete_user_scope_index_blocks_fanout():
    event = make("UserKeyRotated", {"userId": b"\x09" * 32, "userVersion": 2})
    with pytest.raises(IncompleteResourceIndex):
        AffectedResourceResolver([], complete=False).resolve(event)


def test_audit_only_has_no_jobs():
    event = make("UserRegistered", {"userId": b"\x09" * 32})
    assert AffectedResourceResolver([], complete=False).resolve(event) == ()
