# 密码Suite决定

## BodyFormat V1

- suite：AES-256-GCM，128-bit tag；ChaCha20-Poly1305仅作E6对照。
- 每个Body版本生成独立随机256-bit CK，禁止复用。
- 默认chunkSize=4 MiB；允许1–16 MiB的2次幂，实施时冻结。
- `chunkCount = ceil(plaintextLength/chunkSize)`且`1 ≤ chunkCount ≤ 2^32-1`。
- 96-bit nonce=`nonceBase(64 random bits) || uint32_be(chunkIndex)`；同一CK下index从0严格递增且不得重复。
- 每块AAD为固定域`R3-BODY-CHUNK-V1\0`与chainId、authorizationContract、resourceId、bodyVersion、plaintextLength、chunkSize、chunkCount、chunkIndex、plaintextChunkLength的定长规范编码。
- Body前缀含magic、formatVersion、suiteId、bodyVersion、plaintextLength、chunkSize、chunkCount、nonceBase；每块含index、ciphertextLength、ciphertext+tag。解密拒绝重排、缺块、重复、截断、额外尾随字节或任意tag失败，不返回部分明文。

## HPKE AccessEnvelope V1

采用pyca/cryptography 49.0.0的RFC 9180单次Base API候选：DHKEM(X25519,HKDF-SHA256)、HKDF-SHA256、AES-128-GCM。选择AES-128-GCM是因为RFC Appendix A.1提供直接向量且封装对象仅为32-byte CK；Body仍为AES-256-GCM。

`info=JCS({domain,chainId,authorizationContract,headerRegistry,resourceId,policyDigest,epoch,stateVersion,recipientKeyId,userVersion,headerVersion,keyVersion})`的SHA-256域分离编码。Base模式不认证发送者，Header整体另以冻结的Ed25519发行者签名认证。pyca API只返回`enc||ct`，Schema按KEM固定长度拆分为encapsulation与wrappedKey。

依据：[RFC 9180](https://www.rfc-editor.org/rfc/rfc9180.html)、[cryptography 49 HPKE](https://cryptography.io/en/stable/hazmat/primitives/hpke/)、[NIST SP 800-38D](https://csrc.nist.gov/pubs/sp/800/38/d/final)。库后端与RFC向量仍属I1最小原型门。
