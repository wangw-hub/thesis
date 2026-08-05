# Besu 26.5.0 multihost deployment

This directory contains the staged deployment automation and raw evidence for
four QBFT validators and one non-validating RPC node. Stages 0 and 1 are
authorized initially. Genesis, node keys, services, processes, RPC deployment,
and fault actions require later explicit approval.

Private material belongs under `private/` and is ignored by Git.

Current status: Stage 0 and Stage 1 passed. Besu 26.5.0 is installed on all
five hosts, but no genesis, validator keys, services, or blockchain processes
have been created. Stage 2 requires explicit approval.
