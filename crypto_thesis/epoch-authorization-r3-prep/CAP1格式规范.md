# CAP1格式规范

正式规范见[docs/token-format.md](docs/token-format.md)。实现入口为
`epoch_auth.serialization.encode_capability`与`decode_capability`。

CAP1采用独立于NTP1的版本空间。NTP1决定`policyDigest`，CAP1绑定资源、
策略摘要、Epoch、用户公钥指纹、操作、有效期和Nonce；Proposed-C还绑定
实际命中的节点及Cover版本。全部字段进入Ed25519签名。
