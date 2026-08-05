# QBFT Reward Transition Lab

FUNDING_REVIEW_ONLY=true

An isolated probe on `experiment-client` used Besu 26.5.0, a distinct chain ID, empty alloc, generated temporary validator material, and no formal ports or data directories. The probe generated a valid initial QBFT genesis, then added future transitions containing `blockreward` and `miningbeneficiary`.

Besu exited with code 2 and `Unable to load genesis file`. The probe result records `accepted=false`. The two configuration files have different file SHA-256 values; this is configuration identity, not Genesis block-hash evidence. No formal chain file, process, port, account, or database was modified.

This is a negative configuration-acceptance result, not evidence that an existing formal ledger can be safely transitioned. It prevents recommending Option A.
