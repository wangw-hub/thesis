# Claim-Evidence Matrix

`FormalClaimEvidenceMatrixV1`（明细见 `formal-claim-evidence-matrix.json`）

| Claim | 摘要 | RQ | Experiment | Support |
|---|---|---|---|---|
| C-01 | VersionedHeaderV1 与链上/数据库固定块状态在预注册更新路径上保持一致、可验证且幂等。… | RQ-1 | E1 | SUPPORTED |
| C-02 | HEADER_ONLY 在同一语义类内的工程开销可按 recipient_count 与 affected_count 描述。… | RQ-2 | E2 | SUPPORTED |
| C-03 | BODY_ROTATION 在同一语义类内的工程开销可按 body_bytes 与 recipient_count 描述。… | RQ-3 | E3 | SUPPORTED |
| C-04 | 预先撤销路径在当前 Header 与释放窗口约束下 fail-closed，且不产生错误材料释放。… | RQ-4 | E4 | SUPPORTED |
| C-05 | RecoveryCoordinator 在预注册对象/服务故障下保持一致性、可解释并按规则 fail-closed。… | RQ-5,RQ-6 | E5 | SUPPORTED |
| C-06 | Kubo replica 相对于 LocalObjectStore 的影响仅在语义相同、对象大小和故障条件匹配的正式块内报告。… | RQ-5,RQ-6 | E5 | SUPPORTED_WITH_QUALIFICATION |
| C-07 | RC3 形式化设计不声称 QBFT 共识吞吐、共识延迟或多验证节点可扩展性。… |  | — | FORBIDDEN |

C-07 为 FORBIDDEN：不得形成 QBFT 共识性能/延迟/多 Validator 可扩展性结论。
