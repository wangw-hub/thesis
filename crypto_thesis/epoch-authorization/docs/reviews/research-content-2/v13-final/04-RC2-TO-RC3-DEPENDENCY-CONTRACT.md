# RC2 to RC3 Dependency Contract

Status: `READ_ONLY_BASELINE`

Research Content 3 may consume the machine-readable
`rc2-interface-manifest.json` only after a read-only reconciliation in the
independent `research-content-3-preparation` worktree.

## Required inheritance

- I* remains the semantic primary representation and policyDigest input.
- C(P) remains an optional derived execution IR.
- CAP2 canonical fields, signing bytes, chain/contract/version binding, and
  rejection order remain unchanged.
- AuthorizationState address, artifact, roles, state transitions, events, and
  read semantics remain frozen.
- PostgreSQL shared Nonce remains the replay-control truth source.
- Issuer and verifier remain fail closed for RPC and database dependency
  failures.
- Research Content 3 uses an independent `r3_control` database schema.

## Prohibited coupling

RC3 must not modify RC2 raw data, preregistration, deployed bytecode, contract
state schema, CAP2 wire format, Nonce unique key, or formal-chain configuration.
It must not restore custom ABE, secret on-chain trapdoors, retroactive plaintext
revocation claims, O(1) total revocation claims, unvalidated HPKE, or an
assumption that IPFS implies permanent availability.

## Entry conditions

1. Recalculate and match the RC2 interface-manifest SHA-256.
2. Reconcile every consumed field against source and deployed evidence.
3. Resolve the KeyStore user decision.
4. Record any proposed extension as a new decision without rewriting RC2.
5. Obtain explicit approval for RC3 I0.

Until then, Research Content 3 remains
`PREPARATION_COMPLETE_AWAITING_ENTRY_DECISION`.
