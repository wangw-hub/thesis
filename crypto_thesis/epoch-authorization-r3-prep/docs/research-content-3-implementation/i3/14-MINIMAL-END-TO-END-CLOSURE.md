# Minimal End-to-End Closure

The isolated closure encrypts a small BodyFormatV1 value, stores it, creates recipient envelopes and a signed Header, stores the Header, reads and validates both objects, opens the selected CK envelope, and decrypts the Body.

Authorized recipients recover the original test plaintext. Nonrecipients, wrong contexts, Header/Body tampering and old-Header rollback are rejected. The closure uses temporary local directories and test-only keys; it performs no network, chain, database or IPFS action.

