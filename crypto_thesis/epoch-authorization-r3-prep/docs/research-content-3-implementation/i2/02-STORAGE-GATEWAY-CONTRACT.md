# StorageGateway 契约

窄接口固定为 `put(data, namespace, object_kind, expected_digest) -> ObjectReferenceV1`、`get(reference) -> bytes`、`exists(reference) -> bool` 和 `verify(reference) -> ObjectVerificationResult`。

`exists` 仅表示物理入口存在，不构成可信判定；`get` 在长度和摘要双重通过前不返回成功；`verify` 返回结构化失败码；I2 不包含 pin、HTTP、远程下载、复制、同步、权限、数据库索引或垃圾回收。
