# I7 Scope and Non-goals

I7 validates bounded recovery across AuthorizationState, HeaderRegistry,
PostgreSQL workflow state, immutable objects, and external test-only key
custody. It covers unknown transaction recovery, backup restoration, derived
state rebuilding, service interruption, and fail-closed material release.

It does not provide IPFS, production disaster recovery, historic state beyond
the retained Bonsai horizon, key escrow, retrospective revocation, performance
results, or automatic entry to I8.
