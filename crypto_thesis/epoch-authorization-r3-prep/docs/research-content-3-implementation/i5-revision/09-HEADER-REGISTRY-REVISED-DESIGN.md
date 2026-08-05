# HeaderRegistry V1 修订设计

HeaderAnchorV1 包含 operationId、resourceId、policyDigest、epoch、stateVersion、headerVersion、bodyVersion、keyVersion、updateKind、previousHeaderDigest、headerDigest、headerObjectDigest、bodyObjectDigest、committer、committedAtBlock 和 exists。

`commitHeaderV1` 必须依次：

1. 检查 HEADER_COMMITTER；
2. 拒绝已使用 operationId；
3. 从冻结 AuthorizationState 读取资源；
4. 检查 ACTIVE、policyDigest、epoch、stateVersion；
5. 从当前 HeaderRegistry 锚点检查更新类型与连续版本；
6. 强制 keyVersion=bodyVersion；
7. 检查 previousHeaderDigest 和非零对象摘要；
8. 写入不可变锚点、更新当前指针、消费 operationId；
9. 发出 HeaderCommittedV1。

合约不得读取 AuthorizationState 中不存在的 keyVersion，也不得写 AuthorizationState。
