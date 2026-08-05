# HPKE RFC 9180 验证

Suite：Base / DHKEM(X25519, HKDF-SHA256) / HKDF-SHA256 / AES-128-GCM。

使用 RFC 9180 A.1.1 的 `skR`、`enc`、首条 `ct`、`info` 和非空 `aad`
进行公开 API 探针。`cryptography 49.0.0` 的 `Suite` 只暴露
`encrypt(plaintext, public_key, info)` 与
`decrypt(enc_ct, private_key, info)`。它没有独立 AAD、确定性 `ikmE`
或 exporter API。

结果：`FAIL_INVALID_TAG`。原因不是允许忽略的测试适配问题，而是公开 API
无法表达权威向量。不得把 AAD 拼入 info 后声称通过 RFC 原始向量，也不得
调用私有 API 或自行拼装 X25519+HKDF+AEAD。

判定：`HARD_STOP_RFC_VECTOR_NOT_EXECUTABLE_WITH_SELECTED_PUBLIC_API`。

