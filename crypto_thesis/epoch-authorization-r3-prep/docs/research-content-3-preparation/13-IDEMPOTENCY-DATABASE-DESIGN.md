# 幂等数据库设计

使用独立 schema `r3_control`：

| 表 | 主键/唯一约束 | 关键状态 |
|---|---|---|
| revocation_event_cursor | `(chain_id,contract,stream)` | safe_block/hash |
| header_update_job | job_id；唯一 `(chain,contract,tx_hash,log_index,resource,target_epoch,key_version)` | READY/CLAIMED/RETRY/DEAD/DONE |
| header_version | `(resource_id,header_version)`；唯一 active partial index | CANDIDATE/STORED/CHAIN_PENDING/ACTIVE/ORPHAN |
| storage_object | digest | ref,size,pin_state |
| commit_attempt | `(operation_id,attempt_no)`；tx_hash唯一 | SENT/MINED/REVERTED/UNKNOWN |
| recovery_audit | audit_id | before/after/reason |
| dead_letter_job | job_id | error,manual disposition |

所有表含 created_at、updated_at、row_version、retry_count、last_error、idempotency_key。插入用 `ON CONFLICT`原子去重；领取队列用短事务 `FOR UPDATE SKIP LOCKED`，只适合多消费者队列而非一致快照；状态转换用 `WHERE row_version=:expected` CAS。默认 READ COMMITTED，关键对账可提高隔离并重试 serialization failure。

幂等键推荐 SHA-256(domain || chainId || contract || txHash || logIndex || resourceId || newEpoch || keyVersion)，不得只用resourceId。
