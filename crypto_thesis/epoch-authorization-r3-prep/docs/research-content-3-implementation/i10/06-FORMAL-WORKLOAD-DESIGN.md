# Formal Workload Design

The workload generator is deterministic, seeded, versioned, and digest-bound. It derives fixture bytes from domain, seed, and requested size, records only digest/size, and never uses the experiment seed as cryptographic randomness. Formal input manifests contain generator version, seed, semantic class, configuration digest, and expected output schema. Plaintext, CK, private keys, and runtime credentials are never retained in evidence.
