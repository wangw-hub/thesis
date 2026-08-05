# 测试向量来源登记

| ID | 来源 | 状态 |
|---|---|---|
| TV-HPKE-01 | RFC 9180 Appendix A.1.1 | 执行首条解密探针；FAIL_INVALID_TAG |
| TV-GCM-01 | NIST SP 800-38D / GCMVS | 未执行 |
| TV-ED25519-01 | RFC 8032 §7.1 | 未执行 |
| TV-JCS-01 | RFC 8785 与 verified errata | 未执行 |
| TV-BODY-01 | PROJECT_FORMAT_VECTOR | 未创建 |
| TV-CKR-01 | PROJECT_FORMAT_VECTOR | 未创建 |

HPKE 探针所用值来自 RFC 正文，不标记为项目向量。项目向量与标准向量未混淆。

