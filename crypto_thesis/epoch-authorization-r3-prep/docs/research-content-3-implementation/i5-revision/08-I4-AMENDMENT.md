# I4 增量修订

新增且仅新增迁移 `0008_add_body_version_and_update_kind.sql`；原 0001–0007 未修改。

`header_version` 增加：

- `body_version`
- `update_kind`
- `body_object_digest`
- `CHECK (body_version >= 1)`
- `CHECK (key_version = body_version)`
- 更新类型转换触发器

迁移在 PostgreSQL 16/r3_i4 的 `epoch_auth_r3_i4_test.r3_control` 成功执行。原数据映射为 `body_version=key_version` 并按前序版本归类；新增 6 项数据库修订测试。I4 合计 55/55，不变量违反 0，事务部分提交 0。
