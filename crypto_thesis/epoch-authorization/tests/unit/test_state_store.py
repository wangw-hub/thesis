from __future__ import annotations

import pytest

from epoch_auth.errors import StateTransitionError
from epoch_auth.models import ResourceState, ResourceStatus, UserState, UserStatus
from epoch_auth.state_store import InMemoryStateStore


def test_resource_state_machine_and_epoch_invalidation():
    store = InMemoryStateStore()
    store.register_resource(
        ResourceState("r", "o", b"x" * 32, 1, ResourceStatus.ACTIVE, 1)
    )
    suspended = store.set_status("r", ResourceStatus.SUSPENDED)
    assert (suspended.epoch, suspended.updated_version) == (2, 2)
    active = store.set_status("r", ResourceStatus.ACTIVE)
    assert active.epoch == 3
    revoked = store.set_status("r", ResourceStatus.REVOKED)
    assert revoked.epoch == 4
    with pytest.raises(StateTransitionError):
        store.set_status("r", ResourceStatus.ACTIVE)


def test_policy_update_and_explicit_epoch_are_monotonic():
    store = InMemoryStateStore()
    store.register_resource(
        ResourceState("r", "o", b"x" * 32, 3, ResourceStatus.ACTIVE, 9)
    )
    assert store.update_policy("r", b"y" * 32).epoch == 4
    assert store.advance_epoch("r").epoch == 5


def test_user_state_machine():
    store = InMemoryStateStore()
    store.register_user(UserState("u", b"k" * 32, UserStatus.ACTIVE))
    suspended = store.set_user_status("u", UserStatus.SUSPENDED)
    assert (suspended.status, suspended.user_version) == (UserStatus.SUSPENDED, 2)
    with pytest.raises(StateTransitionError):
        store.set_user_status("u", UserStatus.ACTIVE)
    assert store.set_user_status("u", UserStatus.REVOKED).status is UserStatus.REVOKED
    with pytest.raises(StateTransitionError):
        store.set_user_status("u", UserStatus.ACTIVE)
