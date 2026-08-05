# Revision 7 invariant report

Application-name invariants passed: ASCII-only, deterministic, role-scoped,
44/47 bytes, exact three-source runtime equality, no prefix matching, no
truncation tolerance, no 5432 fallback, and no complete attempt/run identity
embedded.

Failure-terminal invariants passed: failure observed, required later stages
marked `NOT_REACHED`, evidence seal present, run finished present, raw SHA
valid, and no post-seal raw mutation.

Pilot acceptance invariants did not pass. Database final state was not
COMMITTED. Receipt and digest details were not retained in failure evidence, so
chain/object invariant counts cannot be asserted as zero. No formal chain,
Validator, P9-A, or PostgreSQL 16/main access occurred.

