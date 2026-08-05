# AuthorizationState Interface-Gap Audit

Status: `HARD_STOP_RC2_KEY_VERSION_INTERFACE_GAP`.

The authoritative frozen interface manifest records the resource tuple as:

`owner:address, policyDigest:bytes32, epoch:uint64, status:Status,
policyVersion:uint64, stateVersion:uint64, updatedAtBlock:uint64`.

The frozen source and deployed-artifact ABI expose only
`getResource(bytes32)` for resource-state retrieval. They do not expose a
resource key version, a current Header key version, or a function from which
one can be derived without inventing new protocol semantics.

I5's approved `commitHeaderV1` requires validation of the submitted
`keyVersion`; therefore neither a read-only `IAuthorizationStateFrozen` nor a
HeaderRegistry can honestly enforce the required state relation. Enforcing only
`keyVersion != 0` would validate syntax rather than authorization state and is
rejected.

This is not repaired by modifying CAP2, `AuthorizationState`, its ABI, its
artifact, or the formal chain. The required next decision is whether the I5
invariant should be narrowed to a Header-local version rule, or whether a
separate new frozen authority for key-version state is required. Either choice
requires a renewed RC3 design review and explicit user approval.
