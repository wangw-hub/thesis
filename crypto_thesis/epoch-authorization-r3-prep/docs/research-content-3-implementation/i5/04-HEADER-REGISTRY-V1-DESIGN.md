# HeaderRegistry V1 设计

合约绑定不可变 AuthorizationState 地址，维护 Header/Body/CK 版本及对象摘要权威状态。`commitHeaderV1` 先读冻结授权状态，再验证更新类型、版本连续性、previousHeaderDigest、非零摘要和 operationId，最后原子写入不可变历史与当前指针。

`keyVersion`、`bodyVersion` 的权威来源均为 HeaderRegistry；V1 强制相等。合约不存储 Header JSON、Envelope、CK 或 Body。
