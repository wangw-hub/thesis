# Pilot environment isolation

Database `epoch_auth_r3_i9_pilot`, role of the same name, schema `r3_pilot`, and remote directories under `/var/lib/epoch-auth-r3/i9-pilot` were created only in PostgreSQL 16/r3_i4 and experiment-client. Existing databases and formal assets were not modified. However, the attempted runner used a Windows-local staging LocalObjectStore rather than the frozen remote root; this is an I9 MAJOR.
