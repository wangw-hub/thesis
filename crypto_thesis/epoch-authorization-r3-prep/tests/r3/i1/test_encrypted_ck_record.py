from dataclasses import replace
import json
import pytest
from epoch_auth_r3.crypto.exceptions import CryptoValidationError, IntegrityError
from epoch_auth_r3.keystore.encrypted_ck_record import EncryptedCKRecordV1, unwrap_content_key, wrap_content_key

ROOT, CK = b"R"*32, b"C"*32
CTX = {"protectionKeyVersion": 2, "chainId": 1337, "authorizationContract": "0x"+"11"*20,
       "headerRegistry": "0x"+"22"*20, "resourceId": "33"*32, "bodyVersion": 4, "keyVersion": 5}


def record():
    return wrap_content_key(ROOT, CK, CTX, created_at="2026-07-30T00:00:00Z", test_nonce=b"N"*12)


def test_wrap_parse_unwrap_and_determinism():
    r = record()
    assert EncryptedCKRecordV1.from_json(r.to_json()) == r
    assert unwrap_content_key(ROOT, r) == CK
    assert r.to_json() == record().to_json()


@pytest.mark.parametrize("changed", [
    {"resource_id": "44"*32}, {"body_version": 9}, {"key_version": 9},
    {"protection_key_version": 9}, {"nonce": b"X"*12},
    {"ciphertext": b"x"+record().ciphertext[1:]}, {"schema_version": 2},
])
def test_context_and_ciphertext_tampering_rejected(changed):
    r = replace(record(), **changed)
    with pytest.raises((CryptoValidationError, IntegrityError)):
        unwrap_content_key(ROOT, r)


def test_wrong_root_and_strict_json_rejected():
    with pytest.raises(IntegrityError): unwrap_content_key(b"X"*32, record())
    base = record().to_dict()
    cases = [
        {**base, "unknown": 1},
        {k:v for k,v in base.items() if k != "nonce"},
        {**base, "nonce": "%%%"},
    ]
    for case in cases:
        with pytest.raises(CryptoValidationError):
            EncryptedCKRecordV1.from_json(json.dumps(case))
    duplicate = record().to_json().decode().replace('"bodyVersion":4', '"bodyVersion":4,"bodyVersion":4')
    with pytest.raises(CryptoValidationError): EncryptedCKRecordV1.from_json(duplicate)
