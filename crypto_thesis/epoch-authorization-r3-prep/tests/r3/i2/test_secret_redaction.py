from epoch_auth_r3.crypto.redaction import redact_event


def test_storage_audit_never_needs_plaintext_or_key_material():
    event = redact_event({"ck": "TEST_SENTINEL", "rootKek": "TEST_SENTINEL",
                          "digestHex": "aa"*32, "failureCode": "DIGEST_MISMATCH"})
    assert event["ck"] == event["rootKek"] == "[REDACTED]"
    assert event["failureCode"] == "DIGEST_MISMATCH"
