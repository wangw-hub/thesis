from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass

from epoch_auth_r3.crypto.aead import aes256_gcm_decrypt, aes256_gcm_encrypt
from epoch_auth_r3.crypto.exceptions import CryptoValidationError
from epoch_auth_r3.crypto.key_material import require_length
from epoch_auth_r3.serialization.base64url import decode, encode
from epoch_auth_r3.serialization.canonical_types import (
    normalize_address,
    normalize_hex32,
    require_safe_integer,
)
from epoch_auth_r3.serialization.jcs_adapter import (
    canonicalize,
    parse_strict,
    require_exact_fields,
)


FIELDS = {
    "schemaVersion",
    "protectionSuite",
    "protectionKeyVersion",
    "chainId",
    "authorizationContract",
    "headerRegistry",
    "resourceId",
    "bodyVersion",
    "keyVersion",
    "nonce",
    "ciphertext",
    "createdAt",
    "metadataDigest",
}


@dataclass(frozen=True)
class EncryptedCKRecordV1:
    schema_version: int
    protection_suite: str
    protection_key_version: int
    chain_id: int
    authorization_contract: str
    header_registry: str
    resource_id: str
    body_version: int
    key_version: int
    nonce: bytes
    ciphertext: bytes
    created_at: str
    metadata_digest: str

    def to_dict(self) -> dict:
        return {
            "authorizationContract": self.authorization_contract,
            "bodyVersion": self.body_version,
            "chainId": self.chain_id,
            "ciphertext": encode(self.ciphertext),
            "createdAt": self.created_at,
            "headerRegistry": self.header_registry,
            "keyVersion": self.key_version,
            "metadataDigest": self.metadata_digest,
            "nonce": encode(self.nonce),
            "protectionKeyVersion": self.protection_key_version,
            "protectionSuite": self.protection_suite,
            "resourceId": self.resource_id,
            "schemaVersion": self.schema_version,
        }

    def to_json(self) -> bytes:
        return canonicalize(self.to_dict())

    @classmethod
    def from_json(cls, value: str | bytes) -> "EncryptedCKRecordV1":
        data = parse_strict(value)
        require_exact_fields(data, FIELDS)
        if data["schemaVersion"] != 1 or data["protectionSuite"] != "AES-256-GCM":
            raise CryptoValidationError("unsupported CK record suite/version")
        record = cls(
            1,
            "AES-256-GCM",
            require_safe_integer(data["protectionKeyVersion"], "protectionKeyVersion"),
            require_safe_integer(data["chainId"], "chainId"),
            normalize_address(data["authorizationContract"]),
            normalize_address(data["headerRegistry"]),
            normalize_hex32(data["resourceId"]),
            require_safe_integer(data["bodyVersion"], "bodyVersion"),
            require_safe_integer(data["keyVersion"], "keyVersion"),
            decode(data["nonce"]),
            decode(data["ciphertext"]),
            data["createdAt"],
            normalize_hex32(data["metadataDigest"]),
        )
        require_length(record.nonce, 12, "CK record nonce")
        if len(record.ciphertext) != 48:
            raise CryptoValidationError("wrapped 32-byte CK must be 48 bytes")
        return record


def _metadata(context: dict) -> dict:
    return {
        "authorizationContract": normalize_address(context["authorizationContract"]),
        "bodyVersion": require_safe_integer(context["bodyVersion"], "bodyVersion"),
        "chainId": require_safe_integer(context["chainId"], "chainId"),
        "headerRegistry": normalize_address(context["headerRegistry"]),
        "keyVersion": require_safe_integer(context["keyVersion"], "keyVersion"),
        "protectionKeyVersion": require_safe_integer(
            context["protectionKeyVersion"], "protectionKeyVersion"
        ),
        "resourceId": normalize_hex32(context["resourceId"]),
        "schemaVersion": 1,
    }


def _aad(metadata: dict) -> bytes:
    return canonicalize({"domain": "EPOCH_AUTH_R3_CK_PROTECTION_V1", **metadata})


def wrap_content_key(
    root_kek: bytes,
    ck: bytes,
    context: dict,
    *,
    created_at: str,
    test_nonce: bytes | None = None,
) -> EncryptedCKRecordV1:
    require_length(root_kek, 32, "ROOT_KEK")
    require_length(ck, 32, "CK")
    metadata = _metadata(context)
    nonce = os.urandom(12) if test_nonce is None else require_length(
        test_nonce, 12, "test nonce"
    )
    metadata_digest = hashlib.sha256(canonicalize(metadata)).hexdigest()
    return EncryptedCKRecordV1(
        1,
        "AES-256-GCM",
        metadata["protectionKeyVersion"],
        metadata["chainId"],
        metadata["authorizationContract"],
        metadata["headerRegistry"],
        metadata["resourceId"],
        metadata["bodyVersion"],
        metadata["keyVersion"],
        nonce,
        aes256_gcm_encrypt(root_kek, nonce, ck, _aad(metadata)),
        created_at,
        metadata_digest,
    )


def unwrap_content_key(root_kek: bytes, record: EncryptedCKRecordV1) -> bytes:
    if record.schema_version != 1 or record.protection_suite != "AES-256-GCM":
        raise CryptoValidationError("unsupported CK record suite/version")
    metadata = _metadata(
        {
            "authorizationContract": record.authorization_contract,
            "bodyVersion": record.body_version,
            "chainId": record.chain_id,
            "headerRegistry": record.header_registry,
            "keyVersion": record.key_version,
            "protectionKeyVersion": record.protection_key_version,
            "resourceId": record.resource_id,
        }
    )
    if hashlib.sha256(canonicalize(metadata)).hexdigest() != record.metadata_digest:
        raise CryptoValidationError("metadata digest mismatch")
    return aes256_gcm_decrypt(
        root_kek, record.nonce, record.ciphertext, _aad(metadata)
    )
