# Funding Options Matrix

FUNDING_REVIEW_ONLY=true

| Option | Outcome | Rationale | Recommendation |
| --- | --- | --- | --- |
| A: future QBFT reward transition on existing chain | Rejected | Official transition scope excludes reward changes; isolated Besu probe rejected the modified genesis. | NOT_RECOMMENDED |
| B1: new formal chain with preallocated bootstrap funder and nonzero base fee | Viable design candidate | Auditable funding source, realistic fee accounting, clean separation from infrastructure-validation chain. | RECOMMENDED |
| B2: new free-gas chain | Viable only if the research explicitly studies fee-free permissioned operation. | Removes fee realism and should not be mixed with B1 without reason. | CONDITIONALLY_RECOMMENDED |
| C: existing legitimate funded/governed account | Not found | No unlocked RPC account and audited validator balances are zero. | NOT_VIABLE |
| D: only lower min-gas-price | Not viable | It is already zero while base fee remains nonzero. | NOT_VIABLE |
| E: edit existing Genesis alloc/zeroBaseFee | Prohibited for current chain | Requires rebuilding or changing frozen chain identity/evidence. | PROHIBITED |

Option B requires a new chain ID, new data directories, and new validator keys. The present chain remains `INFRASTRUCTURE_VALIDATION_CHAIN`; the new one would be `FORMAL_AUTHORIZATION_EXPERIMENT_CHAIN`.
