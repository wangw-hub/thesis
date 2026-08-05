# Development MINOR disposition

- issueId: `P9A-DEV-MINOR-001`
- originalDescription: frozen dependency emits a `websockets.legacy` deprecation warning
- rootCause: the frozen Web3 dependency closure still imports the compatibility namespace deprecated by the installed websockets release
- affectedComponents: dependency warning path only; no P9-A protocol or evidence component
- affectsSecurity: no
- affectsDataIntegrity: no
- affectsReproducibility: no; the dependency lock and snapshot digest remain frozen
- affectsStageEvidence: no
- affectsChainDatabaseObjectConsistency: no
- affectsFormalP9AValidity: no
- disposition: `ACCEPTED_LIMITATION_WITH_WORDING`

The warning does not affect material-release decisions, Header/Body digests, database transactions, chain invariants, run identity, raw immutability, or validity classification. Dependency replacement is deliberately deferred to avoid changing the frozen runtime immediately before final P9-A.
