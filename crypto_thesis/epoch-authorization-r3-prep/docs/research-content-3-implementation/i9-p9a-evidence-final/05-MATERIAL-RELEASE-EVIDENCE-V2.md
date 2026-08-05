# MaterialReleaseEvidenceV2

Fields: decision, reasonCode, evaluationBlockNumber/hash, headerDigest, authorizationStateVersion, headerVersion, evaluated, sourceComponent, and observedAt. Decisions are `NOT_EVALUATED`, `DENIED`, `ALLOWED`, `ALLOWED_AFTER_CURRENT_HEADER_ONLY`, and `UNKNOWN`.

`AccessMaterialReleaseGuard` is the authoritative successful-evaluation source. Scenario, outer, final-envelope, and strict projections serialize the same object. Failure before evaluation uses `NOT_EVALUATED` from the terminalizer.
