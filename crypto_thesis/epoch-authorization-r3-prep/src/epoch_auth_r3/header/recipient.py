from epoch_auth_r3.crypto.exceptions import IntegrityError
from epoch_auth_r3.crypto.hpke_provider import PyHPKEProvider

from .context import HeaderBuildContextV1, HeaderVerificationContextV1
from .envelope import CKEnvelopePayloadV1, hpke_aad, hpke_info
from .exceptions import HeaderErrorCode, HeaderValidationError
from .models import SignedVersionedHeaderV1
from .validator import VersionedHeaderValidatorV1


class RecipientHeaderOpenerV1:
    def __init__(self, provider: PyHPKEProvider | None = None):
        self.provider = provider or PyHPKEProvider()
        self.validator = VersionedHeaderValidatorV1()

    def open_content_key(
        self, *, header: SignedVersionedHeaderV1, recipient_key_id: str,
        user_version: int, recipient_private_key: bytes,
        verification_context: HeaderVerificationContextV1,
    ) -> bytes:
        self.validator.validate(header, verification_context)
        matches = [x for x in header.core.recipient_envelopes if x.recipient_key_id == recipient_key_id]
        if len(matches) != 1:
            raise HeaderValidationError(HeaderErrorCode.RECIPIENT_NOT_FOUND)
        envelope = matches[0]
        if envelope.user_version != user_version:
            raise HeaderValidationError(HeaderErrorCode.USER_VERSION_MISMATCH)
        core = header.core
        build_context = HeaderBuildContextV1(
            core.chain_id, core.authorization_contract, core.header_registry,
            core.resource_id, core.body_version, core.policy_digest, core.epoch,
            core.state_version, core.header_version, core.key_version,
            core.previous_header_digest, header.signature.issuer_key_id,
        )
        try:
            plaintext = self.provider.open_base(
                recipient_private_key, envelope.enc, envelope.ciphertext,
                hpke_info(build_context, recipient_key_id, user_version),
                hpke_aad(build_context, recipient_key_id, user_version, core.body_digest),
            )
        except IntegrityError as exc:
            raise HeaderValidationError(HeaderErrorCode.HPKE_OPEN_FAILED) from exc
        payload = CKEnvelopePayloadV1.from_strict_bytes(plaintext)
        expected = (
            payload.resource_id == core.resource_id
            and payload.body_version == core.body_version
            and payload.key_version == core.key_version
            and payload.body_digest == core.body_digest
            and payload.policy_digest == core.policy_digest
            and payload.epoch == core.epoch
        )
        if not expected:
            raise HeaderValidationError(HeaderErrorCode.HPKE_CONTEXT_MISMATCH)
        return payload.content_key
