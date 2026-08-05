# r3_control Schema

迁移创建独立Schema及八张表：`schema_metadata`、`revocation_event_cursor`、
`header_update_job`、`header_version`、`storage_object`、`commit_attempt`、
`recovery_audit`和`dead_letter_job`。

地址使用20字节domain，摘要/operationId使用32字节domain；版本和链字段为有界非负
整数；关键状态使用PostgreSQL enum；外键、CHECK、唯一约束及部分唯一索引由数据库
执行。关键安全字段不使用无约束JSONB，数据库不存CK、ROOT_KEK或私钥。

