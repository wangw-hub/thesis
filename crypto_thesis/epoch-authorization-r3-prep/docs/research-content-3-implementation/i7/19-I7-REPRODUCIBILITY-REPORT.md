# I7 Reproducibility Report

Environment: Windows test driver, Python 3.13, PostgreSQL 16 `r3_i4`,
isolated Besu chainId `2026073005`, LocalObjectStore temporary directories,
and repository-external test credentials.

Commands use explicit `PYTHONPATH`, a controlled pytest base directory, the
existing SSH tunnels, and the external pgpass. No timing values are interpreted
as performance evidence.

The independent restore database and backup are retained on experiment-client
for I8-entry review.
