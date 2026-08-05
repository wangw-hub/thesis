# Canary result

The one authorized Canary failed closed at `JOB_CREATE` before any chain transaction. PostgreSQL truncated the overlong per-attempt `application_name` to 63 bytes, so exact runtime attestation rejected it. No retry was made. The partial phase journal is sealed; SHA-256 is `962f51f3b2cf6a64011090f5ec05677e28fa3e5bb86c0901b8f0dfa1a4d9f082`.
