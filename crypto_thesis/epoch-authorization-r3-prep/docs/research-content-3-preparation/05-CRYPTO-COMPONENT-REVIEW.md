# 密码组件审查

**Body AEAD。** AES-256-GCM与ChaCha20-Poly1305均要求同一密钥下 nonce 唯一并支持 AAD。默认推荐 AES-256-GCM，但以分块记录协议实现：每个 Body 使用随机 256-bit CK；由随机 body nonce prefix 与严格递增 chunk index派生唯一96-bit nonce；AAD绑定 resourceId、bodyVersion、chunkIndex、chunkCount和明文长度。ChaCha20-Poly1305作为 E6 对照。

**接收者封装。** RFC 9180 HPKE Base模式提供接收者公钥封装，但不单独认证发行者；因此 Header再由发行者数字签名认证。候选 suite 为 DHKEM(X25519, HKDF-SHA256)+HKDF-SHA256+AES-256-GCM；具体 Python 库、suite与测试向量通过 R3-B 后决定，禁止手拼“HPKE”。

**包装层。** 默认直接 HPKE 封装 CK 的小型 access envelope，避免无证据增加 KEK_e。仅当接收者规模实验表明共享 KEK 可显著降低 Header且不扩大撤销风险时，才启用 `HPKE(KEK_e)` + `AEAD-wrap(KEK_e, CK)`。

**摘要/签名。** SHA-256用于寻址与版本链；签名算法复用经审查的发行者密钥体系，不把哈希等同真实性。证据来源见 [依赖基线](01-DEPENDENCY-BASELINE.md)。
