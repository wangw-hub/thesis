# Recovery Runbook V1 — IPFS addendum

Verify replica mapping, fetch once, verify full bytes and object format, quarantine corrupt local state, atomically restore, reverify, and only then reevaluate material-release gates. Never fall back to a public gateway.
