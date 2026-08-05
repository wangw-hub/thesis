# A6 result

`HEADER_UPDATE_PENDING`, seed 91006: invalid and evidence sealed. JOB_CREATE committed and was independently visible; three planned transactions produced three status-1 receipts. The fixed-block composite read then failed with `COMPOSITE_STATE_MISSING` at `COMPOSITE_STATE_READ`; database finalize was not reached and material was not released. This is an unexpected scenario/protocol mismatch, so P9-A stopped without retry and A7/A8 were not entered.
