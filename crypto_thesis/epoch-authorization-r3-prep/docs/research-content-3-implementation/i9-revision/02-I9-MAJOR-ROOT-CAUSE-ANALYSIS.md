# I9 MAJOR root-cause analysis

## I9-MAJOR-01 — incomplete mandatory phase instrumentation

The original runner emitted one synthetic `RUNNING` record per run.  The
validator expected three coarse phases and therefore reported 186 missing
records (two per run).  The deeper defect was the absence of an executable,
scenario-specific phase contract and component-side start/end journaling.
The repair adds `PilotPhaseContractV1`, an append-only remote journal using a
monotonic clock, explicit `NOT_APPLICABLE`, strict identity checks, and a
validator that cannot manufacture missing events.

## I9-MAJOR-02 — fault labels lacked activation and independent observation

The original `fault-evidence.json` recorded only a scenario label and
`EXPECTED_OR_NONE`; it did not prove that a fault happened or that a separate
component observed its consequence.  The repair requires `FAULT_ACTIVATION`
and `FAULT_OBSERVATION` phases plus `activated`, `observed`, and
`observationSource` evidence.  A labelled but unobserved fault invalidates the
run.

## I9-MAJOR-03 — Windows staging was the effective storage root

The old runner executed on Windows and serialized a Windows LocalObjectStore
root even though remote directories existed.  Directory preparation was
mistaken for execution placement.  The repair rejects Windows/unresolved paths,
requires hostname `experiment-client`, binds every config to the attempt-scoped
Linux root, and permits Windows only to trigger the bounded remote command and
mirror sealed evidence.

## Stage-gate defect

The original orchestration equated process completion with admission and built
all 93 configurations before validating P9-A.  `PilotStageGateV1` now makes the
gate executable: a stage cannot start unless its predecessor is `PASSED`, and
any invalid run makes the current stage fail without creating downstream work.
