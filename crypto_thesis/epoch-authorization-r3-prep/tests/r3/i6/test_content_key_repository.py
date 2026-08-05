from epoch_auth_r3.revocation.key_repository import ContentKeyRepositoryV1, KeyProtectionServiceV1


def context():
    return {
        "chainId": 2026073005,
        "authorizationContract": "0x" + "12" * 20,
        "headerRegistry": "0x" + "28" * 20,
        "resourceId": "34" * 32,
        "bodyVersion": 7,
        "keyVersion": 7,
        "protectionKeyVersion": 1,
    }


def test_wrap_unwrap_and_persist_only_ciphertext(db):
    protection = KeyProtectionServiceV1(b"\x88" * 32)
    ck = b"\x77" * 32
    record = protection.wrap(ck, context(), created_at="2026-07-30T00:00:00Z", test_nonce=b"\x66" * 12)
    repo = ContentKeyRepositoryV1(db)
    assert repo.put(record)
    assert not repo.put(record)
    loaded = repo.get("34" * 32, 7)
    assert loaded.ciphertext != ck
    assert protection.unwrap(loaded) == ck


def test_plaintext_ck_column_does_not_exist(db):
    columns = {r[0] for r in db.execute(
        """select column_name from information_schema.columns
           where table_schema='r3_control' and table_name='content_key_record'"""
    )}
    assert "ck" not in columns and "plaintext_ck" not in columns and "root_kek" not in columns
