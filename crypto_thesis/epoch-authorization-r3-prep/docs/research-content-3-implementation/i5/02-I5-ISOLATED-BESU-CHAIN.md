# Isolated Besu Environment Record

An isolated environment was provisioned only after I4 admission: chain name
`r3_i5`, chain ID `2026073005`, single-validator QBFT, Besu `26.5.0`, RPC
`127.0.0.1:18545`, P2P `127.0.0.1:31305`, data directory
`/var/lib/epoch-auth-r3/i5-besu/data`, configuration directory
`/etc/epoch-auth-r3/i5-besu`, and service
`epoch-auth-r3-i5-besu.service`. Its genesis SHA-256 is
`010711cdf0b30fa87ab605489068fd897f7140e9c7d921e5fe2faee24b5a369d`.

The service briefly started to validate independent QBFT block production and
loopback binding, then was stopped after the interface hard stop. Its isolated
configuration and data are preserved; no deletion or reuse of formal paths,
ports, accounts, or services occurred. This is environment evidence only, not
EVM deployment, performance, or BFT-tolerance evidence.
