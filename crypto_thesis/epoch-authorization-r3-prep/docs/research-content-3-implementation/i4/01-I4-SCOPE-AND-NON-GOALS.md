# I4范围与非目标

I4验证独立PostgreSQL `r3_control`持久任务状态机：迁移、OperationIdV1、幂等、
SKIP LOCKED、CAS、租约、重试、死信、游标、Header版本、对象映射、CommitAttempt
和追加审计。输入均为`SYNTHETIC_TEST_FIXTURE`，提交证据均为`TEST_DOUBLE_ONLY`。

I4不读取真实链事件、不广播交易、不实现HeaderRegistry、RevocationAgent或IPFS，
不修改RC2数据库，不生成性能结论，也不进入I5。

