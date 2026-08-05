from epoch_auth_r3.crypto.hpke_provider import PyHPKEProvider
from epoch_auth_r3.crypto.key_material import require_length
from epoch_auth_r3.serialization.canonical_types import normalize_address, normalize_hex32
from epoch_auth_r3.storage.references import ObjectReferenceV1

from .context import HeaderBuildContextV1, RecipientPublicKeyV1
from .envelope import seal_content_key
from .exceptions import HeaderErrorCode, HeaderValidationError
from .models import HeaderCoreV1, SignedVersionedHeaderV1
from .schema_v1 import RECIPIENT_MODE, SCHEMA_VERSION, SUITE_ID
from .signature import sign_core


class VersionedHeaderBuilderV1:
    def __init__(self, provider: PyHPKEProvider | None = None):
        self.provider = provider or PyHPKEProvider()

    def build(
        self,
        *,
        context: HeaderBuildContextV1,
        body_reference: ObjectReferenceV1,
        content_key: bytes,
        recipients: list[RecipientPublicKeyV1],
        signing_private_seed: bytes,
    ) -> SignedVersionedHeaderV1:
        require_length(content_key, 32, "CK")
        require_length(signing_private_seed, 32, "Header signing private seed")
        if body_reference.object_kind.value != "BODY":
            raise HeaderValidationError(HeaderErrorCode.INVALID_BODY_REFERENCE)
        if not recipients:
            raise HeaderValidationError(HeaderErrorCode.RECIPIENT_LIST_EMPTY)
        normalized = []
        seen = set()
        for recipient in recipients:
            key_id = normalize_hex32(recipient.recipient_key_id)
            if key_id in seen:
                raise HeaderValidationError(HeaderErrorCode.RECIPIENT_DUPLICATE)
            seen.add(key_id)
            if type(recipient.user_version) is not int or recipient.user_version < 0:
                raise HeaderValidationError(HeaderErrorCode.USER_VERSION_MISMATCH)
            require_length(recipient.public_key, 32, "recipient public key")
            normalized.append(recipient)
        normalized.sort(key=lambda item: (item.recipient_key_id, item.user_version))
        context = HeaderBuildContextV1(
            context.chain_id, normalize_address(context.authorization_contract),
            normalize_address(context.header_registry), normalize_hex32(context.resource_id),
            context.body_version, normalize_hex32(context.policy_digest), context.epoch,
            context.state_version, context.header_version, context.key_version,
            None if context.previous_header_digest is None else normalize_hex32(context.previous_header_digest),
            context.issuer_key_id,
        )
        envelopes = tuple(
            seal_content_key(
                self.provider, context=context, recipient=item, content_key=content_key,
                body_digest=body_reference.digest_hex,
            )
            for item in normalized
        )
        core = HeaderCoreV1(
            SCHEMA_VERSION, SUITE_ID, context.chain_id, context.authorization_contract,
            context.header_registry, context.resource_id, body_reference,
            body_reference.digest_hex, context.body_version, context.policy_digest,
            context.epoch, context.state_version, context.header_version,
            context.key_version, context.previous_header_digest, RECIPIENT_MODE, envelopes,
        )
        signed = SignedVersionedHeaderV1(
            core, sign_core(core, signing_private_seed, context.issuer_key_id)
        )
        signed.validate_schema()
        return signed
