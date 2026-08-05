from dataclasses import dataclass

from .context import HeaderVerificationContextV1
from .digest import header_core_digest
from .exceptions import HeaderErrorCode, HeaderValidationError
from .models import SignedVersionedHeaderV1
from .signature import verify_core_signature


@dataclass(frozen=True)
class HeaderValidationResult:
    verified: bool
    header_digest: str


class VersionedHeaderValidatorV1:
    def validate(
        self, header: SignedVersionedHeaderV1, context: HeaderVerificationContextV1
    ) -> HeaderValidationResult:
        header.validate_schema()
        core = header.core
        comparisons = (
            (core.chain_id, context.expected_chain_id, HeaderErrorCode.UNTRUSTED_HEADER),
            (core.authorization_contract, context.expected_authorization_contract, HeaderErrorCode.UNTRUSTED_HEADER),
            (core.header_registry, context.expected_header_registry, HeaderErrorCode.UNTRUSTED_HEADER),
            (core.resource_id, context.expected_resource_id, HeaderErrorCode.INVALID_RESOURCE_ID),
            (core.policy_digest, context.expected_policy_digest, HeaderErrorCode.INVALID_POLICY_DIGEST),
            (core.epoch, context.expected_epoch, HeaderErrorCode.EPOCH_MISMATCH),
            (core.state_version, context.expected_state_version, HeaderErrorCode.STATE_VERSION_MISMATCH),
            (core.header_version, context.expected_header_version, HeaderErrorCode.HEADER_VERSION_MISMATCH),
            (core.body_version, context.expected_body_version, HeaderErrorCode.BODY_VERSION_MISMATCH),
            (core.key_version, context.expected_key_version, HeaderErrorCode.KEY_VERSION_MISMATCH),
            (core.previous_header_digest, context.expected_previous_header_digest, HeaderErrorCode.PREVIOUS_HEADER_DIGEST_MISMATCH),
            (core.body_reference, context.expected_body_reference, HeaderErrorCode.INVALID_BODY_REFERENCE),
        )
        for actual, expected, code in comparisons:
            if actual != expected:
                raise HeaderValidationError(code)
        if core.body_reference.digest_hex != core.body_digest:
            raise HeaderValidationError(HeaderErrorCode.BODY_DIGEST_MISMATCH)
        if header.signature.issuer_key_id != context.trusted_issuer_key_id:
            raise HeaderValidationError(HeaderErrorCode.ISSUER_KEY_ID_MISMATCH)
        verify_core_signature(core, header.signature, context.trusted_issuer_public_key)
        return HeaderValidationResult(True, header_core_digest(core).hex())
