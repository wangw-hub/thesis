# I1测试向量登记

| ID | 对象 | 一手来源 | I1用途 | 状态 |
|---|---|---|---|---|
| TV-HPKE-01 | X25519/HKDF-SHA256/AES-128-GCM Base | RFC 9180 Appendix A.1.1及官方JSON向量 | enc、key schedule、ciphertext、export | FROZEN_SOURCE_NOT_RUN |
| TV-X25519-01 | X25519 | RFC 7748 §5.2/§6.1 | 边界和迭代向量 | FROZEN_SOURCE_NOT_RUN |
| TV-ED25519-01 | Ed25519 | RFC 8032 §7.1 | Header签名正负向 | FROZEN_SOURCE_NOT_RUN |
| TV-GCM-01 | AES-GCM | NIST SP 800-38D及CAVP GCMVS向量 | CK记录/Body AEAD | FROZEN_SOURCE_NOT_RUN |
| TV-JCS-01 | JCS | RFC 8785 §3与附录、verified errata | Unicode、数字、键序、负零拒绝 | FROZEN_SOURCE_NOT_RUN |
| TV-BODY-01 | BodyFormatV1 | 项目规范生成的小型固定TEST_ONLY输入 | 分块、nonce、重排/删除/截断/替换 | TO_CREATE_DURING_I1 |
| TV-CKR-01 | EncryptedCKRecordV1 | 项目规范生成的小型固定TEST_ONLY输入 | AAD、版本、tag、CAS记录 | TO_CREATE_DURING_I1 |

项目自定义黄金向量不得标为标准向量。其随机量必须固定、公开且标记`TEST_ONLY_NON_SECRET`，不能复用于正式密钥。

来源：[RFC 9180](https://www.rfc-editor.org/rfc/rfc9180.html)、[RFC 7748](https://www.rfc-editor.org/rfc/rfc7748.html)、[RFC 8032](https://www.rfc-editor.org/rfc/rfc8032.html)、[NIST GCMVS](https://csrc.nist.gov/Projects/Cryptographic-Algorithm-Validation-Program/CAVP-TESTING-BLOCK-CIPHER-MODES)、[RFC 8785](https://www.rfc-editor.org/rfc/rfc8785.html)。
