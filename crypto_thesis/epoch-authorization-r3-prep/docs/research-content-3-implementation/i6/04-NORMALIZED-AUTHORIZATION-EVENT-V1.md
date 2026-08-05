# NormalizedAuthorizationEventV1

Identity is `(chainId, authorizationContract, transactionHash, logIndex)`. The record also binds event signature/name/class, block number/hash, optional resource/user identifiers, strict payload, and SHA-256 canonical payload digest. Identical duplicates are idempotent; payload or block-hash conflicts are rejected.
