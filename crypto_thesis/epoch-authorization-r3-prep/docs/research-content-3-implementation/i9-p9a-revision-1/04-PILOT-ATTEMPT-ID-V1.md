# PilotAttemptIdV1

`PilotAttemptIdV1` is the sole generator/parser/validator/serializer for I9 runtime attempt identities.

Accepted canonical forms are:

- `I9_REVISION_<positive-decimal>_<YYYYMMDDTHHMMSSZ>_<7-lowercase-hex>`;
- `I9_P9A_<YYYYMMDDTHHMMSSZ>_<7-lowercase-hex>`.

The identifier is ASCII, 33 to 64 characters, uppercase in fixed/family tokens, lowercase hexadecimal in the Git suffix, UTC-second timestamped, deterministic in structure, and safe as a Windows/Linux path component. Spaces, slashes, backslashes, colons, shell metacharacters, non-ASCII and non-canonical representations are rejected. `create()` performs an immediate parse round-trip; `serialize(parse(id)) == id` is mandatory.

Invariants `P9A-ID-INV-1` through `P9A-ID-INV-8` are enforced. The runId domain remains `EPOCH_AUTH_R3_I9_PILOT_RUN_ATTEMPT_V1` and is unchanged by this repair.

