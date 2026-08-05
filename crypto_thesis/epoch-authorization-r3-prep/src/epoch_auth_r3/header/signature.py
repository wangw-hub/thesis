from epoch_auth_r3.crypto.ed25519_signer import sign_header, verify_header
from epoch_auth_r3.crypto.exceptions import IntegrityError

from .digest import header_core_digest
from .exceptions import HeaderErrorCode, HeaderValidationError
from .models import HeaderCoreV1, HeaderSignatureV1
from .schema_v1 import HEADER_SIGNATURE_DOMAIN


def sign_core(core: HeaderCoreV1, private_seed: bytes, issuer_key_id: str) -> HeaderSignatureV1:
    digest = header_core_digest(core)
    signature = sign_header(
        private_seed, chain_id=core.chain_id,
        authorization_contract=bytes.fromhex(core.authorization_contract[2:]),
        header_registry=bytes.fromhex(core.header_registry[2:]),
        header_digest=digest, issuer_key_id=issuer_key_id,
    )
    return HeaderSignatureV1(
        "Ed25519", issuer_key_id, HEADER_SIGNATURE_DOMAIN, digest.hex(), signature,
    )


def verify_core_signature(core: HeaderCoreV1, signature: HeaderSignatureV1, public_key: bytes) -> None:
    digest = header_core_digest(core)
    if signature.header_digest != digest.hex():
        raise HeaderValidationError(HeaderErrorCode.HEADER_DIGEST_MISMATCH)
    try:
        verify_header(
            public_key, signature.signature, chain_id=core.chain_id,
            authorization_contract=bytes.fromhex(core.authorization_contract[2:]),
            header_registry=bytes.fromhex(core.header_registry[2:]),
            header_digest=digest, issuer_key_id=signature.issuer_key_id,
        )
    except (IntegrityError, ValueError) as exc:
        raise HeaderValidationError(HeaderErrorCode.HEADER_SIGNATURE_INVALID) from exc
