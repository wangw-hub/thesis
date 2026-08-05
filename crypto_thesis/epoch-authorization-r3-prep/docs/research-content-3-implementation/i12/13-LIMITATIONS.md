# Limitations

`LimitationRegistryV1`（明细见 `formal-limitations.json`）

| ID | limitation |
|---|---|
| L-01 | 单节点 QBFT Formal 链；不评估多 Validator 共识性能（C-07 FORBIDDEN） |
| L-02 | 29 个冻结配置与每配置 5 次重复；有界工程精度而非总体推断（POWER_ANALYSIS_NOT_JUSTIFIED） |
| L-03 | 受控隔离实验环境（本地回环、Kubo 零 peer） |
| L-04 | 故障类别覆盖为冻结的 4 类对象故障（NONE/CORRUPT_RESTORE/CID_MISMATCH/BOTH_MISSING） |
| L-05 | 仅前瞻性撤销（FORWARD_LOOKING_REVOCATION_ONLY），不涉及追溯撤销/收回已获数据 |
| L-06 | Body 规模 64KiB-8MiB、recipient 2/8/32、affected 1/4 的范围限制 |
| L-07 | 运行时长范围受环境与时序影响；未做跨主机通用性推断 |
| L-08 | 实验验证而非形式化证明；不变量通过限于所测配置 |

