# Negative Results

`NegativeResultRegistryV1`（明细见 `formal-negative-results.json`）

| class | result | boundary |
|---|---|---|
| NO_CLEAR_EFFECT | E5 BOTH_MISSING: LOCAL vs KUBO duration difference median=17.5 ms, Cliff's delta=0.04 | 匹配块内未观察到稳定差异 |
| NO_CLEAR_EFFECT | E5 CORRUPT_RESTORE: LOCAL vs KUBO duration difference median=-30.9 ms, Cliff's delta=0.04 | 匹配块内未观察到稳定差异 |
| NO_CLEAR_EFFECT | E5 NONE: LOCAL vs KUBO duration difference median=-48.3 ms, Cliff's delta=0.04 | 匹配块内未观察到稳定差异 |
| TRADEOFF | E5 CORRUPT_RESTORE: LOCAL_ONLY 恢复结果为 UNRECOVERABLE（Fail-Closed），KUBO_REPLICA 恢复为 CONSISTENT（repair=1）；端到端中位数差 -30.9 ms（Cliff's delta 0.04） | Kubo 副本决定恢复来源可用性（trade-off）；时长差异小 |
| LIMITED_SCOPE | 单节点 Formal 链；未评估多 Validator 共识性能（C-07 禁止） | 结论仅适用于受限应用层环境测量 |

负结果/弱效应保留，作为论文结论边界。
