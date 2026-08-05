# Content Key Recovery Path

`content_key_record` stores only EncryptedCKRecordV1 nonce, ciphertext, metadata digest, version metadata, and strict JSON. CK plaintext and ROOT_KEK have no columns. The test-only ROOT_KEK is a 32-byte random external file outside Git; its value is never logged or copied into evidence.
