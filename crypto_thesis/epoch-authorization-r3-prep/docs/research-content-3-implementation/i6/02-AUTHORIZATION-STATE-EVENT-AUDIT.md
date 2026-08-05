# AuthorizationState Event Audit

The frozen ABI exposes nine events: seven authorization-state events and inherited `RoleGranted`/`RoleRevoked`. `PolicyUpdated`, `EpochAdvanced`, and `ResourceStatusChanged` are direct-resource triggers. `UserKeyRotated` and `UserStatusChanged` are user-scope triggers. Registration and role events are audit-only. Unsupported ABI events: zero.

Logs omit `stateVersion`; actionable events therefore require `getResource`/`getUser` at the event block. Early block 829 state was pruned by Bonsai, so it is retained as historic audit evidence and never used to generate a current task. The admitted bounded range 2076–2097 had retained event-block state.
