# Research Content 2 Interface Freeze

Status: `FROZEN`

Authoritative source baseline: `26ef5bc8dc7b09e683aae8c7d7012f779f6847ed`

## Chain

- Besu 26.5.0, QBFT, chain/network ID `2026072901`.
- Genesis SHA-256:
  `7d431f01aab7d0c55c58c09346ee1f9a43475322a4aca304cfbb172b9b32add4`.
- Four validator nodes and one non-validator RPC node.
- Contract: `0x9ef44cf538d0df457ba77c556d8785e48bfc436d`.
- Contract artifact SHA-256:
  `b8cd8040e4a7683fb4454ea1cf3c3c4d97647611ad7cb3d616b72a35cf496ad5`.

## AuthorizationState

The deployed contract source is `contracts/AuthorizationState.sol`, source
SHA-256
`a6ad3e76eed272036eaa1f9c5c6086c3cf46f198b1adb66045915409c3056c5f`.
The canonical ABI SHA-256 is
`bf9780238971c3e505756dcb2d0fd53ef823fb73ef4b9a994e77313044dda0a0`.
The artifact bytecode and deployed-bytecode SHA-256 values use the frozen ASCII
hex convention: `d9c20c6638...` and `7c35d95acb...`; full values are in the
machine manifest.

Resource state is:
`owner, policyDigest, epoch, status, policyVersion, stateVersion,
updatedAtBlock`. User state is:
`account, userKeyId, status, userVersion, updatedAtBlock`.
Status values are `NONE`, `ACTIVE`, `SUSPENDED`, and `REVOKED`.

The role set is `ADMIN`, `OWNER`, `AUTHORIZER`, `REVOCATION`, and `AUDITOR`.
The bootstrap funder owns no business role. Revocation is terminal. Policy
updates advance policyVersion, epoch, and stateVersion; epoch advancement and
resource status changes advance epoch and stateVersion; user key/status changes
advance userVersion.

The authoritative interface is the deployed artifact ABI plus
`AuthorizationState.sol`. `contracts/interfaces/IAuthorizationState.sol` omits
`stateVersion` in its historical tuple and is frozen as
`SUPERSEDED_NON_AUTHORITATIVE_STUB`; it must not be used for RC3 integration.

## CAP2

CAP2 canonical bytes are big-endian and contain:

`magic, version, flags, issuer, resourceId, policyDigest, epoch, userKeyId,
operation, notBefore, expiresAt, nonce, issuedAt, chainId, contractAddress,
resourceStateVersion, userVersion`, followed, when present, by
`matchedNode.start, matchedNode.size, coverVersion`.

Text values have unsigned 16-bit byte lengths. Integer values are unsigned
64-bit. `policyDigest`, `userKeyId`, and `coverVersion` are 32 bytes;
`contractAddress` is 20 bytes; `nonce` is 16 bytes. Operations are
`READ=1`, `UPDATE=2`, and `MANAGE=3`. Ed25519 signs the complete canonical
payload; `userKeyId` is SHA-256 of the raw 32-byte Ed25519 public key.
`policyDigest` binds I*, not C(P). CAP1 is rejected by chain-mode context checks.

## Gateway

`BesuStateGateway.get_confirmed_state(resource_id, user_id)` returns one
`ConfirmedState(block_number, block_hash, resource_state, user_state)`.
Resource and user calls are pinned to the same selected block. Required-state
absence and RPC failure raise `GatewayUnavailable`; callers reject with
`SYSTEM_STATE_UNAVAILABLE`. No stale-state or in-memory fallback is allowed.

The selected block hash is the immutable hash of the selected confirmed block.
`confirmations=0` in the formal deployment. The V13 request boundary contains
three gateway reads: initial issuer read, issuer pre-sign reread, and verifier
read. This is an experimental request boundary, not a claim that every future
consumer must make exactly three reads.

## Issuer and verifier

The issuer requires active resource/user state, matching user key and I* digest,
a permitted time window, and an unchanged pre-sign reread. It then signs CAP2.
Any gateway error or detected state race returns
`SYSTEM_STATE_UNAVAILABLE`.

The verifier order is frozen:

1. canonical encoding;
2. Ed25519 signature;
3. confirmed state read;
4. resource existence/status;
5. user existence/status;
6. policyDigest;
7. epoch;
8. chainId and contractAddress;
9. resource stateVersion;
10. userVersion;
11. userKeyId;
12. operation;
13. notBefore;
14. expiresAt;
15. policy availability;
16. time-policy/C(P) binding;
17. atomic Nonce consumption;
18. accept and audit.

Nonce is consumed only after every prior check succeeds. Verifier instances use
independent processes and one PostgreSQL truth source.

## PostgreSQL

The shared Nonce primary key is:
`chain_id, contract_address, resource_id, epoch, nonce`. Consumption is one
transaction using `INSERT ... ON CONFLICT DO NOTHING RETURNING 1`; database
failure propagates and causes fail-closed rejection.

Transaction Nonce state is keyed by `chain_id, sender`. Reservation uses
`SELECT ... FOR UPDATE` and allocates `max(database_next_nonce,
rpc_pending_nonce)`. Reservation states are `RESERVED`, `BROADCAST`,
`CONFIRMED`, and `FAILED`; reconciliation never moves the durable counter
backwards.

Research Content 3 may add only an independent `r3_control` schema. It may not
silently alter these RC2 tables or transaction boundaries.
