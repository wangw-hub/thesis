# 数据库—链—对象闭环

迁移 0009 增加 `REAL_ISOLATED_CHAIN_ONLY`、真实回执状态及 nonce/block/receipt 字段。最终任务：

- Job：COMMITTED
- CommitAttempt：CONFIRMED_REAL_CHAIN
- receiptStatus：1
- blockNumber：832
- OperationId 与触发事件、Anchor、数据库一致
- 数据库不变量违反：0
- 事务部分提交：0

正式 PostgreSQL 未修改。
