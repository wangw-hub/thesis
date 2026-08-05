# 数据库Schema V1

R3使用独立`r3_control` schema，不修改R2的`consumed_nonces`或交易Nonce表。

| 表 | 主键/唯一 | 外键/状态 | 并发与保留 |
|---|---|---|---|
| chain_event | event_id；唯一(chain,auth,tx_hash,log_index) | OBSERVED/SAFE/REORGED/APPLIED | blockHash保留永久审计 |
| revocation_event_cursor | (chain,auth,event_signature) | safe block/hash，row_version | CAS推进；不可跳过缺口 |
| header_update_job | operation_id | FK event；状态机、lease、retry | `SKIP LOCKED`仅队列领取 |
| header_version | (resource,header_version)；operation唯一 | FK job/storage；候选状态 | 每资源唯一ACTIVE部分索引 |
| storage_object | object_digest | backend/ref/pin/verify | ref唯一；引用计数不作唯一真相 |
| commit_attempt | (operation,attempt_no)；tx_hash唯一 | nonce reservation/status | UNKNOWN保留至对账 |
| recovery_audit | audit_id | before/after/reason | append-only |
| dead_letter_job | operation_id | snapshot/manual disposition | 人工重开需审计 |

事务边界：

1. 事件入库、任务`ON CONFLICT DO NOTHING`和游标候选在一事务；只有范围全处理后单独CAS推进游标。
2. 任务领取：`SELECT ... ORDER BY available_at, operation_id FOR UPDATE SKIP LOCKED LIMIT n`，同事务写CLAIMED/lease；PostgreSQL官方明确SKIP LOCKED只适合队列而非通用一致视图。
3. 每一状态转移带`WHERE row_version=:expected AND status IN (...)`；rowcount必须为1。
4. 候选Header和storage对象入库在一事务；外部put不置于数据库事务内，以digest幂等补偿。
5. 交易nonce继续调用R2已冻结管理器；R3只引用reservation_id，不复制其表。

默认READ COMMITTED；对账按资源获取advisory/row lock并按固定顺序访问表，避免死锁。重试仅限明确瞬态错误，指数退避+抖动+上限；永久验证失败直接DEAD。
