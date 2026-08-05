# 阶段4 四Validator节点部署报告

## 结论

阶段4通过。四个 `besu.service` 均为 active/enabled，以 `besu` 用户运行，P2P端口30303监听，静态拓扑连接完成，每台 `net_peerCount=3`。QBFT已持续产生区块，Validator集合严格为Genesis中的四个地址。

## 部署配置

- Besu版本：26.5.0；
- Genesis SHA-256：`7ad57e14684a1e7b224ab3b83078bb59eee0e63d438ad2243339a6f5e8a7155a`；
- P2P：各主机冻结IP的30303端口；
- discovery：关闭；
- static nodes：四个冻结Validator；
- 业务RPC：关闭；
- 诊断RPC：仅 `127.0.0.1:8545`，API为 `ETH,NET,QBFT`；
- systemd：统一 `/etc/systemd/system/besu.service`。

## 验收摘要

| 主机 | 服务 | peerCount | 验收区块高度 | 节点身份 |
|---|---|---:|---:|---|
| besu-validator-1 | active | 3 | `0x37` | 匹配 |
| besu-validator-2 | active | 3 | `0x37` | 匹配 |
| besu-validator-3 | active | 3 | `0x37` | 匹配 |
| besu-validator-4 | active | 3 | `0x38` | 匹配 |

相邻采集导致最后一台高度领先一个区块，属于2秒出块期间的正常时间差，不是链分裂。后续阶段6将在同一高度比较区块哈希。

## 修复记录

首次验收已观察到四服务active、peerCount=3和正常出块，但采集脚本读取 `key.pub` 时的shell重定向没有继承 `sudo -n`，并且未兼容 `ss` 将回环地址显示为 `[::ffff:127.0.0.1]:8545`。修复后仅重新采集证据，未重启或重部署服务。

证据：

- `evidence/validators/deployment/failure-attempt-1.json`
- `evidence/validators/deployment/summary.json`
- `evidence/validators/deployment/<hostname>-install.txt`
- `evidence/validators/deployment/<hostname>-acceptance.txt`

阶段4达到阶段5准入条件。
