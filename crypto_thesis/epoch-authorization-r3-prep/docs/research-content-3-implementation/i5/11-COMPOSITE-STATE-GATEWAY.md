# CompositeStateGateway

网关在同一块读取 AuthorizationState 的 resourceStatus、policyDigest、epoch、stateVersion，以及 HeaderRegistry 的 Header/Body/key 版本和摘要。字段来源显式分离；任一 RPC 异常或跨合约状态不一致返回 UNKNOWN。

最新授权 epoch 推进后，旧锚点上下文返回 `CROSS_CONTRACT_STATE_MISMATCH`。
