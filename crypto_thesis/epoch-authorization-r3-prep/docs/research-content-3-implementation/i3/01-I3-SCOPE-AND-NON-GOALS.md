# I3 Scope and Non-goals

I3 implements Versioned Header V1, direct per-recipient HPKE envelopes, strict JCS serialization, Header digest/signature verification, immutable local Header storage, version-chain checks, and a small Body/Header end-to-end closure.

It does not implement a database state machine, HeaderRegistry contract, chain reads, revocation agent, recovery worker, IPFS, production key custody, performance experiments, or a cryptographic proof. Fixed test material is test-only.

