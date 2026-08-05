import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from epoch_auth_r3.crypto.ed25519_signer import sign_header, verify_header
from epoch_auth_r3.crypto.exceptions import IntegrityError
from epoch_auth_r3.header.signature_domain import CAP2_DOMAIN


def test_cap2_domain_cannot_verify_header_signature():
    seed = b"S"*32
    args = dict(chain_id=1, authorization_contract=b"\x11"*20,
                header_registry=b"\x22"*20, header_digest=b"D"*32,
                issuer_key_id="test-key")
    sig = sign_header(seed, **args)
    with pytest.raises(IntegrityError):
        verify_header(
            Ed25519PrivateKey.from_private_bytes(seed).public_key().public_bytes_raw(),
            sig, domain=CAP2_DOMAIN, **args
        )
