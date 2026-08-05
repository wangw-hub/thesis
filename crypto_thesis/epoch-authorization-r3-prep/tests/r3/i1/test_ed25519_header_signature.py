import pytest
from epoch_auth_r3.crypto.ed25519_signer import sign_header, verify_header
from epoch_auth_r3.crypto.exceptions import IntegrityError

SEED = bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60")
PUBLIC = bytes.fromhex("d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a")
ARGS = dict(chain_id=1337, authorization_contract=bytes.fromhex("11"*20),
            header_registry=bytes.fromhex("22"*20), header_digest=bytes.fromhex("33"*32),
            issuer_key_id="test-issuer-key-v1")


def test_sign_and_verify_and_mutations_fail():
    sig = sign_header(SEED, **ARGS)
    verify_header(PUBLIC, sig, **ARGS)
    for field, value in [
        ("chain_id", 1), ("authorization_contract", bytes.fromhex("55"*20)),
        ("header_registry", bytes.fromhex("66"*20)), ("header_digest", bytes.fromhex("77"*32)),
        ("issuer_key_id", "other-key"),
    ]:
        changed = {**ARGS, field: value}
        with pytest.raises(IntegrityError): verify_header(PUBLIC, sig, **changed)
    for bad in (sig[:-1], sig+b"\x00"):
        with pytest.raises((IntegrityError, ValueError)): verify_header(PUBLIC, bad, **ARGS)
