# RFC 9180 A.1.1 字段映射

一手来源为 IETF RFC 9180 Appendix A.1.1。映射保持 `info` 与每条记录的非空 `aad` 独立：Base mode=0，KEM=0x0020，KDF=0x0001，AEAD=0x0001；`skE/pkE` 用于测试专用确定性发送上下文；`skR/pkR` 用于接收上下文；`enc` 必须等于 `pkE`；按序号 0、1、2 比较 `pt/aad/ct`；分别比较空上下文、`00` 和 `TestContext` 的 32 字节 exporter 输出。

判定禁止仅凭 round-trip；必须同时精确匹配 `enc`、三条 `ct`、三个 exporter 和接收端明文。
