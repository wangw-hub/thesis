from dataclasses import dataclass

from epoch_auth_r3.storage.references import ObjectReferenceV1

from .models import HeaderCoreV1


@dataclass(frozen=True)
class HeaderBuildContextV1:
    chain_id: int
    authorization_contract: str
    header_registry: str
    resource_id: str
    body_version: int
    policy_digest: str
    epoch: int
    state_version: int
    header_version: int
    key_version: int
    previous_header_digest: str | None
    issuer_key_id: str


@dataclass(frozen=True)
class HeaderVerificationContextV1:
    expected_chain_id: int
    expected_authorization_contract: str
    expected_header_registry: str
    expected_resource_id: str
    expected_policy_digest: str
    expected_epoch: int
    expected_state_version: int
    expected_header_version: int
    expected_body_version: int
    expected_key_version: int
    expected_body_reference: ObjectReferenceV1
    expected_previous_header_digest: str | None
    trusted_issuer_public_key: bytes
    trusted_issuer_key_id: str


@dataclass(frozen=True)
class RecipientPublicKeyV1:
    recipient_key_id: str
    user_version: int
    public_key: bytes


def verification_context_for(
    core: HeaderCoreV1, trusted_public_key: bytes, trusted_key_id: str
) -> HeaderVerificationContextV1:
    return HeaderVerificationContextV1(
        core.chain_id, core.authorization_contract, core.header_registry,
        core.resource_id, core.policy_digest, core.epoch, core.state_version,
        core.header_version, core.body_version, core.key_version, core.body_reference,
        core.previous_header_digest, trusted_public_key, trusted_key_id,
    )
