# I4 Entry Checklist

I4 remains user-gated. Before entry, verify:

- explicit I4 approval and scope;
- I3 artifact hashes and 48/48 tests;
- I1/I2 regressions remain green;
- FATAL=0 and MAJOR=0;
- frozen Header schemas and validation order are unchanged;
- planned database schema is isolated from RC2 tables;
- no chain, HeaderRegistry, revocation, recovery or IPFS work is inferred without approval;
- secret and logging boundaries remain enforced;
- rollback/fail-closed invariants have executable contract tests.

