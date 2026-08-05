# 阶段7 受控故障测试计划

## 状态

本阶段仅完成脚本与方案准备，不执行计划性故障。所有停止和恢复脚本均要求
显式传入`-Execute`，缺少该开关时立即安全退出。

准备验收已通过。五个脚本均存在并完成SHA-256记录，四个PowerShell脚本
通过语法解析。验收摘要保存在
`evidence/faults/preparation-summary.json`。

## F1 停止单个Validator

- 目的：验证四Validator QBFT网络在停止一个Validator时仍能继续出块，并
  验证恢复节点能够重新连接和追平。
- 前置条件：阶段6通过；四Validator与RPC服务均active；peerCount均为4。
- 默认目标：`besu-validator-4`。
- 步骤：记录RPC区块高度；停止目标服务；按2秒周期采样至少30秒；确认区块
  增长；恢复服务；等待30秒；确认active、peer恢复和高度追平；比较停止前
  已确认高度的区块哈希。
- 通过条件：停止期间区块增长；恢复后目标节点高度与网络高度差不超过2个
  区块；同高度哈希一致；无持续共识错误。
- 回滚：立即运行恢复脚本；若恢复失败，保留服务日志并停止后续测试。
- 证据：`evidence/faults/f1_<UTC>/`。

## F2 RPC节点中断

- 目的：验证客户端能够明确观察RPC不可用，恢复后查询重新可用，同时
  Validator共识不依赖RPC节点。
- 前置条件：阶段6通过；客户端未配置不受控的备用RPC。
- 步骤：停止`besu-rpc.service`；确认8545查询失败；从Validator本地诊断RPC
  观察链仍增长；恢复RPC服务；等待30秒；确认查询、peer和同步恢复。
- 通过条件：中断被客户端明确观察；Validator链持续增长；恢复后RPC返回
  正确chainId和最新高度。
- 回滚：运行RPC恢复脚本；失败时保留日志并停止测试。
- 证据：`evidence/faults/f2_<UTC>/`。

## F3 节点重启恢复

- 目的：重复验证systemd异常恢复、P2P重连和账本追平。
- 方法：复用F1的停止/恢复与状态采集逻辑，但记录完整journal和固定高度哈希。
- 通过条件：服务恢复、peerCount回到4、节点追平、固定高度哈希一致。

## 禁止行为

- 不同时停止两个或更多Validator。
- 不删除`/var/lib/besu`、Genesis或节点密钥。
- 不重新生成Validator密钥或Genesis。
- 不修改冻结IP、chainId、QBFT参数或Validator集合。
- 不在本阶段采集论文正式性能数据。
- 不自动执行任何故障脚本。

阶段7完成，故障测试执行状态为“仅准备、未执行”。
