# HPKE Header Context

HPKE Base mode uses PyHPKE 0.6.4 with X25519/HKDF-SHA256/AES-128-GCM.

`info` is the frozen deterministic HPKEInfoV1 encoding of schemaVersion, chainId, both contract addresses, resourceId, bodyVersion, policyDigest, epoch, stateVersion, headerVersion, keyVersion, recipientKeyId and userVersion.

AAD is strict JCS over a separate domain, the same context, and bodyDigest. Cross-chain, contract, resource, epoch, Header-version, key-version or recipient substitution therefore cannot open an unchanged envelope.

