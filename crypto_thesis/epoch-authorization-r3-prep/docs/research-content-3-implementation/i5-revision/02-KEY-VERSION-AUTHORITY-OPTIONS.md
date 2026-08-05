# keyVersion 权威方案比较

| 方案 | 结论 | 理由 |
|---|---|---|
| A 修改 AuthorizationState | REJECTED | 破坏 RC2 冻结 Artifact、ABI 与证据 |
| B 链下数据库权威 | REJECTED | 客户端无法仅凭链上状态构造外部验证上下文 |
| C 独立 KeyVersionRegistry | REJECTED_AS_UNNECESSARY_COMPLEXITY | HeaderRegistry 已承担 Header/Body/CK 生命周期 |
| D HeaderRegistry 维护 bodyVersion/keyVersion | RECOMMENDED | 权威唯一、职责闭合、无需第三合约 |
| E 删除 keyVersion | REJECTED_FOR_V1 | 虽与 bodyVersion 冗余，但显式表达 CK 生命周期并对接 EncryptedCKRecord |

V1 接受“显式冗余 + 合约、数据库和客户端三层强制相等”，不接受可分叉的两个自由版本。
