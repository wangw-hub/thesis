# R2依赖与接口审计

| 接口/事实 | 分类 | R3使用与边界 |
|---|---|---|
| I*与policyDigest | FROZEN_DEPENDENCY | Header和Registry均绑定32-byte policyDigest；不恢复C(P)主表示 |
| CAP2字段与Ed25519签名 | PROHIBITED_MODIFICATION | 保持version、issuer、resourceId、policyDigest、epoch、userKeyId、operation、时间、Nonce及ChainBinding |
| chainId/AuthorizationState地址 | FROZEN_DEPENDENCY | CAP2继续只绑定旧合约；Header另含headerRegistry地址 |
| resourceId/epoch/stateVersion | FROZEN_DEPENDENCY | Header提交与客户端接受的主授权快照 |
| userKeyId/userVersion | FROZEN_DEPENDENCY | 每个recipientEnvelope绑定；Header顶层不放单一userVersion |
| operation | FROZEN_DEPENDENCY | R3访问仍要求CAP2.READ；不新增操作码 |
| PostgreSQL Nonce消费 | PROHIBITED_MODIFICATION | R3独立schema，不复用或改写`consumed_nonces` |
| 正式角色 | FROZEN_DEPENDENCY | HeaderRegistry新增独立HEADER_COMMITTER_ROLE，不改变旧角色 |
| BesuStateGateway/Fail-Closed | FROZEN_DEPENDENCY | 复用只读confirmed-state语义；新增组合Gateway而非改核心拒绝语义 |
| chain_read与V13统计实现 | PENDING_V13_CONFIRMATION | 只影响最终接口对账/性能基线，不决定R3设计 |
| Header锚点 | REQUIRES_INTERFACE_EXTENSION | 新HeaderRegistry提供，不进入AuthorizationState/CAP2 |
| 审计日志 | REQUIRES_INTERFACE_EXTENSION | 增加operationId/headerDigest/版本/依赖结果；禁止秘密 |

结论：R3不需要也不得修改CAP2。现有epoch、stateVersion、policyDigest足以描述授权快照；Header真实性/当前性由独立Registry和客户端组合验证补充。V13只要不改变协议字段，本包无需重构。
