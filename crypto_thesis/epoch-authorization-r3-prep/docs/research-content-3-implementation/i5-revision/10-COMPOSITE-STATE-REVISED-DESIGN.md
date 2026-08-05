# CompositeStateGateway 修订设计

网关在同一 `block_identifier` 读取：

- AuthorizationState：resourceStatus、policyDigest、epoch、stateVersion；
- HeaderRegistry：headerVersion、bodyVersion、keyVersion、updateKind、previousHeaderDigest、headerDigest、headerObjectDigest、bodyObjectDigest。

输出 `CompositeResourceStateV1`，逐字段携带来源。任何调用失败、块号/块哈希不一致、未知状态或 Header 与外部上下文不一致，整体返回 UNKNOWN/拒绝。Header 自身字段不作为预期值来源。
