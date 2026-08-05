# Recovery Authority Matrix V1

| State | Authority | Not authoritative |
|---|---|---|
| status, policyDigest, epoch, stateVersion | AuthorizationState | database/header |
| current Header/body/key versions and anchor digests | HeaderRegistry | header self-claims |
| signed Header and Body bytes | LocalObjectStore | current-version selection |
| events, jobs, attempts, audits, encrypted CK, recipient index cache | PostgreSQL | chain state |
| test ROOT_KEK and test signing/transaction keys | external KeyStore | Git/database |

Dual-contract reads use one explicit block number. PostgreSQL uses one
transaction snapshot. These are correlated evidence, not a globally atomic
cross-system snapshot.
