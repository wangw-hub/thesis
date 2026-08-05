"""Shared capability issuance flow."""

from __future__ import annotations

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from .audit import AuditEvent, AuditLog
from .baseline_i import BaselineIExecutor
from .blockchain.errors import GatewayUnavailable
from .errors import RejectCode
from .keys import user_key_id
from .models import (
    AuthorizationDecision,
    AuthorizationRequest,
    CapabilityPayload,
    ChainBinding,
    ResourceStatus,
    UserStatus,
)
from .proposed_c import ProposedCExecutor
from .state_store import PolicyRepository, StateStore
from .token import sign_capability

PolicyExecutor = BaselineIExecutor | ProposedCExecutor


class CapabilityIssuer:
    """Issue CAP1 tokens with a pluggable, frozen policy execution step."""

    def __init__(
        self,
        *,
        issuer_id: str,
        signing_key: Ed25519PrivateKey,
        state_store: StateStore,
        policies: PolicyRepository,
        executor: PolicyExecutor,
        chain_id: int | None = None,
        contract_address: bytes | None = None,
        audit_log: AuditLog | None = None,
    ) -> None:
        self.issuer_id = issuer_id
        self.signing_key = signing_key
        self.state_store = state_store
        self.policies = policies
        self.executor = executor
        self.chain_id = chain_id
        self.contract_address = contract_address
        self.audit_log = audit_log or AuditLog()

    def _reject(
        self, request: AuthorizationRequest, code: RejectCode, epoch: int | None = None
    ) -> AuthorizationDecision:
        self.audit_log.append(
            AuditEvent("ISSUE", request.resource_id, epoch, False, code, request.now)
        )
        return AuthorizationDecision(False, code)

    def issue(self, request: AuthorizationRequest) -> AuthorizationDecision:
        """Issue a token only from current active state and an allowed time slot."""

        try:
            resource, user = self.state_store.get_authorization_state(
                request.resource_id, request.user_id
            )
        except GatewayUnavailable:
            return self._reject(request, RejectCode.SYSTEM_STATE_UNAVAILABLE)
        if resource is None:
            return self._reject(request, RejectCode.RESOURCE_NOT_FOUND)
        if resource.status is not ResourceStatus.ACTIVE:
            return self._reject(request, RejectCode.RESOURCE_INACTIVE, resource.epoch)
        if user is None:
            return self._reject(request, RejectCode.USER_NOT_FOUND, resource.epoch)
        if user.status is not UserStatus.ACTIVE:
            return self._reject(request, RejectCode.USER_INACTIVE, resource.epoch)
        request_key_id = user_key_id(request.user_public_key)
        if request_key_id != user.user_key_id:
            return self._reject(request, RejectCode.USER_KEY_MISMATCH, resource.epoch)
        policy = self.policies.get(resource.policy_digest)
        if policy is None or policy.digest != resource.policy_digest:
            return self._reject(
                request, RejectCode.POLICY_DIGEST_MISMATCH, resource.epoch
            )
        match = self.executor.evaluate(policy, request.now)
        if not match.allowed or match.window_end is None:
            return self._reject(request, RejectCode.TIME_POLICY_DENIED, resource.epoch)
        expires_at = min(request.now + request.ttl, match.window_end)
        if expires_at <= request.now:
            return self._reject(request, RejectCode.TIME_POLICY_DENIED, resource.epoch)
        # Re-read the same logical pair immediately before signing. A Besu
        # gateway pins each pair to one confirmed block; any intervening state
        # transition aborts issuance rather than signing a stale snapshot.
        try:
            current_resource, current_user = self.state_store.get_authorization_state(
                request.resource_id, request.user_id
            )
        except GatewayUnavailable:
            return self._reject(
                request, RejectCode.SYSTEM_STATE_UNAVAILABLE, resource.epoch
            )
        if current_resource != resource or current_user != user:
            return self._reject(
                request, RejectCode.SYSTEM_STATE_UNAVAILABLE, resource.epoch
            )
        chain_binding = None
        version = 1
        if self.chain_id is not None and self.contract_address is not None:
            version = 2
            chain_binding = ChainBinding(
                self.chain_id,
                self.contract_address,
                resource.updated_version,
                user.user_version,
            )
        payload = CapabilityPayload(
            version=version,
            issuer=self.issuer_id,
            resource_id=resource.resource_id,
            policy_digest=resource.policy_digest,
            epoch=resource.epoch,
            user_key_id=request_key_id,
            operation=request.operation,
            not_before=request.now,
            expires_at=expires_at,
            nonce=request.nonce,
            issued_at=request.now,
            chain_binding=chain_binding,
            matched_node=match.matched_node,
            cover_version=match.cover_version,
        )
        capability = sign_capability(payload, self.signing_key)
        self.audit_log.append(
            AuditEvent("ISSUE", request.resource_id, resource.epoch, True, None, request.now)
        )
        return AuthorizationDecision(True, None, capability)
