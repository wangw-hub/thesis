from epoch_auth_r3.crypto.redaction import redact_event


def test_header_errors_do_not_log_ck_or_private_keys():
    event = redact_event({"ck": "TEST_ONLY_KEY_MATERIAL", "userPrivateKey": "TEST_ONLY_KEY_MATERIAL",
                          "failureCode": "HPKE_OPEN_FAILED", "headerDigest": "aa"*32})
    assert event["ck"] == event["userPrivateKey"] == "[REDACTED]"
    assert event["failureCode"] == "HPKE_OPEN_FAILED"
