# Current Chain Audit

FUNDING_REVIEW_ONLY=true

Read-only audit confirmed Besu 26.5.0, QBFT chain ID 2026072801, four validators, one RPC node, `peerCount=4`, and matching Genesis SHA-256 on all five hosts. The latest observed height was `0x7353`; `eth_gasPrice` and `baseFeePerGas` were both `0x7`. All formal configurations set `min-gas-price=0`, proving that this setting alone does not remove the EIP-1559 base-fee requirement.

The frozen Genesis allocation is empty, `eth_accounts` is empty on the RPC node, and all four validator addresses previously audited have zero balance. No funded, governed source was found in this review. Formal infrastructure was read only and not modified.
