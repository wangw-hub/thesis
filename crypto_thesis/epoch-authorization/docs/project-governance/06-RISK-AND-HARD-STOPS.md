# Risk and Hard Stops

## Resolved

- `HS-FUNDING-001`: `RESOLVED_BY_NEW_FORMAL_CHAIN_DECISION`. The old empty-alloc chain remains cold preserved; it was not rewritten.
- Legacy Besu P2P key exposure: `RESOLVED_WITH_ARCHIVE`; the identity was retired and repository history sanitized.

## Accepted limitations

- `C(P)` has no demonstrated general storage or lookup advantage over the interval baseline.
- Python timing constants do not establish language-independent complexity.
- PILOT_ONLY observations are excluded from formal performance claims.
- Formal results confirm that C(P) remains an optional derived IR rather than a core performance contribution.
- V13's CPU field is cumulative process time, not utilization; no method-level
  CPU-efficiency claim is allowed.
- The frozen preregistration JSON has an appended archival note and is not
  strict JSON as a whole; its immutable bytes and index remain authoritative.
- `contracts/interfaces/IAuthorizationState.sol` is a superseded historical
  stub. RC3 must use the deployed ABI and interface manifest.
- Research Content 3 implementation is completed in the `epoch-authorization-r3-prep`
  worktree (I11 Formal 145/145 valid); this repository remains RC2-scoped.

## Active controls

- Never commit keys or passwords.
- Never mix the two chains' evidence or PILOT_ONLY/formal data.
- Formal performance collection requires the admitted, frozen configuration and a separate authorized run.

## Resolved review stop

- `HS-R2-FORMAL-REVIEW-001`: `RESOLVED_BY_CORRECTED_V13_RERUN`. The first
  formal benchmark remains immutable and invalidated. V13 completed the corrected
  request protocol and passed integrity and run-level paired analysis.

## Active hard stop

None for RC2. RC3 (r3-prep worktree) has no active hard stop either;
`HS-R2-FORMAL-REVIEW-001` was resolved by the corrected V13 rerun.
