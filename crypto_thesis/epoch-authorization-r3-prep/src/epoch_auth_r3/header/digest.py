import hashlib

from epoch_auth_r3.serialization.jcs_adapter import canonicalize

from .schema_v1 import HEADER_DIGEST_DOMAIN


def header_digest(unsigned_header: dict) -> bytes:
    """Frozen I1 generic digest helper."""
    return hashlib.sha256(canonicalize(unsigned_header)).digest()


def header_core_digest(header: object) -> bytes:
    if hasattr(header, "to_canonical_bytes"):
        canonical = header.to_canonical_bytes()
    else:
        canonical = canonicalize(header)
    return hashlib.sha256(HEADER_DIGEST_DOMAIN + canonical).digest()


def header_object_digest(signed_header_bytes: bytes) -> str:
    return hashlib.sha256(signed_header_bytes).hexdigest()
