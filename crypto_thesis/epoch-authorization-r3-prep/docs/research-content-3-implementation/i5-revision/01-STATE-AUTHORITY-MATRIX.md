# 状态权威矩阵

| 字段 | 唯一权威 | 消费方 | 规则 |
|---|---|---|---|
| resourceId/resourceStatus | AuthorizationState | HeaderRegistry、CompositeStateGateway | 冻结 RC2 接口 |
| policyDigest/epoch/stateVersion | AuthorizationState | HeaderRegistry、客户端 | HeaderRegistry 只读核验，不写入授权状态 |
| headerVersion/bodyVersion/keyVersion | HeaderRegistry | CompositeStateGateway、客户端 | `keyVersion == bodyVersion` |
| headerDigest/headerObjectDigest/bodyObjectDigest | HeaderRegistry | 客户端、数据库对账 | 当前锚点权威值 |
| previousHeaderDigest/updateKind | HeaderRegistry | 合约状态机、客户端 | 连续版本转换 |
| operationId 使用状态 | HeaderRegistry | 提交者、恢复逻辑 | 一次性、链上幂等 |
| RecipientEnvelope/Header 完整字节/Body 密文 | 链下不可变对象存储 | 客户端 | 不是链上权威状态 |

Header 自身携带的版本字段只接受与双合约同块高读取结果比对，不能自证。
