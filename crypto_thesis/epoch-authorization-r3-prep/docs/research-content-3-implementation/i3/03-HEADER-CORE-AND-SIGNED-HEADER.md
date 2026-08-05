# Header Core and Signed Header

`HeaderCoreV1` is the signed security statement. `HeaderSignatureV1` carries Ed25519, issuer key ID, the fixed Header signature domain, the explicit core digest and signature. `SignedVersionedHeaderV1` contains exactly `core` and `signature`.

The trusted issuer public key and expected current state are deliberately external in `HeaderVerificationContextV1`; a Header cannot declare its own trust anchor.

