# Revision 7 Chain–Database–Object Reconciliation

Classification: `CHAIN_AHEAD_OF_DATABASE`, `HEADER_ANCHOR_COMMITTED`, `AUTHORIZATION_STATE_UPDATED`.

The Pilot database has zero job rows for the failed run and no idle transaction. The local Body and Header objects exist, but the old runner anchored synthetic digests rather than their actual object digests. The resource and both derived operation identifiers are `BURNED_PILOT_NAMESPACE` and `DO_NOT_REUSE`.

Counts: duplicate anchors 0; duplicate COMMITTED rows 0; wrong material releases 0; database invariant violations 1; chain/object binding invariant violations 1.
