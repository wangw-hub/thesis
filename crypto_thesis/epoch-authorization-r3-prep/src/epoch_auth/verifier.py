"""Shared deterministic capability verification flow."""

from __future__ import annotations

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from .audit import AuditEvent, AuditLog
from .baseline_i import BaselineIExecutor
from .blockchain.errors import GatewayUnavailable
from .errors import RejectCode
from .keys import user_key_id, verify
from .models import (
    AuthorizationDecision,
    Operation,
    ResourceStatus,
    SignedCapability,
    UserStatus,
)
from .nonce_store import NonceStore
from .proposed_c import ProposedCExecutor
from .serialization import encode_capability
from .state_store import PolicyRepository, StateStore

PolicyExecutor = BaselineIExecutor | ProposedCExecutor


class CapabilityVerifier:
    """Verify CAP1 with one frozen rejection order and atomic nonce consumption."""

    def __init__(
        self,
        *,
        issuer_public_key: Ed25519PublicKey,
        state_store: StateStore,
        policies: PolicyRepository,
        nonce_store: NonceStore,
        executor: PolicyExecutor,
        chain_id: int | None = None,
        contract_address: bytes | None = None,
        audit_log: AuditLog | None = None,
    ) -> None:
        self.issuer_public_key = issuer_public_key
        self.state_store = state_store
        self.policies = policies
        self.nonce_store = nonce_store
        self.executor = executor
        self.chain_id = chain_id
        self.contract_address = contract_address
        self.audit_log = audit_log or AuditLog()

    def _reject(
        self, cap: SignedCapability, code: RejectCode, now: int
    ) -> AuthorizationDecision:
        self.audit_log.append(
            AuditEvent(
                "VERIFY", cap.payload.resource_id, cap.payload.epoch, False, code, now
            )
        )
        return AuthorizationDecision(False, code)

    def verify(
        self,
        cap: SignedCapability,
        *,
        user_id: str,
        user_public_key: bytes,
        operation: Operation,
        now: int,
    ) -> AuthorizationDecision:
        """Verify all signed and current-state bindings before consuming the nonce."""

        try:
            if encode_capability(cap.payload) != cap.payload_bytes:
                return self._reject(cap, RejectCode.MALFORMED_TOKEN, now)
            verify(self.issuer_public_key, cap.signature, cap.payload_bytes)
        except InvalidSignature:
            return self._reject(cap, RejectCode.INVALID_SIGNATURE, now)

        payload = cap.payload
        try:
            resource, user = self.state_store.get_authorization_state(
                payload.resource_id, user_id
            )
        except GatewayUnavailable:
            return self._reject(cap, RejectCode.SYSTEM_STATE_UNAVAILABLE, now)
        if resource is None:
            return self._reject(cap, RejectCode.RESOURCE_NOT_FOUND, now)
        if resource.status is not ResourceStatus.ACTIVE:
            return self._reject(cap, RejectCode.RESOURCE_INACTIVE, now)
        if user is None:
            return self._reject(cap, RejectCode.USER_NOT_FOUND, now)
        if user.status is not UserStatus.ACTIVE:
            return self._reject(cap, RejectCode.USER_INACTIVE, now)
        if payload.policy_digest != resource.policy_digest:
            return self._reject(cap, RejectCode.POLICY_DIGEST_MISMATCH, now)
        if payload.epoch != resource.epoch:
            return self._reject(cap, RejectCode.EPOCH_MISMATCH, now)
        if self.chain_id is not None or self.contract_address is not None:
            binding = payload.chain_binding
            if (
                binding is None
                or binding.chain_id != self.chain_id
                or binding.contract_address != self.contract_address
            ):
                return self._reject(cap, RejectCode.CHAIN_CONTEXT_MISMATCH, now)
            if binding.resource_state_version != resource.updated_version:
                return self._reject(cap, RejectCode.STATE_VERSION_MISMATCH, now)
            if binding.user_version != user.user_version:
                return self._reject(cap, RejectCode.USER_VERSION_MISMATCH, now)
        try:
            presented_key_id = user_key_id(user_public_key)
        except ValueError:
            return self._reject(cap, RejectCode.USER_KEY_MISMATCH, now)
        if payload.user_key_id != presented_key_id or user.user_key_id != presented_key_id:
            return self._reject(cap, RejectCode.USER_KEY_MISMATCH, now)
        if payload.operation is not operation:
            return self._reject(cap, RejectCode.OPERATION_MISMATCH, now)
        if now < payload.not_before:
            return self._reject(cap, RejectCode.NOT_YET_VALID, now)
        if now >= payload.expires_at:
            return self._reject(cap, RejectCode.EXPIRED, now)
        policy = self.policies.get(resource.policy_digest)
        if policy is None:
            return self._reject(cap, RejectCode.POLICY_DIGEST_MISMATCH, now)
        if not self.executor.validate_binding(
            policy, now, payload.matched_node, payload.cover_version
        ):
            return self._reject(cap, RejectCode.TIME_POLICY_DENIED, now)
        if not self.nonce_store.consume_once(
            payload.resource_id, payload.epoch, payload.nonce
        ):
            return self._reject(cap, RejectCode.NONCE_REPLAY, now)
        self.audit_log.append(
            AuditEvent("VERIFY", payload.resource_id, payload.epoch, True, None, now)
        )
        return AuthorizationDecision(True, None, cap)
