from __future__ import annotations

from dataclasses import dataclass

from epoch_auth_r3.serialization.base64url import decode, encode
from epoch_auth_r3.serialization.canonical_types import (
    normalize_address,
    normalize_hex32,
    require_safe_integer,
)
from epoch_auth_r3.serialization.jcs_adapter import canonicalize, parse_strict
from epoch_auth_r3.storage.references import ObjectReferenceV1

from .exceptions import HeaderErrorCode, HeaderValidationError
from .schema_v1 import (
    HEADER_SIGNATURE_DOMAIN,
    HPKE_SUITE,
    RECIPIENT_MODE,
    SCHEMA_VERSION,
    SUITE_ID,
)

CORE_FIELDS = {
    "schemaVersion", "suiteId", "chainId", "authorizationContract",
    "headerRegistry", "resourceId", "bodyReference", "bodyDigest",
    "bodyVersion", "policyDigest", "epoch", "stateVersion", "headerVersion",
    "keyVersion", "previousHeaderDigest", "recipientMode", "recipientEnvelopes",
}
ENVELOPE_FIELDS = {
    "envelopeVersion", "recipientKeyId", "userVersion", "hpkeSuite", "enc", "ciphertext",
}
SIGNATURE_FIELDS = {
    "signatureAlgorithm", "issuerKeyId", "signatureDomain", "headerDigest", "signature",
}
SIGNED_FIELDS = {"core", "signature"}


def _exact(value: object, expected: set[str]) -> dict:
    if not isinstance(value, dict):
        raise HeaderValidationError(HeaderErrorCode.INVALID_JSON)
    missing, unknown = expected - set(value), set(value) - expected
    if missing:
        raise HeaderValidationError(HeaderErrorCode.MISSING_FIELD)
    if unknown:
        raise HeaderValidationError(HeaderErrorCode.UNKNOWN_FIELD)
    return value


def _uint(value: object, name: str, *, positive: bool = False) -> int:
    try:
        result = require_safe_integer(value, name)
    except (TypeError, ValueError) as exc:
        raise HeaderValidationError(HeaderErrorCode.INVALID_JSON) from exc
    if result < (1 if positive else 0):
        raise HeaderValidationError(HeaderErrorCode.INVALID_JSON)
    return result


@dataclass(frozen=True)
class RecipientEnvelopeV1:
    envelope_version: int
    recipient_key_id: str
    user_version: int
    hpke_suite: str
    enc: bytes
    ciphertext: bytes

    def __post_init__(self) -> None:
        if self.envelope_version != 1 or self.hpke_suite != HPKE_SUITE:
            raise HeaderValidationError(HeaderErrorCode.UNSUPPORTED_SUITE)
        normalize_hex32(self.recipient_key_id)
        _uint(self.user_version, "userVersion")
        if not isinstance(self.enc, bytes) or len(self.enc) != 32:
            raise HeaderValidationError(HeaderErrorCode.HPKE_CONTEXT_MISMATCH)
        if not isinstance(self.ciphertext, bytes) or len(self.ciphertext) < 17:
            raise HeaderValidationError(HeaderErrorCode.HPKE_CONTEXT_MISMATCH)

    def to_canonical_dict(self) -> dict:
        return {
            "ciphertext": encode(self.ciphertext), "enc": encode(self.enc),
            "envelopeVersion": self.envelope_version, "hpkeSuite": self.hpke_suite,
            "recipientKeyId": self.recipient_key_id, "userVersion": self.user_version,
        }

    @classmethod
    def from_strict_dict(cls, value: object) -> "RecipientEnvelopeV1":
        data = _exact(value, ENVELOPE_FIELDS)
        try:
            return cls(data["envelopeVersion"], normalize_hex32(data["recipientKeyId"]),
                       _uint(data["userVersion"], "userVersion"), data["hpkeSuite"],
                       decode(data["enc"]), decode(data["ciphertext"]))
        except HeaderValidationError:
            raise
        except (TypeError, ValueError) as exc:
            raise HeaderValidationError(HeaderErrorCode.INVALID_JSON) from exc


@dataclass(frozen=True)
class HeaderCoreV1:
    schema_version: int
    suite_id: str
    chain_id: int
    authorization_contract: str
    header_registry: str
    resource_id: str
    body_reference: ObjectReferenceV1
    body_digest: str
    body_version: int
    policy_digest: str
    epoch: int
    state_version: int
    header_version: int
    key_version: int
    previous_header_digest: str | None
    recipient_mode: str
    recipient_envelopes: tuple[RecipientEnvelopeV1, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SCHEMA_VERSION:
            raise HeaderValidationError(HeaderErrorCode.INVALID_SCHEMA_VERSION)
        if self.suite_id != SUITE_ID or self.recipient_mode != RECIPIENT_MODE:
            raise HeaderValidationError(HeaderErrorCode.UNSUPPORTED_SUITE)
        _uint(self.chain_id, "chainId")
        normalize_address(self.authorization_contract)
        normalize_address(self.header_registry)
        normalize_hex32(self.resource_id)
        normalize_hex32(self.body_digest)
        normalize_hex32(self.policy_digest)
        for name, value in (
            ("bodyVersion", self.body_version), ("epoch", self.epoch),
            ("stateVersion", self.state_version), ("headerVersion", self.header_version),
            ("keyVersion", self.key_version),
        ):
            _uint(value, name, positive=name in {"bodyVersion", "headerVersion", "keyVersion"})
        if self.key_version != self.body_version:
            raise HeaderValidationError(HeaderErrorCode.KEY_BODY_VERSION_MISMATCH)
        if self.body_reference.object_kind.value != "BODY":
            raise HeaderValidationError(HeaderErrorCode.INVALID_BODY_REFERENCE)
        if self.body_reference.digest_hex != self.body_digest:
            raise HeaderValidationError(HeaderErrorCode.BODY_DIGEST_MISMATCH)
        if self.header_version == 1:
            if self.body_version != 1 or self.key_version != 1:
                raise HeaderValidationError(HeaderErrorCode.KEY_BODY_VERSION_MISMATCH)
            if self.previous_header_digest is not None:
                raise HeaderValidationError(HeaderErrorCode.PREVIOUS_HEADER_DIGEST_MISMATCH)
        elif self.previous_header_digest is None:
            raise HeaderValidationError(HeaderErrorCode.PREVIOUS_HEADER_DIGEST_MISMATCH)
        elif normalize_hex32(self.previous_header_digest) != self.previous_header_digest:
            raise HeaderValidationError(HeaderErrorCode.PREVIOUS_HEADER_DIGEST_MISMATCH)
        if not self.recipient_envelopes:
            raise HeaderValidationError(HeaderErrorCode.RECIPIENT_LIST_EMPTY)
        keys = [item.recipient_key_id for item in self.recipient_envelopes]
        if len(keys) != len(set(keys)):
            raise HeaderValidationError(HeaderErrorCode.RECIPIENT_DUPLICATE)
        ordered = sorted(self.recipient_envelopes, key=lambda item: (item.recipient_key_id, item.user_version))
        if list(self.recipient_envelopes) != ordered:
            raise HeaderValidationError(HeaderErrorCode.RECIPIENT_ORDER_INVALID)

    def to_canonical_dict(self) -> dict:
        return {
            "authorizationContract": self.authorization_contract,
            "bodyDigest": self.body_digest,
            "bodyReference": self.body_reference.to_canonical_dict(),
            "bodyVersion": self.body_version, "chainId": self.chain_id,
            "epoch": self.epoch, "headerRegistry": self.header_registry,
            "headerVersion": self.header_version, "keyVersion": self.key_version,
            "policyDigest": self.policy_digest,
            "previousHeaderDigest": self.previous_header_digest,
            "recipientEnvelopes": [x.to_canonical_dict() for x in self.recipient_envelopes],
            "recipientMode": self.recipient_mode, "resourceId": self.resource_id,
            "schemaVersion": self.schema_version, "stateVersion": self.state_version,
            "suiteId": self.suite_id,
        }

    def to_canonical_bytes(self) -> bytes:
        return canonicalize(self.to_canonical_dict())

    @classmethod
    def from_strict_dict(cls, value: object) -> "HeaderCoreV1":
        data = _exact(value, CORE_FIELDS)
        try:
            previous = data["previousHeaderDigest"]
            if previous is not None:
                previous = normalize_hex32(previous)
            return cls(
                data["schemaVersion"], data["suiteId"], _uint(data["chainId"], "chainId"),
                normalize_address(data["authorizationContract"]),
                normalize_address(data["headerRegistry"]), normalize_hex32(data["resourceId"]),
                ObjectReferenceV1.from_strict_dict(data["bodyReference"]),
                normalize_hex32(data["bodyDigest"]), _uint(data["bodyVersion"], "bodyVersion", positive=True),
                normalize_hex32(data["policyDigest"]), _uint(data["epoch"], "epoch"),
                _uint(data["stateVersion"], "stateVersion"),
                _uint(data["headerVersion"], "headerVersion", positive=True),
                _uint(data["keyVersion"], "keyVersion", positive=True), previous,
                data["recipientMode"],
                tuple(RecipientEnvelopeV1.from_strict_dict(x) for x in data["recipientEnvelopes"]),
            )
        except HeaderValidationError:
            raise
        except (TypeError, ValueError) as exc:
            raise HeaderValidationError(HeaderErrorCode.INVALID_JSON) from exc


@dataclass(frozen=True)
class HeaderSignatureV1:
    signature_algorithm: str
    issuer_key_id: str
    signature_domain: str
    header_digest: str
    signature: bytes

    def __post_init__(self) -> None:
        if self.signature_algorithm != "Ed25519" or self.signature_domain != HEADER_SIGNATURE_DOMAIN:
            raise HeaderValidationError(HeaderErrorCode.UNSUPPORTED_SUITE)
        if not isinstance(self.issuer_key_id, str) or not self.issuer_key_id:
            raise HeaderValidationError(HeaderErrorCode.ISSUER_KEY_ID_MISMATCH)
        normalize_hex32(self.header_digest)
        if not isinstance(self.signature, bytes) or len(self.signature) != 64:
            raise HeaderValidationError(HeaderErrorCode.HEADER_SIGNATURE_INVALID)

    def to_canonical_dict(self) -> dict:
        return {
            "headerDigest": self.header_digest, "issuerKeyId": self.issuer_key_id,
            "signature": encode(self.signature), "signatureAlgorithm": self.signature_algorithm,
            "signatureDomain": self.signature_domain,
        }

    @classmethod
    def from_strict_dict(cls, value: object) -> "HeaderSignatureV1":
        data = _exact(value, SIGNATURE_FIELDS)
        try:
            return cls(data["signatureAlgorithm"], data["issuerKeyId"], data["signatureDomain"],
                       normalize_hex32(data["headerDigest"]), decode(data["signature"]))
        except HeaderValidationError:
            raise
        except (TypeError, ValueError) as exc:
            raise HeaderValidationError(HeaderErrorCode.INVALID_JSON) from exc


@dataclass(frozen=True)
class SignedVersionedHeaderV1:
    core: HeaderCoreV1
    signature: HeaderSignatureV1

    def to_canonical_dict(self) -> dict:
        return {"core": self.core.to_canonical_dict(), "signature": self.signature.to_canonical_dict()}

    def to_canonical_bytes(self) -> bytes:
        return canonicalize(self.to_canonical_dict())

    @classmethod
    def from_strict_json_bytes(cls, value: bytes | str) -> "SignedVersionedHeaderV1":
        try:
            data = _exact(parse_strict(value), SIGNED_FIELDS)
            return cls(HeaderCoreV1.from_strict_dict(data["core"]),
                       HeaderSignatureV1.from_strict_dict(data["signature"]))
        except HeaderValidationError:
            raise
        except (TypeError, ValueError) as exc:
            raise HeaderValidationError(HeaderErrorCode.INVALID_JSON) from exc

    def validate_schema(self) -> None:
        HeaderCoreV1.from_strict_dict(self.core.to_canonical_dict())
        HeaderSignatureV1.from_strict_dict(self.signature.to_canonical_dict())
