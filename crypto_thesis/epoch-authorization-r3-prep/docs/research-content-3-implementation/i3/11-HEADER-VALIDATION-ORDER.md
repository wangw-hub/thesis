# Header Validation Order

1. Strict parse and schema validation.
2. Compare all externally expected chain, contract, resource, state, version, previous-digest and Body-reference values.
3. Check Body reference/digest consistency.
4. Check trusted issuer key ID.
5. Recompute core digest and verify Ed25519 signature with the external trust key.
6. Locate exactly one recipient envelope.
7. Rebuild HPKE info and AAD from accepted context.
8. Open the envelope and strictly validate the CK payload.
9. Read the Body through verified immutable storage and decrypt it.

Any failure stops the flow; no partial plaintext or fallback Header is accepted.

