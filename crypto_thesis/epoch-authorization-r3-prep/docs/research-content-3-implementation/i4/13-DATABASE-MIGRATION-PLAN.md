# 数据库迁移

七个显式SQL迁移按文件名顺序在独立事务中应用，schema_metadata记录版本、名称、
SHA-256和时间。重复执行返回no-op；名称或SHA漂移立即拒绝。所有对象显式限定
`r3_control`，不依赖search_path，不包含DROP/CASCADE或RC2对象。

