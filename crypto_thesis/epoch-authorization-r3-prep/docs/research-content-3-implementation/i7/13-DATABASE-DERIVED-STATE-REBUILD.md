# Database Derived-state Rebuild

When workflow history is lost, only the current externally verifiable anchor,
verified signed Header, and object mappings may be rebuilt. Rows are labelled
`DERIVED_RECOVERY_STATE`; `historyComplete=false` is mandatory. The process
does not invent event, attempt, or audit history.
