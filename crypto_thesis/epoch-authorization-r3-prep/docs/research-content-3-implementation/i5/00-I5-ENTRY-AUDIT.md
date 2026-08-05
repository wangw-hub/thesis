# I5 Entry Audit

Decision: `BLOCKED`.

I4 is verified as `I4_COMPLETED_AWAITING_I5_APPROVAL`, with 49/49 tests,
zero FATAL, zero MAJOR, zero database-invariant violations, and zero partial
transactions. The RC2 main-repository baseline remains at
`dac223468f550224257986a169304ed2c3dcf5af`.

The I5 entry audit then found an RC2 interface gap before any contract
compilation, deployment, or isolated-chain transaction. The frozen
`AuthorizationState.getResource(bytes32)` ABI exposes `owner`,
`policyDigest`, `epoch`, `status`, `policyVersion`, `stateVersion`, and
`updatedAtBlock`; it exposes no resource `keyVersion`. I5 requires the
registry to verify the submitted `keyVersion` against current authorization
state. Treating a Header-provided value as that missing state would weaken the
approved invariant and is not permitted.

No HeaderRegistry, AuthorizationState mirror, Header anchor, Header commit,
or r3_control real-chain commit was deployed or executed.
