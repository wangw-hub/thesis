# PilotJobCreateTransactionV1

The transaction explicitly begins, inserts the complete candidate context and frozen chain-write plan, checks the affected row count, commits, and rolls back on error. It never waits for a chain receipt and never relies on connection-close or context-manager commit behavior.

Initial durable state: `READY_FOR_CHAIN_SUBMISSION`.
