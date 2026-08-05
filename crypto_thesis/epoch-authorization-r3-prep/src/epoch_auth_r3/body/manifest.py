from __future__ import annotations

import hashlib

from epoch_auth_r3.serialization.jcs_adapter import canonicalize


def manifest_payload(
    *,
    chain_id: int,
    resource_id: str,
    body_version: int,
    plaintext_length: int,
    chunk_lengths: list[int],
) -> dict:
    return {
        "bodyVersion": body_version,
        "chainId": chain_id,
        "chunkCount": len(chunk_lengths),
        "chunkPlaintextLengths": chunk_lengths,
        "domain": "EPOCH_AUTH_R3_BODY_MANIFEST_V1",
        "plaintextLength": plaintext_length,
        "resourceId": resource_id,
    }


def manifest_digest(**kwargs) -> bytes:
    return hashlib.sha256(canonicalize(manifest_payload(**kwargs))).digest()

