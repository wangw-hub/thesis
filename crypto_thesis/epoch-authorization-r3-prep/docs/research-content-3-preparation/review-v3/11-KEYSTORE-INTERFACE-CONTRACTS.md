# KeyStore 接口契约（不可执行草案）

```text
SecretStore.load_secret(secret_id) -> SecretHandle
SecretStore.secret_metadata(secret_id) -> NonSecretMetadata

KeyProtectionService.wrap_content_key(context, controlled_ck) -> EncryptedCKRecordV1
KeyProtectionService.with_unwrapped_content_key(context, record, callback) -> CallbackResult
KeyProtectionService.current_key_version() -> int
KeyProtectionService.plan_rotation() -> RotationPlan

ContentKeyRepository.put_encrypted_ck(record, expected_absent=True)
ContentKeyRepository.get_encrypted_ck(resource_id, body_version) -> EncryptedCKRecordV1
ContentKeyRepository.compare_and_set_version(record, expected_record_version)

UserPublicKeyRegistry.get_active_keys(user_id) -> list[PublicKeyRecord]
SigningKeyProvider.sign_header_digest(header_digest) -> SignatureRecord
TransactionSignerProvider.sign_allowed_transaction(unsigned_tx) -> SignedTransaction
```

约束：

- `SecretHandle` 不提供 `repr`、JSON、日志或任意导出；仅受控 provider 可解析；
- 只有 Body encryptor 和 `with_unwrapped_content_key` 回调允许短暂接触 CK bytes；
- Repository、注册表和元数据接口永不返回明文秘密；
- Header signer 只能签固定 32-byte 摘要和固定域；交易 signer 必须检查 chainId、to、method 和角色；
- wrap/unwrap、签名、轮换、备份恢复和拒绝均产生不含秘密的审计事件；
- 所有接口当前均为设计契约；本轮不创建可运行实现。
