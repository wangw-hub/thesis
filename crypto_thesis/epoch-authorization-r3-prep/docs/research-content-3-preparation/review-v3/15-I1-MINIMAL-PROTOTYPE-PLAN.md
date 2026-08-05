# I1 标准密码最小验证计划（尚未执行）

I1 只验证正确性、标准兼容性和负向拒绝；不采集或报告性能。

| 组 | 用例 | PASS证据 |
|---|---|---|
| HPKE标准 | RFC 9180向量、Base、X25519、HKDF-SHA256、AES-128-GCM | enc/ciphertext/export结果与向量一致 |
| HPKE负向 | 错私钥、info、AAD；篡改enc/ciphertext | 全部认证失败且无CK输出 |
| Header签名 | Ed25519、固定签名域、JCS摘要 | 正向黄金向量；错域/错摘要拒绝 |
| CK记录 | AES-256-GCM EncryptedCKRecordV1 | wrap/unwrap黄金向量；错AAD/版本/nonce/tag拒绝 |
| Body格式 | 分块AES-256-GCM黄金向量 | 完整文件逐字节确定性验证（固定测试随机量） |
| nonce | 同CK下chunk nonce唯一、跨Body新CK | 重复检测和上限测试通过 |
| 分块负向 | 重排、删除、截断、重复、尾随 | 全部fail-closed，不返回部分明文 |
| 替换负向 | 跨resource、chain、contract、bodyVersion替换 | AAD/摘要验证拒绝 |
| Envelope规模 | 小规模接收者排序、重复和Header字节上限 | 形成I3输入阈值，不作性能主张 |

执行要求：只用合成测试密钥和小型固定明文；测试材料明确标记 `TEST_ONLY_NON_SECRET`；不接触正式数据库、链、IPFS、五 VM 或真实用户材料。每组保存实现版本、测试向量来源、命令、退出码、JSON结果和SHA-256。任一标准向量不通过即停止，不手拼X25519+HKDF+AEAD冒充HPKE。

映射：V2 M-01、OD-01、OD-02、OD-06保持 `REQUIRES_MINIMAL_PROTOTYPE`，只有 I1 实际证据通过后才能关闭。
