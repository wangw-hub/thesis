import pytest
from epoch_auth_r3.crypto.ed25519_signer import CAP2_DOMAIN, verify_header
from epoch_auth_r3.crypto.exceptions import IntegrityError
from epoch_auth_r3.header.digest import header_core_digest
from conftest import signing_public


def test_cap2_domain_cannot_verify_header_signature(signed_header):
    core = signed_header.core
    with pytest.raises(IntegrityError):
        verify_header(
            signing_public(), signed_header.signature.signature, domain=CAP2_DOMAIN,
            chain_id=core.chain_id, authorization_contract=bytes.fromhex(core.authorization_contract[2:]),
            header_registry=bytes.fromhex(core.header_registry[2:]),
            header_digest=header_core_digest(core), issuer_key_id=signed_header.signature.issuer_key_id,
        )
