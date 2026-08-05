# COMMIT_UNKNOWN Recovery

Known transaction hash: query its receipt and verify the operation at the
receipt block. Success advances the database; revert is conflict; absence is
transient. No new transaction is sent.

Known sender and nonce: scan a finite block interval and accept only one exact
sender/nonce/target/calldata/operation match. Zero or multiple matches require
manual reconciliation.

No hash and no nonce is `UNKNOWN_TRANSACTION`. Re-broadcast is always false.
