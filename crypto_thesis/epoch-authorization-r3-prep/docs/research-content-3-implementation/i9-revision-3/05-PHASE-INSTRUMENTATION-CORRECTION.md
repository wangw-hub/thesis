# Phase instrumentation correction

`JOB_CREATE`, `DATABASE_COMMIT`, object-digest verification, and material-release-rule checks are emitted at their real component boundaries. The append-only journal flushes and fsyncs each event. `EVIDENCE_SEAL` follows business phases and precedes final artifact sealing; `RUN` completion follows the sealed run journal.
