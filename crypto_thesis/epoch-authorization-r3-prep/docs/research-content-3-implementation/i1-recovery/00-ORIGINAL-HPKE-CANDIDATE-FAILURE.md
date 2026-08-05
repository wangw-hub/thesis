# 原 HPKE 候选失败保全

`cryptography 49.0.0` 在提交 `2004b0c1` 与 `87ae3b81` 中作为完整 HPKE 提供者未通过冻结的 RFC 9180 A.1.1 非空 AAD 向量，接收端返回 `InvalidTag`。原锁文件、原始输出、环境清单、测试向量和审稿结论均原样保留，原 I1 SHA 清单复核为零错误。

决定：`REJECTED_AS_COMPLETE_HPKE_PROVIDER_FOR_I1`；仅保留为 `LOW_LEVEL_CRYPTO_PROVIDER_ONLY`。本恢复工作不删除、不覆盖或改写失败历史。
