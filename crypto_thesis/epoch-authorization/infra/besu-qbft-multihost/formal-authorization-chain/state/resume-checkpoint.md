# Formal Chain Resume Checkpoint

Updated: 2026-07-29T04:10:00Z

Completed through F5 and the principal F6 controls: the isolated formal QBFT
chain is producing blocks, has four validators and four peers, preserves the
old chain in cold storage, uses bootstrap-only Genesis allocation, and rejects
a funded unauthorized sender through Besu local account permissioning.  ADMIN,
OWNER, AUTHORIZER, and REVOCATION received minimum functional test balances by
locally signed bootstrap transactions; public receipts are under `evidence/f6`.

Next action: confirm F6 receipt balances, then execute F7 using the
governance-selected `contracts/AuthorizationState.sol`. Compile reproducibly,
deploy with ADMIN's externally stored key by offline signing, grant only the
defined business roles, and collect real state-machine evidence. Do not start
old-chain services, modify either Genesis, or expose external key contents.
