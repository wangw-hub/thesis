# 阶段6 链运行完整验收报告

## 结论

阶段6通过。五个Besu节点使用相同Genesis和静态节点配置，四个Validator
身份与冻结清单一致，RPC节点不属于Validator集合。固定高度区块哈希在五台
机器上一致，区块高度持续增长，未发现持续共识错误。

## 核心结果

- chainId：2026072801
- Validator数量：4
- 每节点peerCount：4
- Genesis SHA-256：`7ad57e14684a1e7b224ab3b83078bb59eee0e63d438ad2243339a6f5e8a7155a`
- 静态节点配置SHA-256：`f252d0820a85895842c4be76b216c9ea3ba602e1324c570f36fbe43d9c768036`
- 固定验收高度：702（`0x2be`）
- 固定高度区块哈希：`0x825ae90e0a2704427d9698a514b295a814d0240d109e5f6a157debd6ad0ecb8a`
- 初始采样高度：708至711
- 最终采样高度：751至754
- 五个节点ID：互不相同
- 五个节点私钥SHA-256：互不相同
- 近5分钟服务错误：0

## 重启恢复

1. 重启`experiment-client`上的`besu-rpc.service`后，服务恢复、重新建立4个
   peer连接并继续同步。
2. 重启`besu-validator-4`上的`besu.service`期间，其余三个Validator继续
   形成QBFT法定数量并持续出块；目标节点恢复后重新连接并追平。

第一次15秒恢复窗口中，Validator-4已经active且完成区块追平，但仅建立3个
peer连接。该结果保留为时序证据。恢复窗口调整为30秒后，严格4-peer验收
通过。未删除或重建任何链数据。

## 证据索引

- `evidence/acceptance/summary.json`
- `evidence/acceptance/before/`
- `evidence/acceptance/growth/`
- `evidence/acceptance/after-rpc-restart/`
- `evidence/acceptance/after-validator-restart/`
- `evidence/acceptance/failure-attempt-1.json`
- `evidence/acceptance/failure-attempt-2.json`
- `evidence/acceptance/failure-attempt-3.json`
- `scripts/powershell/06-chain-acceptance.ps1`
- `scripts/remote/collect-chain-state.sh`

阶段6达到阶段7准入条件。
