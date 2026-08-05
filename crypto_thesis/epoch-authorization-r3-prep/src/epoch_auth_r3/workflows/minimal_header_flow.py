from __future__ import annotations

from dataclasses import dataclass

from epoch_auth_r3.body.chunk_crypto import NonceUseRegistry
from epoch_auth_r3.body.format_v1 import BodyEnvelopeV1, EncryptedChunk, decrypt_body, encrypt_body
from epoch_auth_r3.header.builder import VersionedHeaderBuilderV1
from epoch_auth_r3.header.context import (
    HeaderBuildContextV1,
    RecipientPublicKeyV1,
    verification_context_for,
)
from epoch_auth_r3.header.models import SignedVersionedHeaderV1
from epoch_auth_r3.header.recipient import RecipientHeaderOpenerV1
from epoch_auth_r3.header.validator import VersionedHeaderValidatorV1
from epoch_auth_r3.serialization.base64url import decode, encode
from epoch_auth_r3.serialization.jcs_adapter import canonicalize, parse_strict
from epoch_auth_r3.storage import LocalObjectStore, ObjectKind, ObjectReferenceV1

BODY_FIELDS = {
    "formatVersion", "chainId", "resourceId", "bodyVersion", "nonceBase",
    "chunkSize", "plaintextLength", "chunkCount", "manifestDigest", "chunks",
}
CHUNK_FIELDS = {"index", "plaintextLength", "ciphertext"}


def serialize_body_envelope(envelope: BodyEnvelopeV1) -> bytes:
    return canonicalize({
        "bodyVersion": envelope.body_version, "chainId": envelope.chain_id,
        "chunkCount": envelope.chunk_count, "chunkSize": envelope.chunk_size,
        "chunks": [
            {"ciphertext": encode(x.ciphertext), "index": x.index, "plaintextLength": x.plaintext_length}
            for x in envelope.chunks
        ],
        "formatVersion": envelope.format_version, "manifestDigest": encode(envelope.manifest_digest),
        "nonceBase": encode(envelope.nonce_base), "plaintextLength": envelope.plaintext_length,
        "resourceId": envelope.resource_id,
    })


def parse_body_envelope(value: bytes) -> BodyEnvelopeV1:
    data = parse_strict(value)
    if not isinstance(data, dict) or set(data) != BODY_FIELDS:
        raise ValueError("invalid BodyEnvelopeV1")
    chunks = []
    for item in data["chunks"]:
        if not isinstance(item, dict) or set(item) != CHUNK_FIELDS:
            raise ValueError("invalid encrypted chunk")
        chunks.append(EncryptedChunk(item["index"], item["plaintextLength"], decode(item["ciphertext"])))
    return BodyEnvelopeV1(
        data["formatVersion"], data["chainId"], data["resourceId"], data["bodyVersion"],
        decode(data["nonceBase"]), data["chunkSize"], data["plaintextLength"],
        data["chunkCount"], decode(data["manifestDigest"]), tuple(chunks),
    )


@dataclass(frozen=True)
class MinimalFlowArtifactsV1:
    body_reference: ObjectReferenceV1
    header_reference: ObjectReferenceV1
    signed_header: SignedVersionedHeaderV1
    recovered_plaintext: bytes


class MinimalHeaderFlowV1:
    def __init__(self, store: LocalObjectStore):
        self.store = store
        self.builder = VersionedHeaderBuilderV1()
        self.validator = VersionedHeaderValidatorV1()
        self.opener = RecipientHeaderOpenerV1()

    def execute(
        self, *, plaintext: bytes, content_key: bytes, nonce_base: bytes,
        context: HeaderBuildContextV1, recipients: list[RecipientPublicKeyV1],
        signing_private_seed: bytes, signing_public_key: bytes,
        recipient_key_id: str, user_version: int, recipient_private_key: bytes,
        chunk_size: int = 8,
    ) -> MinimalFlowArtifactsV1:
        body = encrypt_body(
            plaintext=plaintext, ck=content_key, nonce_base=nonce_base,
            chain_id=context.chain_id, resource_id=context.resource_id,
            body_version=context.body_version, chunk_size=chunk_size,
            nonce_registry=NonceUseRegistry(),
        )
        body_bytes = serialize_body_envelope(body)
        body_ref = self.store.put(body_bytes, namespace="body", object_kind=ObjectKind.BODY)
        header = self.builder.build(
            context=context, body_reference=body_ref, content_key=content_key,
            recipients=recipients, signing_private_seed=signing_private_seed,
        )
        header_bytes = header.to_canonical_bytes()
        header_ref = self.store.put(header_bytes, namespace="header", object_kind=ObjectKind.HEADER)
        parsed = SignedVersionedHeaderV1.from_strict_json_bytes(self.store.get(header_ref))
        verification = verification_context_for(parsed.core, signing_public_key, context.issuer_key_id)
        self.validator.validate(parsed, verification)
        recovered_key = self.opener.open_content_key(
            header=parsed, recipient_key_id=recipient_key_id, user_version=user_version,
            recipient_private_key=recipient_private_key, verification_context=verification,
        )
        recovered_body = parse_body_envelope(self.store.get(parsed.core.body_reference))
        recovered_plaintext = decrypt_body(recovered_body, recovered_key)
        return MinimalFlowArtifactsV1(body_ref, header_ref, parsed, recovered_plaintext)
