# I5 不变量报告

协议修订与 I5 核心不变量均通过：AuthorizationState 不可变绑定、operationId 一次性、版本单调、previous 连续、授权状态核验、角色隔离、锚点不可变、成功回执先于数据库 COMMITTED、同块高双读、key/body 相等。

- 链上不变量违反：0
- 数据库不变量违反：0
- 事务部分提交：0
- 重复任务产生第二 Anchor：0
