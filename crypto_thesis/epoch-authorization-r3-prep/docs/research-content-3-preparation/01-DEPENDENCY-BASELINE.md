# 依赖与一手资料基线

| 项目 | 核验基线 | 用途/限制 |
|---|---|---|
| Besu | 仓库冻结 26.5.0，chainId 2026072901 | 只读复用；R3不得修改正式链 |
| PostgreSQL | 正式环境 16.14 | R3使用独立 schema；不触碰 R2 Nonce 表 |
| Python cryptography | 官方文档当前稳定版 49.0.0 | AESGCM/ChaCha20Poly1305可用；一次性 API 不适合超大文件，需分块协议 |
| Web3.py | 官方稳定文档 7.16.0 | `eth_getLogs/get_logs`范围补扫；版本以实施锁文件再冻结 |
| Kubo | 官方 RPC 文档由 0.42.0 生成 | 后置接入；RPC具管理权限，不公开暴露 |

规范依据：[RFC 9180 HPKE](https://www.rfc-editor.org/info/rfc9180/)、[RFC 9180 errata](https://www.rfc-editor.org/errata/rfc9180)、[NIST SP 800-38D](https://csrc.nist.gov/pubs/sp/800/38/d/final)、[RFC 8785 JCS](https://www.rfc-editor.org/rfc/rfc8785.html)、[cryptography AEAD](https://cryptography.io/en/stable/hazmat/primitives/aead/)、[PostgreSQL INSERT](https://www.postgresql.org/docs/current/sql-insert.html)、[IPFS persistence](https://docs.ipfs.tech/concepts/persistence/)。

版本会变化的库只在 R3-B 最小验证后冻结；不得依据本文件推断 API 已通过实现测试。
