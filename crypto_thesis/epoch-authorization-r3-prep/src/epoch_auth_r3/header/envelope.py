from __future__ import annotations

from dataclasses import dataclass

from epoch_auth_r3.crypto.hpke_provider import PyHPKEProvider, build_hpke_info_v1
from epoch_auth_r3.serialization.base64url import decode, encode
from epoch_auth_r3.serialization.canonical_types import normalize_hex32
from epoch_auth_r3.serialization.jcs_adapter import canonicalize, parse_strict

from .context import HeaderBuildContextV1, RecipientPublicKeyV1
from .exceptions import HeaderErrorCode, HeaderValidationError
from .models import RecipientEnvelopeV1
from .schema_v1 import CK_PAYLOAD_VERSION, ENVELOPE_AAD_DOMAIN, HPKE_SUITE

PAYLOAD_FIELDS = {
    "payloadVersion", "contentKey", "resourceId", "bodyVersion", "keyVersion",
    "bodyDigest", "policyDigest", "epoch",
}


@dataclass(frozen=True)
class CKEnvelopePayloadV1:
    payload_version: int
    content_key: bytes
    resource_id: str
    body_version: int
    key_version: int
    body_digest: str
    policy_digest: str
    epoch: int

    def to_canonical_dict(self) -> dict:
        return {
            "bodyDigest": self.body_digest, "bodyVersion": self.body_version,
            "contentKey": encode(self.content_key), "epoch": self.epoch,
            "keyVersion": self.key_version, "payloadVersion": self.payload_version,
            "policyDigest": self.policy_digest, "resourceId": self.resource_id,
        }

    def to_canonical_bytes(self) -> bytes:
        return canonicalize(self.to_canonical_dict())

    @classmethod
    def from_strict_bytes(cls, value: bytes) -> "CKEnvelopePayloadV1":
        try:
            data = parse_strict(value)
            if not isinstance(data, dict) or set(data) != PAYLOAD_FIELDS:
                raise HeaderValidationError(HeaderErrorCode.HPKE_CONTEXT_MISMATCH)
            result = cls(
                data["payloadVersion"], decode(data["contentKey"]),
                normalize_hex32(data["resourceId"]), data["bodyVersion"], data["keyVersion"],
                normalize_hex32(data["bodyDigest"]), normalize_hex32(data["policyDigest"]),
                data["epoch"],
            )
            if result.payload_version != CK_PAYLOAD_VERSION or len(result.content_key) != 32:
                raise HeaderValidationError(HeaderErrorCode.HPKE_CONTEXT_MISMATCH)
            if any(type(x) is not int or x < 0 for x in (result.body_version, result.key_version, result.epoch)):
                raise HeaderValidationError(HeaderErrorCode.HPKE_CONTEXT_MISMATCH)
            return result
        except HeaderValidationError:
            raise
        except (TypeError, ValueError) as exc:
            raise HeaderValidationError(HeaderErrorCode.HPKE_CONTEXT_MISMATCH) from exc


def hpke_context_dict(context: HeaderBuildContextV1, recipient_key_id: str, user_version: int) -> dict:
    return {
        "schemaVersion": 1, "chainId": context.chain_id,
        "authorizationContract": context.authorization_contract,
        "headerRegistry": context.header_registry, "resourceId": context.resource_id,
        "bodyVersion": context.body_version, "policyDigest": context.policy_digest,
        "epoch": context.epoch, "stateVersion": context.state_version,
        "headerVersion": context.header_version, "keyVersion": context.key_version,
        "recipientKeyId": recipient_key_id, "userVersion": user_version,
    }


def hpke_info(context: HeaderBuildContextV1, recipient_key_id: str, user_version: int) -> bytes:
    return build_hpke_info_v1(hpke_context_dict(context, recipient_key_id, user_version))


def hpke_aad(
    context: HeaderBuildContextV1, recipient_key_id: str, user_version: int, body_digest: str
) -> bytes:
    return canonicalize({
        "bodyDigest": normalize_hex32(body_digest),
        "context": hpke_context_dict(context, recipient_key_id, user_version),
        "domain": ENVELOPE_AAD_DOMAIN,
    })


def seal_content_key(
    provider: PyHPKEProvider,
    *,
    context: HeaderBuildContextV1,
    recipient: RecipientPublicKeyV1,
    content_key: bytes,
    body_digest: str,
) -> RecipientEnvelopeV1:
    payload = CKEnvelopePayloadV1(
        CK_PAYLOAD_VERSION, content_key, context.resource_id, context.body_version,
        context.key_version, body_digest, context.policy_digest, context.epoch,
    )
    result = provider.seal_base(
        recipient.public_key, payload.to_canonical_bytes(),
        hpke_info(context, recipient.recipient_key_id, recipient.user_version),
        hpke_aad(context, recipient.recipient_key_id, recipient.user_version, body_digest),
    )
    return RecipientEnvelopeV1(
        1, recipient.recipient_key_id, recipient.user_version, HPKE_SUITE,
        result.enc, result.ciphertext,
    )
