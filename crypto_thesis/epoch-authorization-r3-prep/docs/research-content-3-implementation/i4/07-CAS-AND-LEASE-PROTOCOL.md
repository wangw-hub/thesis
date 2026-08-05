# CAS与租约协议

CAS SQL同时匹配job_id、expected status和row_version；rowcount为0即
`STALE_WRITE_REJECTED`。并发双写仅一方成功。续租要求正确owner、未过期租约和
版本；过期CLAIMED唯一恢复为PENDING并追加RecoveryAudit，旧worker版本随后失败。
所有最终时间判断使用PostgreSQL `clock_timestamp()`。

