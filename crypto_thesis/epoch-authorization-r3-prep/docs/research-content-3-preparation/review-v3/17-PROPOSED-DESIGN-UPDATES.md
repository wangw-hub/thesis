# 设计更新提案

本文件补充 review-v2，不改写历史：

1. OD-13 KeyStore 从宽泛 `USER_DECISION_REQUIRED` 收敛为 A/B/C 三项，推荐 A，状态 `READY_FOR_USER_DECISION`。
2. K-01 用户私钥严格置于客户端；多设备采用多 recipientKeyId。
3. K-03 CK 必须为 Header 重建受保护持久化，禁止明文数据库。
4. 新增 EncryptedCKRecordV1 和本地 ROOT_KEK；明确它不是 Header `KEK_e`。
5. CAP2 与 Header Ed25519 私钥采用两个独立 keyId 和托管边界。
6. HeaderRegistry 使用独立 HEADER_COMMITTER 交易账户。
7. KS-1 为可移植基线；KS-2 是条件性 Ubuntu 注入；KS-3 仅开发适配。
8. Vault、云 KMS、HSM 不进入当前论文实现。
9. 软件 KeyStore 不抗 root/内存读取是接受限制。
10. V2 的 HPKE/Envelope 未决项映射到 I1，未提前关闭。

不需要修改 CAP2 或 AuthorizationState。
