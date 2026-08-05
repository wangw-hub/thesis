# KeyStore方案A实施基线

状态：`OPTION_A_APPROVED`。

1. 用户X25519私钥只在客户端；服务只存公钥、recipientKeyId、userVersion、状态和登记证明。
2. 每Body版本独立随机256-bit CK。
3. CK只以AES-256-GCM `EncryptedCKRecordV1`持久化；绑定chainId、两个合约、resourceId、bodyVersion、keyVersion和protectionKeyVersion。
4. ROOT_KEK在仓库和数据库外，版本状态为ACTIVE/DECRYPT_ONLY/RETIRED/COMPROMISED。
5. Ubuntu优先systemd Credential；能力未核验时不能承诺使用`LoadCredentialEncrypted`，后备为严格权限文件。
6. CAP2签名密钥沿用RC2边界；Header使用独立Ed25519 keyId和签名域。
7. HEADER_COMMITTER及其他交易账户角色分离、本地签名、无RPC长期解锁。
8. ROOT_KEK不统一包装用户、签名或交易密钥。
9. Vault、HSM、云KMS不进入论文实现。
10. 不抗root、进程内存读取、完全主机失陷和用户主动共享，均为`ACCEPTED_LIMITATION`。

本基线保证数据库单独泄露不会直接给出CK；数据库与ROOT_KEK联合泄露会使相应CK静态保护失效。
