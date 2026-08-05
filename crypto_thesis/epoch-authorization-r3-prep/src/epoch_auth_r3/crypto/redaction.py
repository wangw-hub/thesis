FORBIDDEN_LOG_FIELDS = frozenset(
    {
        "userPrivateKey",
        "ck",
        "rootKek",
        "signingPrivateKey",
        "transactionPrivateKey",
        "hpkePlaintext",
        "databasePassword",
        "connectionString",
    }
)


def redact_event(event: dict) -> dict:
    """Return an audit-safe copy without secret-bearing fields."""
    return {
        key: ("[REDACTED]" if key in FORBIDDEN_LOG_FIELDS else value)
        for key, value in event.items()
    }
