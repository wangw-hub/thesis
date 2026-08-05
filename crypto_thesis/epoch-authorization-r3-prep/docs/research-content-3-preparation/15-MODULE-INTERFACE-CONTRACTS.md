# 模块接口契约

| 模块 | 输入→输出 | Fail-closed/秘密 |
|---|---|---|
| CryptoService | chunks+AAD→encrypted body；envelope→CK | nonce/标签错误即失败；处理CK |
| HeaderService | state+recipients+body ref→signed candidate | 不接受旧状态；处理CK/KEK |
| StorageGateway | bytes/ref→verified ref/bytes | digest不符失败；不解释授权 |
| RevocationAgent | finalized logs→idempotent jobs | 缺块/乱序不推进游标 |
| AuthorizationGateway | resource/user→冻结合约状态 | RPC异常失败 |
| BlockchainGateway | range/tx→logs/receipt | 校验chain/contract/block hash |
| KeyStore | keyId+operation→signature/decapsulation | 私钥不导出 |
| RecoveryService | discrepancies→repair/dead letter | 不自动接受候选 |
| AuditService | structured event→append-only record | 秘密字段禁止记录 |

每次调用记录 correlationId、operationId、resourceId、版本、结果码和依赖状态。CAP2不变；R3验证是附加门，不静默新增CAP2字段。
