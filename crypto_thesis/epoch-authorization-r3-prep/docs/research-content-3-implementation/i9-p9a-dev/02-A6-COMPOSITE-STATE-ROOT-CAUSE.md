# A6 根因

失败资源固定块 87966 上，AuthorizationState 与 HeaderRegistry 状态均存在。授权状态为 epoch/stateVersion 2/2，Header 为 1/1。旧网关把跨合约版本不一致映射为 `UNKNOWN/CROSS_CONTRACT_STATE_MISMATCH` 并丢弃双方已解码状态，运行器随后统一映射为 `COMPOSITE_STATE_MISSING`。

精确根因是 `GATEWAY_REJECTION`，并非状态不存在。
