# 加密—授权—撤销—更新—解密协议

```mermaid
sequenceDiagram
  participant A as RevocationAgent
  participant DB as PostgreSQL
  participant S as Storage
  participant C as AuthorizationStateV2
  A->>DB: upsert(operationId), claim job
  A->>C: advance/revoke authorization state
  C-->>A: finalized epoch/stateVersion
  A->>A: build/sign Header candidate
  A->>S: put candidate; verify digest
  A->>C: commitHeader(expected versions,digest,opId)
  C-->>A: receipt/finality
  A->>DB: mark ACTIVE; advance cursor
```

推荐“链上授权变更先行、Header候选后建、链上锚定提交收尾”的两阶段补偿协议。授权变更后至新 Header生效前系统 fail-closed，避免旧用户继续获取材料；存储先写产生的孤儿对象可回收，不能被客户端接受。

上传/初次授权生成 CK、Body和 Header v1；访问时同时验证CAP2、旧授权合约、V2锚点、Header签名/摘要/版本，再解封装CK并逐块AEAD解密。撤销按受影响资源逐一排队；合法用户取得新 envelope，撤销用户不在接收者集合。交易未知先查 receipt/链状态，禁止盲目重复推进版本。
