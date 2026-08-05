# 治理更新提案 V2

本文件是提案，不直接修改 `docs/project-governance/`。

## 建议更新

### 01-CURRENT-STATE.md / project-state.json

- R3 状态设为 `PREPARATION_COMPLETE_AWAITING_ENTRY_DECISION`；
- `RESEARCH_CONTENT_2_V13_ACTIVE=true` 保持到主任务正式报告结束；
- 明确 R3 未实现、未测试、未验证、未完成。

### 02-DECISION-LOG.md

建议登记：

- R3-DV2-01：拒绝迁移型 AuthorizationStateV2，采用独立 HeaderRegistry；
- R3-DV2-02：CAP2 和 AuthorizationState 核心语义为禁止修改依赖；
- R3-DV2-03：Body 使用分块 AES-256-GCM；
- R3-DV2-04：HPKE 使用 RFC 9180 Base/X25519/HKDF-SHA256/AES-128-GCM，须经 I1；
- R3-DV2-05：V1 直接按接收者封装 CK，不引入 KEK_e；
- R3-DV2-06：链下候选上传后一次 COMMITTED；
- R3-DV2-07：立即授权撤销、逐资源异步 Header 更新；
- R3-DV2-08：LocalObjectStore 优先，IPFS 延后；
- R3-DV2-09：用户 KeyStore 决策与 V13 对账是实现准入条件。

### 04-CLAIM-EVIDENCE-MATRIX.md

将 R3 主张标为设计/预注册状态；不得填写性能数值。为前瞻性撤销、Body-size 解耦、恢复闭环分别设置反证条件。

### 06-RISK-AND-HARD-STOPS.md

增加：

- 修改 RC2 CAP2 或 AuthorizationState 核心语义；
- 使用旧 Header 维持可用性；
- 将链下 PENDING 对象视为可接受；
- 未通过标准测试向量即进入集成；
- 将旧明文/CK 泄露描述为可撤回。

### 07-NEXT-ACTION.md

唯一下一步建议为：V13 最终审稿结束后执行只读接口对账；对账通过且用户完成 KeyStore 决策后，再由用户决定是否批准 I0。

### 09-SOURCE-OF-TRUTH-INDEX.md

将 `review-v2/18-FORMAL-IMPLEMENTATION-ENTRY-PACKAGE.md`、V2 state 和 V2 SHA manifest 登记为 R3 第二阶段设计权威入口。
