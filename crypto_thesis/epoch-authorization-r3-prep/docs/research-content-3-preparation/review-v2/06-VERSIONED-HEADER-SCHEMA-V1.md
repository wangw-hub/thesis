# Versioned Header Schema V1

Header是每资源、每版本一个JCS对象；全部字段进入`headerDigest`，唯独`issuerSignature`在摘要计算时临时移除。`createdAt`只设置一次并持久化候选，重试必须复用候选而非重建。

| 类 | 字段 | 必要/空值 | HPKE info | Body AAD | 链/客户端验证 | 变化规则 |
|---|---|---|---|---|---|---|
| A/F | schemaVersion,suiteId | 必须/否 | 是 | suite部分 | 客户端 | Schema升级才变 |
| B | chainId,authorizationContract,headerRegistry | 必须/否 | 是 | 前两项 | 双合约/客户端 | 不变 |
| C | resourceId,bodyReference,bodyDigest,bodyVersion | 必须/否 | 是 | 除reference | Registry/客户端；Body摘要 | Body版本才变 |
| D | policyDigest,epoch,stateVersion,headerVersion,keyVersion,previousHeaderDigest | 必须/否；首版previous为零 | 是 | policy/epoch/bodyVersion | Registry/客户端 | 授权/Header更新 |
| E | recipientEnvelopes[].recipientKeyId,userVersion,encapsulation,wrappedKey | 至少1项 | 每项是 | 否 | AuthorizationState用户状态+客户端 | 接收者/用户版本变 |
| G | createdAt,issuerId,metadataDigest | 必须；metadataDigest可零值表示无元数据 | issuerId | 否 | 客户端签名/格式 | 每候选固定 |
| 签名 | issuerSignature | 必须 | 否 | 否 | 客户端Ed25519 | 摘要后生成 |
| H | 数据库headerReference/索引状态 | 不进入Header | 否 | 否 | 链下 | 可迁移 |

`bodyReference`参与摘要，避免存储位置静默替换；CID与bodyDigest不等价：前者是存储寻址，后者是协议独立Body字节摘要。接收者列表按解码后recipientKeyId字节升序且不得重复。顶层不存在单一`userVersion`、`recipientMode`或显式HPKE nonce；userVersion属于每个envelope，HPKE nonce由RFC 9180上下文管理。

规范化：RFC 8785 JCS；所有uint64用十进制字符串；二进制用无填充base64url；地址固定`0x`+40个小写hex；摘要固定`0x`+64个小写hex；禁止未知字段、重复JSON键、浮点数、负零和Unicode自动正规化。

```
headerDigest = SHA-256(UTF8(JCS(header without issuerSignature)))
signatureInput = "R3-HEADER-SIGNATURE-V1\0" || headerDigest
```

Schema升级使用新`schemaVersion`与新域常量；V1解析器对未知版本fail-closed。
