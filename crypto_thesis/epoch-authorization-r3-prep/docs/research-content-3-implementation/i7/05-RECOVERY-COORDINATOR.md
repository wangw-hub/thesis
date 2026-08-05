# Recovery Coordinator

Supported bounded modes are `RECONCILE_RESOURCE`, `RECONCILE_OPERATION`,
`RECONCILE_EVENT`, and `RECONCILE_ALL_BOUNDED`. A reconciliation run disables
material release before reading evidence and enables it only when every
selected resource is `CONSISTENT`. There is no infinite scanner or implicit
repair loop.
