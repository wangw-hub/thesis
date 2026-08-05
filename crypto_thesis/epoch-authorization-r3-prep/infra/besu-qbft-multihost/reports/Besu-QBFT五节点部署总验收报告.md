# Besu QBFT五节点部署总验收报告

## 总体结论

Besu 26.5.0五节点QBFT联盟链部署成功。网络由四个独立Validator和一个
非验证RPC节点组成，五台Ubuntu虚拟机使用相同Genesis、独立节点密钥和
独立数据目录。阶段2至阶段7均已完成并通过各自验收。

## 冻结环境

| 项目 | 值 |
|---|---|
| Besu版本 | 26.5.0 |
| Java主版本 | 21 |
| 操作系统 | Ubuntu 24.04 LTS |
| 共识 | QBFT |
| chainId | 2026072801 |
| block period | 2秒 |
| request timeout | 4秒 |
| epoch length | 30000 |
| Validator数量 | 4 |
| Genesis SHA-256 | `7ad57e14684a1e7b224ab3b83078bb59eee0e63d438ad2243339a6f5e8a7155a` |
| 静态节点配置SHA-256 | `f252d0820a85895842c4be76b216c9ea3ba602e1324c570f36fbe43d9c768036` |
| 本地Git HEAD | `015973261556b614c47adc17a57b266ed6933920` |
| Git工作区 | dirty，未自动提交 |

## 节点与角色

| 主机 | IP | 角色 | 服务 | 最终状态 |
|---|---|---|---|---|
| besu-validator-1 | 192.168.6.129 | Validator-1 | besu.service | active |
| besu-validator-2 | 192.168.6.130 | Validator-2 | besu.service | active |
| besu-validator-3 | 192.168.6.131 | Validator-3 | besu.service | active |
| besu-validator-4 | 192.168.6.132 | Validator-4 | besu.service | active |
| experiment-client | 192.168.6.133 | 非验证RPC节点 | besu-rpc.service | active |

RPC地址为`http://192.168.6.133:8545`，仅开放`ETH,NET,WEB3,QBFT`。
WebSocket关闭，Host allowlist未使用通配符。

## Validator公共清单

| Validator | 地址 |
|---|---|
| Validator-1 | `0x6e86edb3d714dc28e149edd280625ded1436fadf` |
| Validator-2 | `0x1583e3922a8b9477d08e00919418a30e619ed49c` |
| Validator-3 | `0x599d6230371a00524208ad63164aae5f90ab5d36` |
| Validator-4 | `0xd7716b03e26dba82368fd4bf2c263da6a76e086b` |

完整节点ID保存在`validator-public/validators.json`。RPC节点ID为
`82a8ae5daa0ad3d00d58fad9a59f3567a08767191a667d55ec5df94bead2d02f41522d591db46f72def6d1e5f9ab013c8efce1ffccc165db6ae4681ad8ae0700`，
不在Validator集合中。

## 阶段结果

| 阶段 | 结果 | 主要证据 |
|---|---|---|
| 阶段2 Genesis及网络材料 | 通过 | `reports/stage-2-qbft-genesis.md` |
| 阶段3 Validator材料分发 | 通过 | `reports/stage-3-validator-keys.md` |
| 阶段4 四Validator部署 | 通过 | `reports/stage-4-validator-deployment.md` |
| 阶段5 RPC节点部署 | 通过 | `reports/stage-5-rpc-deployment.md` |
| 阶段6 链运行验收 | 通过 | `reports/stage-6-chain-acceptance.md` |
| 阶段7 故障测试准备 | 通过，仅准备 | `reports/stage-7-fault-test-plan.md` |

## 链运行验收

- QBFT Validator集合严格为冻结的4个地址。
- RPC节点不在Validator集合中。
- 五台Genesis和静态节点配置哈希一致。
- 五个节点ID及私钥哈希分别互不相同。
- 固定高度702的五节点区块哈希均为
  `0x825ae90e0a2704427d9698a514b295a814d0240d109e5f6a157debd6ad0ecb8a`。
- 阶段6初始高度为708至711，最终高度为751至754。
- 2026-07-28T11:15:17Z收尾检查高度为823（`0x337`），peerCount为4，
  说明链在验收后继续出块。
- RPC服务重启后恢复查询、P2P连接和同步。
- Validator-4重启期间网络继续出块，节点恢复后重新连接并追平。

## 警告与限制

1. Validator重启后15秒采样时仅恢复3个peer，但已active并追平；等待30秒后
   4-peer严格验收通过。该时序结果已完整保留。
2. 部署期间脚本兼容性与证据采集失败均以`failure-attempt-*.json`保留，
   未覆盖Genesis、密钥或链数据。
3. Validator上的HTTP RPC仅绑定`127.0.0.1`用于部署诊断，不对业务网络开放。
4. 当前工作区dirty，且整个基础设施目录尚未提交。`private/`已被
   `.gitignore`排除，`git ls-files`未发现被跟踪的私密材料。
5. 本轮没有部署AuthorizationState合约、PostgreSQL或IPFS。

## 原始证据索引

- `evidence/genesis/`
- `evidence/validators/`
- `evidence/rpc/`
- `evidence/acceptance/`
- `evidence/faults/preparation-summary.json`
- `evidence/artifact-sha256.json`
- `genesis/parameter-freeze.json`
- `validator-public/validators.json`
- `configs/`
- `systemd/`
- `scripts/powershell/`
- `scripts/remote/`

## 最终判定

```text
五节点QBFT链是否部署成功：是
四Validator集合是否正确：是
RPC节点是否为非验证节点：是
链是否持续出块：是
部署是否可复现：是
故障测试是否仅完成准备：是
是否采集论文正式性能数据：否
```
