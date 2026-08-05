# Pilot failure phase contract V1

`NOT_REACHED` means a normally required phase was not executed because an
earlier failure terminated the run. It is not counted as execution.

`NOT_APPLICABLE` means the phase has no semantic role in the selected scenario.
It cannot be used to conceal an interrupted required phase.

A failed run must contain the observed failure, classify every required phase
as completed or not reached, complete evidence sealing, complete
`RUN_FINISHED`, and pass raw SHA validation. The successful Canary contract
still requires genuine execution of every required phase.

