# Formal Research Questions

The frozen questions are:

- **RQ-1** (CORRECTNESS, SECURITY_BEHAVIOR): 在固定链上块与数据库快照边界下，VersionedHeaderV1、AuthorizationState 和 HeaderRegistry 的状态更新是否保持可验证的一致性与幂等性？
- **RQ-2** (ENGINEERING_OVERHEAD, SCALABILITY): 在不改变安全语义的同类任务内，HEADER_ONLY 的端到端工程开销如何随 recipient_count 与 affected_count 变化？
- **RQ-3** (ENGINEERING_OVERHEAD, CORRECTNESS): BODY_ROTATION 在固定语义内如何随 body_bytes 与 recipient_count 变化，并是否保持旧版本不可释放和新版本可验证？
- **RQ-4** (SECURITY_BEHAVIOR, CORRECTNESS): 预先撤销事件发生后，当前 Header 的可用性窗口与材料释放判定是否 fail-closed、可追踪且不产生错误释放？
- **RQ-5** (RECOVERY, SECURITY_BEHAVIOR, ENGINEERING_OVERHEAD): 在 LocalObjectStore 与 Kubo replica 两种已冻结对象来源下，RecoveryCoordinator 能否在对象缺失、损坏或 CID 不一致时保持一致性并完成预注册的恢复动作？
- **RQ-6** (PERFORMANCE, RECOVERY): 在受限且明确标注的独立正式环境中，链上、数据库和对象存储边界的组合是否产生可重复的应用层开销与恢复成本？

RQ-2 and RQ-3 are separate semantic analyses. No question asks whether one update kind is globally better than the other.
