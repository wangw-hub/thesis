# I1 恢复结果

PyHPKE 0.6.4 通过公开 API 精确复现 RFC 9180 A.1.1 的 `enc`、序号 0/1/2 的密文、三组 exporter 和接收明文；错误 AAD、info、enc、ciphertext 与私钥均 Fail-Closed。PyCryptodome 3.23.0 使用公开 API 成功解密同一固定向量并拒绝错误上下文，形成独立接收端互操作证据，但因无公开确定性临时密钥和 exporter API，不作为主提供者。

随后恢复全部 I1：BodyFormatV1、nonce、分块完整性、EncryptedCKRecordV1、JCS、Header 摘要、Ed25519 签名域、日志脱敏与严格 Schema 共 49 项测试全部通过。没有性能采集或密码学安全证明主张。
