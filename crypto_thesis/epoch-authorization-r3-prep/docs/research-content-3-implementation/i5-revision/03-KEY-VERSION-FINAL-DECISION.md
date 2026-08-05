# keyVersion 最终决定

`keyVersion` 是加密特定 Body 版本的内容密钥 CK 的逻辑版本。它不是 `stateVersion`、`userVersion`、`protectionKeyVersion`、签名密钥版本或交易密钥版本。

冻结不变量：

1. `keyVersion == bodyVersion`。
2. Header 版本独立递增。
3. Header-only 更新不改变 Body、CK 或其对象摘要。
4. Body 变化必须生成新 CK，Body 与 key 版本同步加一。
5. AuthorizationState 不维护 keyVersion。
6. HeaderRegistry 不改变 policyDigest、epoch 或 stateVersion，只读取并核验。

保留 keyVersion 是经审查的显式冗余；任何不相等状态均 Fail-Closed。
