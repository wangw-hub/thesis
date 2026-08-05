# 研究内容二 Besu 架构修订追踪表

| 编号 | 风险等级 | 修改位置 | 修改方式 | 状态 | 证据 |
|---|---|---|---|---|---|
| M1 | 重大 | `AuthorizationState.sol`、网关 | 新增独立 `stateVersion`，所有资源授权状态迁移递增 | 已解决 | 合约测试、真实链旧 Epoch 拒绝 |
| M2 | 重大 | `besu_gateway.py`、`deploy_besu.py` | 本地签名并提交原始交易，校验 sender 与私钥一致 | 已解决 | 部署交易与网关测试 |
| M3 | 重大 | Web3 初始化 | 注入 QBFT/PoA 扩展头中间件 | 已解决 | 同区块快照读取成功 |
| M4 | 重大 | Issuer、Verifier | RPC 故障和状态竞态 fail-closed | 已解决 | `test_gateway_fail_closed.py` |
| G1 | 一般 | 部署说明 | 明确单机、开发密钥和集中治理限制 | 已解决 | V1.1、部署清单 |
| G2 | 一般 | 实验边界 | 故障数据仅作功能验证 | 已解决 | `fault-check.json` |
