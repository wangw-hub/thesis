# EncryptedCKRecordV1

## 字段

| 字段 | 约束 | 摘要/AAD | 说明 |
|---|---|---|---|
| schemaVersion | `"1"` | 是 | 未知版本拒绝 |
| protectionSuite | `AES-256-GCM` | 是 | 与 BodyFormat 分离 |
| protectionKeyVersion | uint64 字符串 | 是 | 选择 ROOT_KEK |
| chainId | uint64 字符串 | 是 | 链绑定 |
| authorizationContract/headerRegistry | 20-byte 小写地址 | 是 | 合约绑定 |
| resourceId | bytes32 hex | 是 | 资源绑定 |
| bodyVersion/keyVersion | uint64 字符串 | 是 | Body/密钥版本 |
| nonce | 12-byte base64url | 否，作为 AEAD nonce | 每次包装随机 |
| ciphertext | 32-byte CK + 16-byte tag 的 base64url | 否 | 数据库秘密字段 |
| createdAt | RFC3339 UTC | 是 | 首次创建后不变 |
| metadataDigest | bytes32 hex | 是 | 业务元数据绑定 |

`aad = FIXED_BINARY("R3-CK-PROTECTION-V1\0", fields excluding nonce/ciphertext)`；字段采用定长大端整数、原始地址/摘要字节和长度前缀 UTF-8，禁止平台默认字符串拼接。

## 并发与恢复

- 主键 `(resource_id, body_version)`；唯一 `(resource_id, key_version)`；
- 更新携带 `record_version` CAS；
- 新记录先写临时候选并完成解包自检，再在同一数据库事务替换密文字段与 protectionKeyVersion；
- 中断时旧记录保持可读，新候选隔离；不得静默尝试任意历史密钥；
- tag 失败、密钥版本不存在或上下文不符进入安全告警和人工恢复，不覆盖原记录。

此记录只在受限数据库/对象存储中存在，不进入公开 Header。
