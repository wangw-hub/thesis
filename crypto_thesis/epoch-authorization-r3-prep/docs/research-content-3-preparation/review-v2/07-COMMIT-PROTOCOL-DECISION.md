# 提交协议决定

| 方案 | Fail-Closed与窗口 | 故障/孤儿 | Gas/复杂度 | 结论 |
|---|---|---|---|---|
| P1单阶段链上提交 | 无法同时创建链下对象 | 容易锚定不存在对象 | 低但不闭合 | 拒绝 |
| P2链上PENDING→上传→COMMITTED | 清晰但PENDING仍不可接受 | 两次Registry交易、悬挂PENDING | 高 | 不采用V1 |
| P3链下上传→一次COMMITTED | 候选不可接受，提交后原子可见 | 可能有可清理孤儿 | 低 | 作为链上子协议采用 |
| P4事件驱动两阶段状态机 | 覆盖授权先行、候选、提交与恢复 | 可审计、可重试 | 中 | **总体采用** |

V1协议是“P4编排 + P3锚定”：

1. AuthorizationState中的撤销/epoch/stateVersion在确认深度后成为授权撤销生效点。
2. 数据库以事件幂等键创建任务；构建并签名一次候选Header，写StorageGateway并回读验证。
3. HeaderRegistry `commitHeader`在同一交易内读取AuthorizationState当前快照，执行expected-value与版本链CAS，仅写COMMITTED锚点。
4. receipt达到确认深度后，数据库标记COMMITTED；UNKNOWN先按txHash、operationId和链上版本对账，禁止盲发新版本。

链上不记录PENDING：它不增加客户端可接受性，却增加Gas、悬挂状态和第二次交易。孤儿对象只能由保留期+引用/receipt对账清理。

```mermaid
sequenceDiagram
  participant AS as AuthorizationState
  participant A as RevocationAgent
  participant DB as r3_control
  participant S as StorageGateway
  participant HR as HeaderRegistry
  AS-->>A: finalized epoch/state event
  A->>DB: ON CONFLICT create job
  A->>S: put candidate; get+digest verify
  A->>HR: commitHeader(expected snapshot,digests,operationId)
  HR->>AS: getResource (same transaction)
  HR-->>A: COMMITTED receipt
  A->>DB: CAS COMMITTED
```
