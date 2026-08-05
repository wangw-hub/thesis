# 候选互操作结果

PyHPKE：`enc/ct/exporter/plaintext` 全部精确匹配，错误 AAD/info/enc/ct/key 拒绝。PyCryptodome：以 RFC `skR/enc/ct/info/aad` 独立恢复明文，错误 AAD/info/enc/ct 拒绝；缺少 exporter 和公开确定性 sender 控制，因此仅为 `INTEROPERABILITY_SECONDARY_ONLY`。两实现接收结果一致，无交叉验证冲突。
