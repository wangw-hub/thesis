# StorageObject映射

storage_object映射I2 ObjectReferenceV1的backend、namespace、objectKind、SHA-256
digest、size、schemaVersion和verified。对象摘要主键保持内容寻址幂等；冲突字段
不会被静默覆盖。I4闭环将本地不可变HEADER测试对象登记并回读验证。

