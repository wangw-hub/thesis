# 阶段5 非验证RPC节点部署报告

## 结论

阶段5通过。`experiment-client` 已部署独立的非验证Besu节点，服务为
`besu-rpc.service`，HTTP JSON-RPC仅绑定实验网地址
`192.168.6.133:8545`。该节点使用独立节点密钥，节点ID不属于冻结的四个
Validator，且未出现在QBFT验证者集合中。

## 冻结配置

- Besu：26.5.0
- chainId：2026072801
- Genesis SHA-256：`7ad57e14684a1e7b224ab3b83078bb59eee0e63d438ad2243339a6f5e8a7155a`
- P2P：`192.168.6.133:30303`
- HTTP RPC：`192.168.6.133:8545`
- RPC API：`ETH,NET,WEB3,QBFT`
- WebSocket：关闭
- Host allowlist：`192.168.6.133,localhost`
- 节点发现：关闭，使用冻结静态节点列表

## 验收结果

- 服务状态：active
- chainId：2026072801
- 验收区块高度：`0x1fd`
- peerCount：4
- Validator数量：4
- RPC节点是否为Validator：否
- Windows控制端RPC访问：通过

RPC节点ID：

`82a8ae5daa0ad3d00d58fad9a59f3567a08767191a667d55ec5df94bead2d02f41522d591db46f72def6d1e5f9ab013c8efce1ffccc165db6ae4681ad8ae0700`

## 修复记录

部署和验收期间共记录6次脚本级失败，涉及OpenSSL输出格式、远端sudo读取、
PowerShell数组展开和空比较结果处理。所有失败均保留在
`evidence/rpc/failure-attempt-*.json`。这些问题未改变Genesis、Validator
材料或已有链数据；最终验收由修复后的同一脚本重新完成。

## 证据

- `evidence/rpc/install.txt`
- `evidence/rpc/acceptance.txt`
- `evidence/rpc/summary.json`
- `evidence/rpc/windows-web3-clientVersion.json`
- `configs/experiment-client.toml`
- `configs/static-nodes-rpc.json`
- `systemd/besu-rpc.service`

阶段5达到阶段6准入条件。
