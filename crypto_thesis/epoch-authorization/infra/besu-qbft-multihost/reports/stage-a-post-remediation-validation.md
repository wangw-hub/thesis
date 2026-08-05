# Stage A Post-remediation Validation

The sanitized repository and the frozen five-node QBFT network were rechecked
after local history cleanup.

- Besu version: 26.5.0 on all five hosts
- Chain ID: 2026072801
- Validator count: 4
- RPC node in validator set: no
- RPC peer count: 4
- Active services: 5
- Genesis SHA-256: `7ad57e14684a1e7b224ab3b83078bb59eee0e63d438ad2243339a6f5e8a7155a`
- Block height increased during the observation window: yes
- Committable worktree, index, reachable-history, and object secrets: 0
- Unclassified candidates: 0
- Sanitized `prepare.ps1` validation: passed

Stage A admission passed. The protected current-chain material remains only in
ignored private storage and was not modified.
