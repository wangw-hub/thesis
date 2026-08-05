"""Replaceable confirmed-state and policy repository interfaces."""

from __future__ import annotations

from dataclasses import replace
from threading import RLock
from typing import Protocol

from time_policy.models import CompiledPolicy

from .errors import StateTransitionError
from .models import ResourceState, ResourceStatus, UserState, UserStatus


class StateStore(Protocol):
    """Abstract state interface later replaceable by a Besu gateway."""

    def get_resource(self, resource_id: str) -> ResourceState | None: ...
    def get_authorization_state(
        self, resource_id: str, user_id: str
    ) -> tuple[ResourceState | None, UserState | None]: ...
    def register_resource(self, state: ResourceState) -> None: ...
    def update_policy(self, resource_id: str, policy_digest: bytes) -> ResourceState: ...
    def advance_epoch(self, resource_id: str) -> ResourceState: ...
    def set_status(self, resource_id: str, status: ResourceStatus) -> ResourceState: ...
    def get_user(self, user_id: str) -> UserState | None: ...
    def register_user(self, state: UserState) -> None: ...
    def rotate_user_key(self, user_id: str, user_key_id: bytes) -> UserState: ...
    def set_user_status(self, user_id: str, status: UserStatus) -> UserState: ...


class InMemoryStateStore:
    """Thread-safe local model of confirmed ledger state."""

    def __init__(self) -> None:
        self._resources: dict[str, ResourceState] = {}
        self._users: dict[str, UserState] = {}
        self._lock = RLock()

    def get_resource(self, resource_id: str) -> ResourceState | None:
        """Return one immutable resource snapshot."""

        with self._lock:
            return self._resources.get(resource_id)

    def get_authorization_state(
        self, resource_id: str, user_id: str
    ) -> tuple[ResourceState | None, UserState | None]:
        """Read resource and user under one lock."""

        with self._lock:
            return self._resources.get(resource_id), self._users.get(user_id)

    def register_resource(self, state: ResourceState) -> None:
        """Register a new active resource."""

        if state.status is not ResourceStatus.ACTIVE:
            raise StateTransitionError("new resource must be ACTIVE")
        with self._lock:
            if state.resource_id in self._resources:
                raise StateTransitionError("resource already exists")
            self._resources[state.resource_id] = state

    def _mutable_resource(self, resource_id: str) -> ResourceState:
        state = self._resources.get(resource_id)
        if state is None:
            raise StateTransitionError("resource does not exist")
        if state.status is ResourceStatus.REVOKED:
            raise StateTransitionError("REVOKED is terminal")
        return state

    def update_policy(self, resource_id: str, policy_digest: bytes) -> ResourceState:
        """Bind a new policy and atomically advance the Epoch."""

        with self._lock:
            state = self._mutable_resource(resource_id)
            updated = replace(
                state,
                policy_digest=policy_digest,
                epoch=state.epoch + 1,
                updated_version=state.updated_version + 1,
            )
            self._resources[resource_id] = updated
            return updated

    def advance_epoch(self, resource_id: str) -> ResourceState:
        """Atomically increase the monotonic authorization version."""

        with self._lock:
            state = self._mutable_resource(resource_id)
            updated = replace(
                state,
                epoch=state.epoch + 1,
                updated_version=state.updated_version + 1,
            )
            self._resources[resource_id] = updated
            return updated

    def set_status(self, resource_id: str, status: ResourceStatus) -> ResourceState:
        """Apply a legal lifecycle transition and invalidate old capabilities."""

        with self._lock:
            state = self._mutable_resource(resource_id)
            legal = {
                ResourceStatus.ACTIVE: {ResourceStatus.SUSPENDED, ResourceStatus.REVOKED},
                ResourceStatus.SUSPENDED: {ResourceStatus.ACTIVE, ResourceStatus.REVOKED},
            }
            if status not in legal[state.status]:
                raise StateTransitionError(f"illegal transition {state.status} -> {status}")
            updated = replace(
                state,
                status=status,
                epoch=state.epoch + 1,
                updated_version=state.updated_version + 1,
            )
            self._resources[resource_id] = updated
            return updated

    def get_user(self, user_id: str) -> UserState | None:
        """Return one immutable user snapshot."""

        with self._lock:
            return self._users.get(user_id)

    def register_user(self, state: UserState) -> None:
        """Register a new active user."""

        if state.status is not UserStatus.ACTIVE:
            raise StateTransitionError("new user must be ACTIVE")
        with self._lock:
            if state.user_id in self._users:
                raise StateTransitionError("user already exists")
            self._users[state.user_id] = state

    def set_user_status(self, user_id: str, status: UserStatus) -> UserState:
        """Apply a legal user lifecycle transition."""

        with self._lock:
            state = self._users.get(user_id)
            if state is None:
                raise StateTransitionError("user does not exist")
            legal = {
                UserStatus.ACTIVE: {UserStatus.SUSPENDED, UserStatus.REVOKED},
                # This prototype has no user-version field in CAP1. Reactivation
                # would otherwise resurrect an unconsumed pre-suspension token.
                UserStatus.SUSPENDED: {UserStatus.REVOKED},
                UserStatus.REVOKED: set(),
            }
            if status not in legal[state.status]:
                raise StateTransitionError(f"illegal transition {state.status} -> {status}")
            updated = replace(state, status=status, user_version=state.user_version + 1)
            self._users[user_id] = updated
            return updated

    def rotate_user_key(self, user_id: str, user_key_id: bytes) -> UserState:
        """Rotate a user key fingerprint and invalidate prior capabilities."""

        if not isinstance(user_key_id, bytes) or len(user_key_id) != 32:
            raise ValueError("user_key_id must contain 32 bytes")
        with self._lock:
            state = self._users.get(user_id)
            if state is None:
                raise StateTransitionError("user does not exist")
            if state.status is UserStatus.REVOKED:
                raise StateTransitionError("REVOKED is terminal")
            updated = replace(
                state,
                user_key_id=user_key_id,
                user_version=state.user_version + 1,
            )
            self._users[user_id] = updated
            return updated


class PolicyRepository:
    """Local digest-addressed repository for compiled policies."""

    def __init__(self) -> None:
        self._policies: dict[bytes, CompiledPolicy] = {}

    def add(self, policy: CompiledPolicy) -> None:
        """Store a compiled policy by its stable semantic digest."""

        self._policies[policy.digest] = policy

    def get(self, digest: bytes) -> CompiledPolicy | None:
        """Load a compiled policy by digest."""

        return self._policies.get(digest)
