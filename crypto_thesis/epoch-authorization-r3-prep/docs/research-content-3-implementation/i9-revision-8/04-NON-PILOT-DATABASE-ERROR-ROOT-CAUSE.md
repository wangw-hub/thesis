# Database Error Root Cause

Revision 7 connected to and attested the correct Pilot PostgreSQL identity. `NON_PILOT_DATABASE` incorrectly masked a zero-row lookup caused by an uncommitted `JOB_CREATE`.

`PILOT_DATABASE_IDENTITY_MISMATCH` is now reserved for host, port, database, user, server-version, or application-name mismatch. Job absence, visibility, state conflict, rollback, transaction abort, and connection loss have independent classifications.
