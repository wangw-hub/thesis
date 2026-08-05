# 内容密钥保护设计

## 为什么持久化

Body 不因普通撤销而重新加密；Header 重建必须再次取得原 CK，为剩余用户生成新 Envelope。因此服务需要受保护的 CK 恢复路径。依赖某个用户 Envelope 恢复 CK 会把用户私钥引入服务端，明确禁止。

## 保护方案

- 每 Body 版本随机生成独立 32-byte CK；
- CK 只在创建 Body、包装记录、重建 Envelope 或解密受控操作期间出现；
- 数据库只保存 EncryptedCKRecordV1；
- ROOT_KEK 每版本独立 32-byte，使用 AES-256-GCM 包装 CK；
- nonce 为每次包装随机 96-bit；同一 ROOT_KEK 下必须由 CSPRNG 生成且不得复用，重包装必须新 nonce；
- AAD 使用固定域和定长编码绑定 chainId、两个合约地址、resourceId、bodyVersion、keyVersion、protectionKeyVersion、metadataDigest；
- 解包后再次校验调用上下文与记录字段；任何 tag、Schema、版本或绑定失败统一拒绝，不返回部分 CK。

## 生命周期

新 Body 生成 CK → 加密 Body → 生成首个 Envelope → 包装 CK → 丢弃明文工作缓冲区。Header 重建时解包一次，在受控回调内生成全部目标 Envelope，随后释放缓冲区。禁止把 CK 返回给日志、通用 REST 响应、任务队列或异常文本。

CK 泄露只影响对应 Body 版本，但无法由 Header 撤回；应标记资源受影响、停止新材料释放、生成新 Body/CK，并审计已知暴露窗口。
