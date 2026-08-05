# Affected Resource Resolution

Direct events resolve their embedded resource ID. User-scope events fan out through a complete reverse index. An incomplete index raises `INCOMPLETE_RESOURCE_RECIPIENT_INDEX`; it never produces a partial fan-out. Audit-only events create no jobs.
