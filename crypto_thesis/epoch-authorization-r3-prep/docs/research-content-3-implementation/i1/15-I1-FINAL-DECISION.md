# I1 最终决定

决定：`I1_REQUIRES_REVISION`。

I1 获准并进入执行，但所选 HPKE 库公开 API 无法执行冻结的 RFC 9180
A.1.1 权威向量，FATAL=1。根据硬停止规则，I1 未完成，不得进入 I2。

需要回到 I0 的最小依赖候选审查，选择一个公开支持 Base mode、目标 Suite、
独立 AAD、确定性 RFC 向量和 exporter 的成熟实现；用户批准修订后方可重启 I1。

