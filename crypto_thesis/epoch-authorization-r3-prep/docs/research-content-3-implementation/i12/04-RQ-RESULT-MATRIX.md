# RQ Result Matrix

| RQ | Experiment | Runs | 结果 |
|---|---|---:|---|
| RQ-1 | E1 | 20 | 20/20 冻结不变量通过 |
| RQ-2 | E2 | 30 | HEADER_ONLY 30/30 valid；因素效应小 |
| RQ-3 | E3 | 45 | BODY_ROTATION 45/45 valid；8MiB 开销上升 |
| RQ-4 | E4 | 10 | Fail-Closed 通过；wrong release 0 |
| RQ-5/RQ-6 | E5 | 40 | 恢复正确性/成本按故障与副本报告 |

RQ-2 与 RQ-3 严格分离，不做跨语义 winner comparison。
