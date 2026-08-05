# A7 target-state propagation

`targetEpoch` is authorized by normalized `EpochAdvanced.newEpoch` and cross-checked against AuthorizationState at the event block. `targetStateVersion` is read from AuthorizationState at the same fixed block because the frozen EpochAdvanced ABI does not carry stateVersion. The intent persists both values and the worker builder consumes only the persisted values. Mismatch is fail-closed.
