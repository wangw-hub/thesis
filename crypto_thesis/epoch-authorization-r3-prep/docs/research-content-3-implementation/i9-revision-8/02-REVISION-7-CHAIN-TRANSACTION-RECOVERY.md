# Revision 7 Chain Transaction Recovery

The bounded block audit (12538–12545) uniquely recovered two successful isolated-chain transactions:

1. `registerResource`, tx `9993b8ac3492288cebc9fec79deb898454d8f3e98abe769338d79bb0793563d9`, block 12539.
2. `commitHeaderV1`, tx `8af56a005ed23484227b079aeb9153f404446ed961e0312d8942536369be71ac`, block 12540.

Both receipts, block hashes, senders, nonces, targets, calldata digests, and effects are recorded in the independent reconciliation evidence. No unbounded scan was used.
