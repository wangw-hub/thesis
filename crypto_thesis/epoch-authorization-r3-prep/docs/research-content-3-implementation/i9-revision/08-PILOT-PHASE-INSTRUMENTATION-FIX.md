# Pilot phase instrumentation fix

The remote runner emits phase boundaries immediately around the actual
component call, using `time.monotonic_ns()`.  Each append is flushed and
`fsync`ed.  Wall-clock UTC is audit metadata only.  Post-processing validates
the journal but never inserts, infers, or repairs an event.

Fault evidence is valid only when a controlled activation and a separately
recorded observation both occur.  Expected fail-closed outcomes can therefore
be valid runs while incomplete evidence remains invalid.
