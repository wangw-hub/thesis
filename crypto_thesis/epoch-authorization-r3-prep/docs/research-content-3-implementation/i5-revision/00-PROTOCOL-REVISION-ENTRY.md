# I5 协议修订入口

- 原状态：`I5_REQUIRES_PROTOCOL_REVISION`
- 原硬停止：`HARD_STOP_RC2_KEY_VERSION_INTERFACE_GAP`
- 原因：冻结的 `AuthorizationState.getResource` 不提供 `keyVersion`。
- 用户批准方向：`HEADER_REGISTRY_OWNED_CONTENT_KEY_VERSION`
- 修订边界：不修改 AuthorizationState、CAP2、研究内容二 ABI、Artifact、正式链或正式数据库。
- 审计原则：保留 `docs/research-content-3-implementation/i5/` 中的原硬停止证据；本目录只追加修订证据。

解决记录：`RC2_KEY_VERSION_INTERFACE_GAP_RESOLVED_BY_AUTHORITY_REALIGNMENT`。
