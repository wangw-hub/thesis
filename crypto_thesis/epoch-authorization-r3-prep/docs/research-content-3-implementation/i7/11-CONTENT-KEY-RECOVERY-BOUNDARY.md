# Content Key Recovery Boundary

A correct external test ROOT_KEK may unwrap an encrypted CK record. Temporary
unavailability is `FAIL_CLOSED_KEY_UNAVAILABLE`; permanent loss is
`IRRECOVERABLE_KEY_LOSS`. I7 does not escrow, reconstruct, log, or copy keys.
Already disclosed plaintext or CK cannot be recalled.
