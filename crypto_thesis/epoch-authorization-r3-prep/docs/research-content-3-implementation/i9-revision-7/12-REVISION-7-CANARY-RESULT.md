# Revision 7 Canary result

The single authorized Canary failed closed during `DATABASE_COMMIT` with
`NON_PILOT_DATABASE`. `JOB_CREATE` used a separate psycopg connection whose
transaction was closed without an explicit commit; the subsequent connection
therefore updated zero rows. This is a database transaction-boundary defect,
not an application-name defect.

The short application-name fix passed at runtime. The run reached two isolated
chain transactions and CompositeState read before the database failure. No
retry occurred.

`PilotRunTerminalizerV1` produced `RUN_FAILURE_OBSERVED`, two truthful
`NOT_REACHED` stages, completed `EVIDENCE_SEAL`, completed `RUN_FINISHED`, and
an internally valid raw artifact manifest with zero SHA errors.

The terminalizer did not preserve the already-observed transaction hashes,
receipt block, CompositeState block, or object digests in its generic failure
records, and it reported the outer unwound phase `RUN` rather than the deepest
phase `DATABASE_COMMIT`. These evidence defects are retained as review issues;
the failed run is not accepted.

