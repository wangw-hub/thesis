# F0 B1 Decision And Old Chain Preservation

The approved B1 decision creates a future `FORMAL_AUTHORIZATION_EXPERIMENT_CHAIN` with chain ID 2026072901. The existing chain remains `INFRASTRUCTURE_VALIDATION_CHAIN`.

Before cold preservation, the old chain reported chain ID `0x78c36ae1`, peer count `0x4`, four validators, and block height growth from `0x7587` to `0x758a`. The fixed sampled block `0x7000` returned a hash. All five hosts reported the frozen old Genesis SHA-256. PostgreSQL remained active.

All old Besu services were stopped and disabled only after sampling. Each host then confirmed `/var/lib/besu` and `/etc/besu/genesis.json` remained present. No old data, keys, Genesis file, or evidence file was deleted, moved, or modified.
