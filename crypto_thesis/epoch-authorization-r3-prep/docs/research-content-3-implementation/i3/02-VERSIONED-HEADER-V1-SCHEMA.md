# Versioned Header V1 Schema

`HeaderCoreV1` contains schema/suite identifiers; chain, authorization-contract, HeaderRegistry and resource bindings; immutable Body reference/digest/version; policy, epoch and state versions; Header/key versions; the previous Header digest; recipient mode; and ordered recipient envelopes.

Frozen values:

- `schemaVersion=1`
- `suiteId=R3-BODY-A256GCM-HPKE-X25519-HKDFSHA256-A128GCM-SHA256-ED25519-JCS`
- `recipientMode=DIRECT_HPKE_PER_RECIPIENT`
- `hpkeSuite=HPKE-BASE-X25519-HKDF-SHA256-AES-128-GCM`

Addresses and 32-byte digests are normalized lowercase strings. Security-schema integers reject booleans, floats and implicit string conversion. Unknown, missing and duplicate JSON fields are rejected.

