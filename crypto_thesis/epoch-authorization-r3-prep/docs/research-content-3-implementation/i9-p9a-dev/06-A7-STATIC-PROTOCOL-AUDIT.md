# A7 静态协议审计

事件类型在执行前冻结为 `EpochAdvanced`，updateKind 冻结为 `HEADER_ONLY`。事件身份由 chainId、block、transactionHash、logIndex 组成；任务幂等键防止重复业务效果。recipient index 不完整时 Fail-Closed。Header anchor 使用事件携带的新 epoch/stateVersion，不在运行后改变 updateKind。
