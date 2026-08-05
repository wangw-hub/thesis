# I9 MINOR disposition

- SSH operational dependence remains an accepted Pilot limitation.  Remote
  execution is bounded, non-interactive, host-pinned to `experiment-client`,
  and produces a sealed local mirror.  It is not presented as production
  orchestration.
- The isolated single-node Besu chain remains suitable only for functional and
  pipeline validation.  It cannot support BFT, multi-validator, or formal
  performance conclusions; a formal multi-node environment remains an I10
  admission decision.
