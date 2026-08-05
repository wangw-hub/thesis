# 幂等键决定

逻辑operationId采用定长、长度前缀的大端二进制编码后SHA-256：

```
SHA-256(
  "R3-HEADER-UPDATE-OP-V1\0" ||
  u64(chainId) ||
  address20(authorizationContract) ||
  address20(headerRegistry) ||
  bytes32(eventSignature) ||
  bytes32(transactionHash) ||
  u32(logIndex) ||
  bytes32(resourceId) ||
  u64(targetEpoch) ||
  u64(targetStateVersion) ||
  u64(targetKeyVersion)
)
```

`resourceId`在R2 API中是文本、合约中是`keccak256(text)`；R3数据库/Registry统一存链上bytes32，并另存非权威displayResourceId。不得用平台默认字符串连接。

`blockNumber/blockHash`不进入operationId：它们属于事件观察与游标证据；同一交易在重组后重新包含时应恢复同一逻辑操作，而不是创建第二个任务。数据库保存observedBlockHash；若安全游标hash改变，先把未最终观察标记`REORGED`并补扫。若交易/log被永久移除，派生任务只能在尚未COMMITTED时取消；已COMMITTED需要链上状态对账和补偿事件，不静默删除。

HeaderRegistry的`operationId`全局唯一，重复相同参数为幂等no-op或返回已有锚点；相同operationId不同参数必须revert。
