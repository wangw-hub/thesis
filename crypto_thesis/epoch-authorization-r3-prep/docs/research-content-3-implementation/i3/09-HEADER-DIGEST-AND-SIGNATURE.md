# Header Digest and Signature

`headerCoreDigest = SHA-256("EPOCH_AUTH_R3_HEADER_CORE_V1\\0" || JCS(HeaderCoreV1))`.

The Ed25519 signature input uses the existing fixed encoder over domain `EPOCH_AUTH_R3_HEADER_V1`, chainId, authorizationContract, headerRegistry, headerCoreDigest and issuerKeyId. It is not a signature over a bare digest.

The Header object digest is separately `SHA-256(JCS(SignedVersionedHeaderV1))` and is used by LocalObjectStore content addressing. It must not be confused with `headerCoreDigest`.

