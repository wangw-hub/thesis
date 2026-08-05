# 共享 Nonce 后端设计与验收报告

## 选择

选择 PostgreSQL，而非 Redis。理由是唯一主键、事务、持久审计和故障恢复语义更适合论文复验。完整唯一键为 `(chain_id, contract_address, resource_id, epoch, nonce)`。

## 实现

`services/shared_nonce/schema.sql` 定义主键和清理索引；`PostgresNonceStore.consume_once` 使用 `INSERT ... ON CONFLICT DO NOTHING RETURNING 1`，允许多个 Verifier 竞争时仅一个成功。旧 Epoch 清理由显式保留策略触发。

## 验收状态

代码与模式已完成，尚无可用 PostgreSQL 服务，因此 50/100/500 并发、数据库重启、网络中断、事务失败和跨主机测试未执行。

```text
共享Nonce是否支持多Verifier：设计与实现是；实证验收否。
同一完整Nonce键成功消费次数：尚无真实PostgreSQL并发证据。
```

在真实测试完成前不得把该后端标记为通过。
