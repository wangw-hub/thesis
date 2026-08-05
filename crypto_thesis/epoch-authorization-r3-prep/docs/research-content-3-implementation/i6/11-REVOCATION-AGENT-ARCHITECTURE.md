# RevocationAgent Architecture

The deterministic core resolves resources, reads event-block state, applies the frozen update policy, and emits planned updates. Side effects are isolated behind database, storage, chain, and key-protection adapters. Execution modes are bounded backfill and bounded poll only.
