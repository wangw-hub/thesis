# Revision 6 failed Canary freeze

Attempt `I9_REVISION_6_20260730T141500Z_8fc5f44` and run
`12d15c7302d632ff5b09c61ec295d470316f10a280e0cda19aeea3b0f6d9b521`
are frozen as `FAILED_CANARY_APPLICATION_NAME_ATTESTATION` and
`CANARY_FAILED_BEFORE_JOB_CREATE`. They are excluded from Pilot acceptance,
pairing, and statistics.

The remote attempt root is read-only. Its phase journal and the committed local
mirror both have SHA-256
`962f51f3b2cf6a64011090f5ec05677e28fa3e5bb86c0901b8f0dfa1a4d9f082`;
the remote/local mismatch count is zero.

