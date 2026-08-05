# PilotFailureContextV1

Failure evidence retains the first failed required phase, deepest successfully completed required phase, database transaction state, candidate and object digests, signed and broadcast transaction facts, receipt and fixed-block facts, material-release state, and the original exception class/message.

Later terminalization errors must not overwrite earlier evidence.
