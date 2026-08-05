# Recommendation

FUNDING_REVIEW_ONLY=true

Recommend **Option B1**, conditional on user approval: create a separate five-host `FORMAL_AUTHORIZATION_EXPERIMENT_CHAIN` using Besu 26.5.0 QBFT, a new chain ID, new validator keys and data directories, and a Genesis preallocation to a non-business `BOOTSTRAP_FUNDER`. Keep the current network unchanged as the infrastructure-validation chain.

Do not recommend Option A: the official transition scope and isolated Besu 26.5.0 rejection both contradict its required mechanism. Do not recommend Option D: `min-gas-price=0` already coexists with a nonzero base fee. Option E is prohibited for the current chain.

The hard stop remains active pending an explicit user decision. No formal role, contract, or performance experiment may begin.
