# 签名与链交易密钥分离

## Ed25519

推荐两个独立密钥：

- CAP2 私钥继续由冻结 R2 Issuer 管理，R3 不读取、不迁移；
- Header 私钥使用独立 keyId 和公钥登记，只签 `"R3-HEADER-SIGNATURE-V1\0" || headerDigest`。

独立密钥比复用+域分离增加一份备份和轮换成本，但使权限、泄露影响、审计和论文职责更清晰。若 Header 私钥泄露，只撤销 Header signer，不自动使 CAP2 signer 失效；反之亦然。

## 链交易账户

- HeaderRegistry 新增最小权限 `HEADER_COMMITTER_ROLE`，不复用 ADMIN/OWNER；
- 每个角色账户独立私钥、许可和撤销流程；
- 本地离线签名，无 RPC 长期解锁；
- 交易 nonce 继续复用 R2 冻结的 reservation 管理器；
- 私钥文件仓库外，仅服务账户可读；签名 API 限制 chainId、目标合约和允许方法；
- 交易密钥不得与 ROOT_KEK、Ed25519 私钥或连接秘密共享包装根或文件。

账户泄露时先撤销链上角色/许可并换号，再对异常交易和 nonce 进行审计；ROOT_KEK 轮换不能修复交易账户泄露。
