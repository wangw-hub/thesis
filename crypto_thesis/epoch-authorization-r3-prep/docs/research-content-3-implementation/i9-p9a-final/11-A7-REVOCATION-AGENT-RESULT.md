# A7 REVOCATION_AGENT

FAILED with an unexpected `SCENARIO_FIXTURE_DEFECT`. The real EpochAdvanced transaction and the two preceding transactions all had receipt status 1. The fourth `commitHeaderV1` reverted because the formal fixture called `_anchor` without the event-derived epoch/stateVersion=2/2, leaving defaults 1/1. The contract correctly rejected the stale anchor. Terminal evidence was sealed, raw SHA errors were 0, and A8 was not executed.

This defect is worth fixing, does not invalidate the thesis protocol, cannot justify deleting or downgrading A7, and is not an environment defect. A separate evidence limitation is that A7 scanner/task counters were not copied into terminal failure context before the reverted fourth transaction, although reaching that transaction proves the scanner and one-task planning path completed.
