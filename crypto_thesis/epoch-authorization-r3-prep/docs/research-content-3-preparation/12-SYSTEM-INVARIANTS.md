# 系统不变量

| ID | 半形式化表述 | 执行点/验证 |
|---|---|---|
| I1 | Accepted(H) ⇒ digest(H)=chain.headerDigest | 客户端；替换/篡改测试 |
| I2 | H.chainId/contract/resource/policy/epoch/stateVersion均等于当前状态 | Gateway；跨域替换测试 |
| I3 | 新有效版 headerVersion、keyVersion单调增加 | 合约CAS+DB唯一约束；乱序测试 |
| I4 | `H.previousDigest = digest(previous active H)` | HeaderService；回滚/断链测试 |
| I5 | 每 `(CK, nonce)`至多使用一次 | CryptoService；重复nonce测试向量 |
| I6 | 同一 operationId+resource+targetEpoch 至多一个 ACTIVE版本 | DB+合约；并发重复事件 |
| I7 | 状态依赖不可用时不签发、不解密 | 各Gateway；RPC/DB/存储故障 |
| I8 | 撤销确认后不为被撤用户创建未来 envelope | HeaderService；E9 |
| I9 | Header更新不改 Body字节与digest | Storage审计；E7 |
| I10 | 事件游标只在范围完整处理后推进 | RevocationAgent；漏读/重启 |

这些是组合不变量，不是新密码学定理。标准原语假设与失败后果见 [安全论证](17-SECURITY-ARGUMENT-PLAN.md)。
