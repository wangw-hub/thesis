# Proposed Governance Updates after I3

For a future authorized merge:

- record I1 and I2 as completed frozen prerequisites;
- set RC3 to `I3_COMPLETED_AWAITING_I4_APPROVAL`;
- register VersionedHeaderV1, HeaderCoreV1, SignedVersionedHeaderV1, HeaderVerificationContextV1, RecipientEnvelopeV1 and CKEnvelopePayloadV1;
- register the direct per-recipient HPKE mode and Header/core-object digest distinction;
- register immutable local Header storage and the minimal Body/Header closure;
- retain accepted limits: no live chain assertion, database state machine, HeaderRegistry, revocation/recovery, IPFS or formal experiment;
- explicitly record that I4 has not started.

This file is a proposal only and does not modify the main repository governance package.
