# Header 提交协议

I5 使用链下一次对象校验后、链上一次 `commitHeaderV1` 的 COMMITTED 锚点协议。链交易失败或回执未知时数据库不得进入 COMMITTED；成功回执、块信息和链上 Anchor 对账完成后才允许 CAS 提交。

最终 INITIAL 操作 ID：`415b8f90c6298925695b536909486a27e4bf71c328acd478cf51f820fe77ba68`。数据库证据来源为 `REAL_ISOLATED_CHAIN_ONLY`。
