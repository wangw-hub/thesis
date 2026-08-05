# ObjectReferenceV1

固定字段为 `schemaVersion=1`、`backend=local`、严格 namespace、`objectKind`、`digestAlgorithm=sha256`、64 位小写十六进制 `digestHex` 和非负整数 `sizeBytes`。对象类别为 BODY、HEADER、GENERIC_TEST；I2 只实际使用 BODY 与 GENERIC_TEST。

引用通过 JCS 输出规范字节；未知、缺失、重复 JSON 键由严格解析边界拒绝。引用不包含主机路径，`digest_identity` 为 `sha256:<digestHex>`。
