from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import pytest
from epoch_auth_r3.storage import LocalObjectStore
from epoch_auth_r3.storage.exceptions import CorruptObjectError
from epoch_auth_r3.workflows import MinimalHeaderFlowV1
from conftest import TEST_ONLY_CK, TEST_ONLY_HEADER_SEED, make_context, private_key, recipients, signing_public


def test_body_header_recipient_minimal_closure(tmp_path):
    flow = MinimalHeaderFlowV1(LocalObjectStore(tmp_path))
    result = flow.execute(
        plaintext=b"artificial i3 plaintext", content_key=TEST_ONLY_CK,
        nonce_base=b"I3NONCE!", context=make_context(), recipients=recipients(),
        signing_private_seed=TEST_ONLY_HEADER_SEED, signing_public_key=signing_public(),
        recipient_key_id="aa"*32, user_version=1, recipient_private_key=private_key(7),
    )
    assert result.recovered_plaintext == b"artificial i3 plaintext"
    assert result.body_reference.digest_hex != result.header_reference.digest_hex


def test_body_tamper_is_rejected_by_storage_before_decryption(tmp_path):
    store = LocalObjectStore(tmp_path)
    flow = MinimalHeaderFlowV1(store)
    result = flow.execute(
        plaintext=b"artificial body", content_key=TEST_ONLY_CK, nonce_base=b"I3NONCE!",
        context=make_context(), recipients=recipients(), signing_private_seed=TEST_ONLY_HEADER_SEED,
        signing_public_key=signing_public(), recipient_key_id="aa"*32, user_version=1,
        recipient_private_key=private_key(7),
    )
    body_path = [p for p in (store.root / "objects").rglob("*.obj") if p.name.startswith(result.body_reference.digest_hex)][0]
    body_path.write_bytes(body_path.read_bytes() + b"x")
    with pytest.raises(CorruptObjectError): store.get(result.body_reference)
