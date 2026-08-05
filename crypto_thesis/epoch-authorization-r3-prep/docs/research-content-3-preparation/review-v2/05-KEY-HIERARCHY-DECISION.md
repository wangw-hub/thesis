# 密钥层次决定

## K1–K4结论

| 方案 | Header/更新 | 撤销与恢复 | 结论 |
|---|---|---|---|
| K1 HPKE直接封装CK | 每接收者一封装，O(N) | 最少密钥状态，粒度清晰 | **采用** |
| K2 HPKE封装KEK_e再包装CK | 仍需每用户封装且多一层包装 | 多KEK生命周期/失败面 | 拒绝V1 |
| K3每用户独立封装CK | 与K1实质相同 | 同K1 | 合并为K1 |
| K4每资源Epoch共享访问密钥 | 可复用但扩大共享密钥暴露面 | 撤销仍需重封装，恢复更复杂 | 拒绝V1 |

冻结层次：

1. 用户X25519长期密钥对：私钥仅在KeyStore；公钥指纹为recipientKeyId。
2. 每Body版本独立CK：只加密Body，不随Header版本变化。
3. 每Header版本按当前合法用户生成AccessEnvelope：直接HPKE封装同一CK，绑定该用户userVersion。
4. 发行者Ed25519签名密钥、HeaderRegistry交易密钥、用户HPKE私钥三者分离。

撤销时不轮换CK、不重加密Body；仅生成不含撤销用户的新Header。已获得CK的用户仍能解密旧Body，这是接受的前瞻边界。Header随接收者线性增长是明确限制，并由E7测量；V1不以无证据的KEK层掩盖该成本。
