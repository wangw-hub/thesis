# OperationIdV1 影响审查

决定：`OperationIdV1` 不修改。

现有输入已包含 chainId、两个合约地址、事件签名、txHash、logIndex、resourceId、newEpoch、newStateVersion 和 newKeyVersion。V1 中 `newKeyVersion == newBodyVersion`，因此再加入 bodyVersion 不增加区分能力。`updateKind` 是针对当前 HeaderRegistry 状态推导并验证的转换语义，不是链上事件处理实例的身份字段；txHash/logIndex 已提供唯一事件定位。

扩大 OperationId 会破坏 I4 冻结幂等身份且无安全收益。Header 内容由 headerDigest 和对象摘要绑定。
