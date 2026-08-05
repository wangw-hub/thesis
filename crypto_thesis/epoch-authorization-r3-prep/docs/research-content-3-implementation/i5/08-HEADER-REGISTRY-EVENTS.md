# HeaderRegistry 事件

`HeaderCommittedV1` 索引 resourceId、headerVersion、operationId，并记录 bodyVersion、keyVersion、updateKind、headerDigest、bodyObjectDigest。

最终测试从 INITIAL 成功回执解码到唯一事件，事件 operationId 与 OperationIdV1、数据库任务和链上 Anchor 一致。
