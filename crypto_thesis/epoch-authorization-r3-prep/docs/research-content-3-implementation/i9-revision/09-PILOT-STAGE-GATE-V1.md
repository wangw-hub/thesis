# Pilot stage gate V1

The executable sequence is Canary, P9-A, P9-B, P9-C, P9-D.  Canary is an
admission probe and is excluded from the 93-run matrix.

P9-A must be 8/8 valid with zero missing phases, hash errors, database or chain
invariant violations, incorrect material releases, duplicate Anchors, or
duplicate COMMITTED states.  The same all-valid rule applies to each later
stage.  A failed stage records its failure and blocks all downstream runner
entry points.
