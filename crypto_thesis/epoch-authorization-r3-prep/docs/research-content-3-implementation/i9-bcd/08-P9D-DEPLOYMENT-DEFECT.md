# P9-D Deployment Defect — Frozen Attempt

`I9_P9D_20260802T050800Z_132cd9e` was frozen before any run was created.  The
remote launcher selected the system Python, which does not provide the approved
`web3` runtime dependency.  No raw evidence, chain transaction, database row,
or object was produced.  The approved benchmark virtual environment was then
identified at `/opt/epoch-auth-benchmark-venv/bin/python`; a new attempt is
required rather than mutating the failed launcher state.

