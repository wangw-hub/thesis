# 重试、退避与死信

退避为确定性指数序列并封顶300秒；max_attempts受CHECK约束。耗尽后进入
FAILED_TERMINAL，再以单一事务CAS转DEAD_LETTER并插入dead_letter_job。原任务不删除，
死信不能自动恢复PENDING。

