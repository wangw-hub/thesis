# Body 存储最小闭环

使用固定、明确标注为非秘密的测试 CK 与小型人工明文生成 BodyFormatV1 密文，将完整密文字节 JCS 编码后 put、exists、verify、get，再由原 Body envelope 解密核对明文。

空 Body、单 chunk、多 chunk 和非整块全部通过。对存储对象的截断、追加、替换和跨引用替换导致 verify 失败且 get Fail-Closed；未修改 I1 BodyFormatV1。
