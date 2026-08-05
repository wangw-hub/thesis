# Funding Amount Estimate

FUNDING_REVIEW_ONLY=true

The compiled AuthorizationState artifact contains 14,438 bytecode characters. No funded isolated B1 chain was started in this review because the review's purpose was to evaluate the existing-chain transition mechanism, which was rejected before a valid reward path existed. Therefore deployment and state-transition `gasUsed` values are **not yet measured** and no numeric recommended balance is asserted.

For approved Option B1, the first implementation step must measure deployment, role grant, resource registration, epoch advance, pause, revoke, and state-update gas on the new formal chain. `minimum_required_balance` is the sum of these observed gas amounts multiplied by the observed base fee plus explicitly chosen priority fee. `recommended_test_balance` must apply a recorded safety multiplier. No reward amount may be selected before those measurements.
