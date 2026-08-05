from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from pyhpke import AEADId, CipherSuite, KDFId, KEMId, KEMKeyPair

from .exceptions import IntegrityError
from .key_material import TestOnlyEphemeral, require_length
from epoch_auth_r3.serialization.base64url import encode
from epoch_auth_r3.serialization.canonical_types import (
    normalize_address,
    normalize_hex32,
    require_safe_integer,
)
from epoch_auth_r3.serialization.jcs_adapter import canonicalize


@dataclass(frozen=True)
class HPKESealResult:
    enc: bytes
    ciphertext: bytes


@dataclass(frozen=True)
class HPKESuiteMetadata:
    provider: str = "pyhpke"
    version: str = "0.6.4"
    mode: int = 0
    kem_id: int = 0x0020
    kdf_id: int = 0x0001
    aead_id: int = 0x0001


class HPKEProvider(Protocol):
    def seal_base(
        self, recipient_public_key: bytes, plaintext: bytes, info: bytes, aad: bytes
    ) -> HPKESealResult: ...

    def open_base(
        self,
        recipient_private_key: bytes,
        enc: bytes,
        ciphertext: bytes,
        info: bytes,
        aad: bytes,
    ) -> bytes: ...

    def suite_metadata(self) -> HPKESuiteMetadata: ...


class PyHPKEProvider:
    """Narrow public-API adapter for RFC 9180 Base mode."""

    def __init__(self) -> None:
        self._suite = CipherSuite.new(
            KEMId.DHKEM_X25519_HKDF_SHA256,
            KDFId.HKDF_SHA256,
            AEADId.AES128_GCM,
        )

    def suite_metadata(self) -> HPKESuiteMetadata:
        return HPKESuiteMetadata()

    def seal_base(
        self, recipient_public_key: bytes, plaintext: bytes, info: bytes, aad: bytes
    ) -> HPKESealResult:
        pkr = self._suite.kem.deserialize_public_key(
            require_length(recipient_public_key, 32, "recipient public key")
        )
        enc, sender = self._suite.create_sender_context(pkr, info=bytes(info))
        return HPKESealResult(enc, sender.seal(bytes(plaintext), bytes(aad)))

    def open_base(
        self,
        recipient_private_key: bytes,
        enc: bytes,
        ciphertext: bytes,
        info: bytes,
        aad: bytes,
    ) -> bytes:
        try:
            skr = self._suite.kem.deserialize_private_key(
                require_length(recipient_private_key, 32, "recipient private key")
            )
            recipient = self._suite.create_recipient_context(
                require_length(enc, 32, "enc"), skr, info=bytes(info)
            )
            return recipient.open(bytes(ciphertext), bytes(aad))
        except Exception as exc:
            raise IntegrityError("HPKE_OPEN_FAILED") from exc

    def create_sender_context_for_test(
        self,
        recipient_public_key: bytes,
        info: bytes,
        ephemeral: TestOnlyEphemeral,
    ):
        """Test-only deterministic RFC-vector path; never called by seal_base."""
        pkr = self._suite.kem.deserialize_public_key(recipient_public_key)
        sk = self._suite.kem.deserialize_private_key(ephemeral.private_key)
        pk = self._suite.kem.deserialize_public_key(ephemeral.public_key)
        return self._suite.create_sender_context(
            pkr, info=bytes(info), eks=KEMKeyPair(sk, pk)
        )

    def create_recipient_context_for_test(
        self, recipient_private_key: bytes, enc: bytes, info: bytes
    ):
        skr = self._suite.kem.deserialize_private_key(recipient_private_key)
        return self._suite.create_recipient_context(enc, skr, info=bytes(info))


def build_hpke_info_v1(context: dict) -> bytes:
    """Canonical, public HPKE application context."""
    expected = {
        "authorizationContract",
        "bodyVersion",
        "chainId",
        "epoch",
        "headerRegistry",
        "headerVersion",
        "keyVersion",
        "policyDigest",
        "recipientKeyId",
        "resourceId",
        "schemaVersion",
        "stateVersion",
        "userVersion",
    }
    if set(context) != expected or context["schemaVersion"] != 1:
        raise ValueError("HPKEInfoV1 fields/version mismatch")
    return canonicalize(
        {
            "authorizationContract": normalize_address(
                context["authorizationContract"]
            ),
            "bodyVersion": require_safe_integer(context["bodyVersion"], "bodyVersion"),
            "chainId": require_safe_integer(context["chainId"], "chainId"),
            "domain": "EPOCH_AUTH_R3_HPKE_INFO_V1",
            "epoch": require_safe_integer(context["epoch"], "epoch"),
            "headerRegistry": normalize_address(context["headerRegistry"]),
            "headerVersion": require_safe_integer(
                context["headerVersion"], "headerVersion"
            ),
            "keyVersion": require_safe_integer(context["keyVersion"], "keyVersion"),
            "policyDigest": normalize_hex32(context["policyDigest"]),
            "recipientKeyId": normalize_hex32(context["recipientKeyId"]),
            "resourceId": normalize_hex32(context["resourceId"]),
            "schemaVersion": 1,
            "stateVersion": require_safe_integer(
                context["stateVersion"], "stateVersion"
            ),
            "userVersion": require_safe_integer(context["userVersion"], "userVersion"),
        }
    )
