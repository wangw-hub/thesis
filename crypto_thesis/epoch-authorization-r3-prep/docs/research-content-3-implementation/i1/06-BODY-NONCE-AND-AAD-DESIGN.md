# Body Nonce 与 AAD

状态：`NOT_EXECUTED_DUE_TO_HPKE_HARD_STOP`。

96-bit nonce 的 64-bit nonceBase + 32-bit chunkIndex 草案未被冻结为实现。
循环依赖、bodyVersion nonce 空间隔离和 manifest 摘要绑定仍需在修订后的
I1 中通过固定项目向量与负向用例关闭。

