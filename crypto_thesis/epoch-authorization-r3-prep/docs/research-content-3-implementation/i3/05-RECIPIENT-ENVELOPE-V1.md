# Recipient Envelope V1

Each `RecipientEnvelopeV1` has `envelopeVersion`, `recipientKeyId`, `userVersion`, fixed HPKE suite, `enc`, and `ciphertext`. One envelope directly seals the CK payload to one registered X25519 public key.

Recipient key IDs must be unique. The complete list is canonically ordered by `(recipientKeyId, userVersion)`. Empty lists, duplicates, noncanonical ordering, malformed encodings, deletion, addition, reordering and ciphertext tampering fail closed.

