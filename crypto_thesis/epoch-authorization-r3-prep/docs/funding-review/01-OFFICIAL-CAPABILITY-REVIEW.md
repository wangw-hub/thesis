# Official Capability Review

FUNDING_REVIEW_ONLY=true

Besu's QBFT documentation lists `blockreward` and `miningbeneficiary` as QBFT genesis properties and requires every node to use identical values. It separately limits transitions to changing `blockperiodseconds` or validator-management method. This distinction is decisive: documentation does not support introducing a block reward through a later QBFT transition.

Local Besu 26.5.0 CLI inspection confirmed the installed official generator and version. The primary official reference is the Besu QBFT configuration documentation: https://docs.besu-eth.org/private-networks/how-to/configure/consensus/qbft .
