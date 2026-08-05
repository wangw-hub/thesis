# Event Cursor and Block Hash

The I4 cursor remains the ordering authority. Gaps, rollback, and block-hash conflict are fail-closed conditions. The I6 event table additionally binds every event to a block hash; conflicting duplicate identities are rejected before persistence.
