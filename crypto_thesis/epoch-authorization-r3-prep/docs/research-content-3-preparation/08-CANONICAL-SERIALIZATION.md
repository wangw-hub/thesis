# 规范序列化

采用 RFC 8785 JCS 的 UTF-8输出作为 Header V1规范形式，但限制为 I-JSON安全子集：键唯一；未知键拒绝；字符串不自动 Unicode normalization；二进制统一无填充 base64url；`uint64`以规范十进制字符串编码，避免 IEEE-754精度丢失；地址为固定20字节小写十六进制；摘要固定32字节小写十六进制；时间为 UTC RFC3339秒精度，仅审计使用。

```
unsigned = JCS(header without issuerSignature and headerDigest)
headerDigest = SHA-256(unsigned)
issuerSignature = Sign(domain || headerDigest)
```

域为固定 ASCII `R3-HEADER-V1\0`。数组顺序有语义：envelope按解码后的 recipientKeyId字节升序；任何输入先验证再规范化，禁止“宽松解析后替用户修复”。`previousHeaderDigest`为前版 `headerDigest`，首版为32字节零值。RFC 8785已核验负零勘误；V1不允许 JSON number，避免该类歧义。

与 [Schema](07-VERSIONED-HEADER-SCHEMA.md)和 [不变量](12-SYSTEM-INVARIANTS.md)共同冻结后方可实现。
