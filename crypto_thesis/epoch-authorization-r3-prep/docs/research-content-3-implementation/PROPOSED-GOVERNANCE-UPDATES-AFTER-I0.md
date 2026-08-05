# I0后治理更新提案

本文件只属于RC3独立worktree，不修改主仓库治理包。

- RC2：保持`COMPLETED_WITH_VALID_RERUN_EVIDENCE`；interface manifest SHA登记为`15e958…9898`。
- RC3：状态更新为`I0_COMPLETED_AWAITING_I1_APPROVAL`，不是IMPLEMENTED/TESTED/VALIDATED。
- 决策：登记`KEYSTORE_OPTION_A`、cryptography 49.0.0和rfc8785 0.1.4候选、独立Header signer。
- 风险：systemd精确版本未核验、候选wheel hash未冻结、I1向量未运行。
- Claim Matrix：R3密码、KeyStore和Header主张仍为`NOT_YET_SUPPORTED`。
- Experiment Registry：I1及E6-E9仍为`NOT_STARTED`。
- Next Action：仅在用户明确批准I1且I1进入清单全部满足后执行标准密码最小验证。
- 禁止：修改RC2 CAP2/AuthorizationState/PostgreSQL表、执行正式链交易、生成正式密钥或把I0文档当成实现证据。
