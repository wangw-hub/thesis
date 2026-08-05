# Full Reconciliation

Full reconciliation is bounded by an explicit resource limit. It reads both
contracts at one block, PostgreSQL in one transaction, verifies all referenced
objects and CK availability, checks recipient-index derivation and cursor
continuity, and appends the resulting disposition. Material release remains
disabled unless every selected resource is consistent.
