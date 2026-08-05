import hashlib
import os

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey

from epoch_auth_r3.body.chunk_crypto import NonceUseRegistry
from epoch_auth_r3.body.format_v1 import (
    BodyEnvelopeV1, EncryptedChunk, decrypt_body, encrypt_body,
)
from epoch_auth_r3.header.builder import VersionedHeaderBuilderV1
from epoch_auth_r3.header.context import (
    HeaderBuildContextV1, RecipientPublicKeyV1, verification_context_for,
)
from epoch_auth_r3.header.models import SignedVersionedHeaderV1
from epoch_auth_r3.header.validator import VersionedHeaderValidatorV1
from epoch_auth_r3.serialization.base64url import decode, encode
from epoch_auth_r3.serialization.jcs_adapter import canonicalize, parse_strict
from epoch_auth_r3.storage import LocalObjectStore, ObjectKind, ObjectReferenceV1
from epoch_auth_r3.storage.ipfs import IpfsReplicaGatewayV1, KuboRpcClient

TEST_HEADER_SEED = b"I" * 32
TEST_CK = b"J" * 32


def body_bytes():
    envelope = encrypt_body(
        plaintext=b"I8 non-sensitive encrypted body fixture", ck=TEST_CK,
        nonce_base=b"I8NONCE!", chain_id=1337, resource_id="33" * 32,
        body_version=1, chunk_size=8, nonce_registry=NonceUseRegistry(),
    )
    return canonicalize({
        "bodyVersion": envelope.body_version, "chainId": envelope.chain_id,
        "chunkCount": envelope.chunk_count, "chunkSize": envelope.chunk_size,
        "chunks": [{"ciphertext": encode(c.ciphertext), "index": c.index,
                    "plaintextLength": c.plaintext_length} for c in envelope.chunks],
        "formatVersion": envelope.format_version,
        "manifestDigest": encode(envelope.manifest_digest),
        "nonceBase": encode(envelope.nonce_base),
        "plaintextLength": envelope.plaintext_length,
        "resourceId": envelope.resource_id,
    })


def build_header(body_reference):
    context = HeaderBuildContextV1(
        1337, "0x" + "11" * 20, "0x" + "22" * 20, "33" * 32, 1,
        "44" * 32, 2, 3, 1, 1, None, "i8-test-header-key",
    )
    recipient_private = X25519PrivateKey.from_private_bytes(b"R" * 32)
    recipient = RecipientPublicKeyV1(
        "55" * 32, 1, recipient_private.public_key().public_bytes_raw()
    )
    header = VersionedHeaderBuilderV1().build(
        context=context, body_reference=body_reference, content_key=TEST_CK,
        recipients=[recipient], signing_private_seed=TEST_HEADER_SEED,
    )
    public = Ed25519PrivateKey.from_private_bytes(TEST_HEADER_SEED).public_key().public_bytes_raw()
    verification = verification_context_for(header.core, public, "i8-test-header-key")
    return header, verification


def body_validator(data):
    value = parse_strict(data)
    required = {
        "bodyVersion", "chainId", "chunkCount", "chunkSize", "chunks",
        "formatVersion", "manifestDigest", "nonceBase", "plaintextLength", "resourceId",
    }
    if not isinstance(value, dict) or set(value) != required or value["formatVersion"] != 1:
        raise ValueError("INVALID_BODY_FORMAT")
    if value["chunkCount"] != len(value["chunks"]):
        raise ValueError("INVALID_BODY_CHUNK_COUNT")
    envelope = BodyEnvelopeV1(
        value["formatVersion"], value["chainId"], value["resourceId"],
        value["bodyVersion"], decode(value["nonceBase"]), value["chunkSize"],
        value["plaintextLength"], value["chunkCount"], decode(value["manifestDigest"]),
        tuple(
            EncryptedChunk(item["index"], item["plaintextLength"], decode(item["ciphertext"]))
            for item in value["chunks"]
        ),
    )
    decrypt_body(envelope, TEST_CK)


@pytest.fixture
def i8_fixture(tmp_path):
    store = LocalObjectStore(tmp_path / "store")
    body = body_bytes()
    body_ref = store.put(body, namespace="body", object_kind=ObjectKind.BODY)
    header, verification = build_header(body_ref)
    header_bytes = header.to_canonical_bytes()
    header_ref = store.put(header_bytes, namespace="header", object_kind=ObjectKind.HEADER)

    def header_validator(data):
        parsed = SignedVersionedHeaderV1.from_strict_json_bytes(data)
        VersionedHeaderValidatorV1().validate(parsed, verification)

    client = KuboRpcClient(os.environ.get("R3_I8_KUBO_API", "http://127.0.0.1:65001"))
    gateway = IpfsReplicaGatewayV1(
        store, client, {ObjectKind.HEADER: header_validator, ObjectKind.BODY: body_validator}
    )
    return {
        "store": store, "gateway": gateway, "client": client,
        "header_ref": header_ref, "body_ref": body_ref,
        "header_bytes": header_bytes, "body_bytes": body,
    }
