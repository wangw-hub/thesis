# A7 evidence preservation

Final A7 records `scenarioEvidence` in EvidenceAccumulator immediately after event normalization/task planning. TerminalizerV2 copies the snapshot, realEventCount, normalizedEventCount, affectedResourceCount and taskCount into failure-context and chain evidence. Zero, unknown and NOT_REACHED remain distinct.
