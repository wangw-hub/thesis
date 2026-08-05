# F13 最终治理与冻结报告

## 结论

正式授权实验链 F0 至 F12 已连续执行并通过验收。F13 完成治理状态同步、最终在线健康检查、秘密扫描和公开证据哈希索引。

## 冻结对象

- 旧基础设施验证链：chainId `2026072801`，冷保留，旧数据和 Genesis 未修改。
- 正式授权实验链：chainId `2026072901`。
- 正式 Genesis SHA-256：`7d431f01aab7d0c55c58c09346ee1f9a43475322a4aca304cfbb172b9b32add4`。
- 正式合约：`AuthorizationState`，地址 `0x9ef44cf538d0df457ba77c556d8785e48bfc436d`。
- 合约 Artifact SHA-256：`b8cd8040e4a7683fb4454ea1cf3c3c4d97647611ad7cb3d616b72a35cf496ad5`。
- PILOT_ONLY：108 个配置、3,780 条记录。
- PILOT_ONLY 原始数据 SHA-256：`a4d0fcb12de587afe31e8af49854a9db7bcc40a04e5ef2a38865cd1c7d4d27b3`。

## 最终验收

- pytest：92 项通过。
- 最终在线链健康检查：通过。
- 攻击错误接受数：0。
- Baseline-I 与 Proposed-C 非预期语义差异数：0。
- Nonce 重复成功数：0。
- 状态竞争错误签发数：0。
- 受控故障 Fail-Closed：通过。
- 秘密扫描：`TRUE_SECRET=0`，`UNCLASSIFIED=0`。
- 正式性能实验准入：`FORMAL_EXPERIMENT_ADMISSION_APPROVED`。
- 正式性能数据采集：未执行。

本报告不把 PILOT_ONLY 数据解释为论文正式性能结论。
