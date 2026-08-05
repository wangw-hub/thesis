# PilotRunTerminalizerV1

The controlled failure path records the observed failure, structured error,
failure point, final outcome, truthful `NOT_REACHED` phases, evidence-seal
events, and `RUN_FINISHED`. It then writes every required raw record and creates
the SHA manifest as the final write within the immutable raw directory.

No file covered by the manifest is changed afterward. A failed business run
therefore remains invalid for acceptance while still being complete,
reproducible pipeline evidence.

