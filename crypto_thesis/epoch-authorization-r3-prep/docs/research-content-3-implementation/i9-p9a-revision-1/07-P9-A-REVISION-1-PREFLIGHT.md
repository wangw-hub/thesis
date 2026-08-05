# P9-A Revision 1 Preflight

Local committed gate after attempt identity and stage terminalization repair:

- I9 tests: 71 passed;
- isolated-chain-only test: 1 skipped locally;
- compileall: passed;
- Revision 8 artifact SHA errors: 0;
- Revision 8 Canary: `CANARY_PASSED`;
- Revision 7: `BURNED_PILOT_NAMESPACE`, `DO_NOT_REUSE`;
- runtime attemptId validator implementations: 1;
- conflicting attemptId rules: 0;
- simulated top-level P9-A exception final state: `P9_A_FAILED`;
- possible terminal residue after guarded execution: 0;
- TRUE_SECRET: 0;
- UNCLASSIFIED: 0.

The local warning about the deprecated `websockets.legacy` package is non-gating and does not alter runtime behavior. Remote PostgreSQL, isolated-chain, Kubo, factory and real CompositeState preflight remain mandatory before attempt creation.
