# Risk and Hard Stops

## Resolved

- `HS-FUNDING-001`: `RESOLVED_BY_NEW_FORMAL_CHAIN_DECISION`. The old empty-alloc chain remains cold preserved; it was not rewritten.
- Legacy Besu P2P key exposure: `RESOLVED_WITH_ARCHIVE`; the identity was retired and repository history sanitized.

## Accepted limitations

- `C(P)` has no demonstrated general storage or lookup advantage over the interval baseline.
- Python timing constants do not establish language-independent complexity.
- PILOT_ONLY observations are excluded from formal performance claims.
- Formal results confirm that C(P) remains an optional derived IR rather than a core performance contribution.
- Research Content 3 formal conclusions are limited to a single-node Formal chain;
  C-07 (QBFT consensus performance) is FORBIDDEN.

## Active controls

- Never commit keys or passwords.
- Never mix the two chains' evidence or PILOT_ONLY/formal data.
- Formal performance collection requires the admitted, frozen configuration and a separate authorized run.

## Resolved review stop

- `HS-R2-FORMAL-REVIEW-001`: `RESOLVED_BY_CORRECTED_V13_RERUN`（epoch-authorization 项目）。

> Updated 2026-08-05：无活动硬停止。
