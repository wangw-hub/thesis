from epoch_auth_r3.crypto.redaction import FORBIDDEN_LOG_FIELDS, redact_event


def test_all_forbidden_secret_fields_are_redacted():
    event = {name: "TEST_ONLY_SECRET_SENTINEL" for name in FORBIDDEN_LOG_FIELDS}
    event.update({"keyId": "public-id", "rejectionCode": "DENIED"})
    result = redact_event(event)
    assert all(result[name] == "[REDACTED]" for name in FORBIDDEN_LOG_FIELDS)
    assert result["keyId"] == "public-id"
