# 链状态架构决定

## S1–S5比较

| 方案 | R2证据影响 | 一致性/恢复 | 复杂度 | 决定 |
|---|---|---|---|---|
| S1修改AuthorizationState | Artifact、地址、验收全部失效 | 单合约简单 | 高风险 | REJECTED_OPTION |
| S2 AuthorizationStateV2迁移 | 旧状态迁移与双合约职责混杂 | 可闭合但迁移面大 | 最高 | REJECTED_OPTION |
| S3独立HeaderRegistry | 旧合约/CAP2完全不变 | 提交交易内只读校验旧状态；客户端同块双读 | 中 | **RECOMMENDED** |
| S4仅摘要事件 | 缺少可查询当前状态与CAS | 回滚/恢复依赖全历史重放 | 中 | REJECTED_OPTION |
| S5仅旧字段 | 无Header摘要、版本或当前引用 | 无法拒绝合法签名旧Header | 低但不足 | REJECTED_OPTION |

## HeaderRegistry V1职责

构造参数固化`authorizationContract`。`commitHeader(resourceId, expectedEpoch, expectedStateVersion, expectedPolicyDigest, headerVersion, keyVersion, previousHeaderDigest, headerDigest, headerReferenceDigest, operationId)`在同一交易内调用旧合约`getResource`，要求状态非REVOKED且快照完全相等，并以CAS要求`headerVersion=old+1`和previousDigest连续。链上仅存COMMITTED当前锚点，不存秘密、完整URI或PENDING候选。

CAP2仍只绑定AuthorizationState地址。Header与客户端另外绑定HeaderRegistry地址；这不是CAP2语义修改。客户端在同一确认区块读取两个合约，接受条件见[客户端不变量](09-CLIENT-ACCEPTANCE-INVARIANTS.md)。

最终建议：不需要AuthorizationStateV2；需要独立HeaderRegistry。该选择关闭原M-03，但合约正确性仍在I5阶段验证。
