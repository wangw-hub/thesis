# Header Canonical Serialization

All persistent Header bytes are RFC 8785 JCS bytes produced from strict canonical dictionaries. Binary fields use unpadded base64url; addresses and digests use normalized lowercase forms; security integers are bounded JSON-safe integers.

Serialization is deterministic for a given Header object. Building a new Header includes fresh HPKE ephemeral randomness and is intentionally not byte-deterministic.

