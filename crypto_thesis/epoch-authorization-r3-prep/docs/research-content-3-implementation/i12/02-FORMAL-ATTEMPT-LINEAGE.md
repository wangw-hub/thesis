# Formal Attempt Lineage

`FormalAttemptLineageAuditV1`

| attemptId | Git SHA | raw dirs | 进入最终统计 | disposition | 原因 |
|---|---|---:|---|---|---|
| FORMAL_20260802T081001Z_a423bb0 | `a423bb0d1331` | 0 | 否 | SUPERSEDED_NO_RAW | canary 阶段 config digest 校验失败（manifest 与 runner 摘要公式未统一） |
| FORMAL_20260802T081341Z_b3f806d | `b3f806dae728` | 150 | 否 | SUPERSEDED | phase contract 要求了 recovery 阶段而执行内嵌于 fault observation，31 runs 未封存 |
| FORMAL_20260802T084518Z_7d5bc91 | `7d5bc91f9c10` | 180 | 否 | SUPERSEDED | fault 证据字段缺失（expectedOutcome/injectionObserved/cleanup）导致 30 runs strict 校验失败 |
| FORMAL_20260802T090650Z_e64a4f7 | `e64a4f7d781d` | 180 | 否 | SUPERSEDED | E4-C2 缺最终 composite 验证与基线行 recovery 标签（M-02/数据质量） |
| FORMAL_20260802T093003Z_0838aaa | `0838aaa38cf6` | 180 | 否 | SUPERSEDED | E4-C2 header 闭合锚点未绑定撤销意图状态（epoch）导致最终状态不一致 |
| FORMAL_20260802T095534Z_4d12daf | `4d12daf78146` | 180 | 是 | FINAL_ACCEPTED | 最终冻结实现；180/180 raw 全部通过 strict 校验 |

FINAL_ACCEPTED_ATTEMPT_COUNT=1；SUPERSEDED_ATTEMPTS_IN_STATISTICS=0；CROSS_EXECUTION_SHA_MIX=0。所有历史 attempt 的 raw 证据均保留在远程权威目录。
