# 设计问题跟踪V2

| ID | 级别 | 问题 | 分类 | 关闭门 | 状态 |
|---|---|---|---|---|---|
| V2-M01 | MAJOR | pyca HPKE/RFC向量与BodyFormat黄金向量未执行 | REQUIRES_MINIMAL_PROTOTYPE | I1 | OPEN_GATED |
| V2-M02 | MAJOR | 内嵌recipientEnvelopes规模/阈值未知 | REQUIRES_MINIMAL_PROTOTYPE | I1/E7 PILOT | OPEN_GATED |
| V2-M03 | MAJOR | UNKNOWN/重组/孤儿补偿未由故障注入验证 | REQUIRES_FORMAL_IMPLEMENTATION | I7/E8 | OPEN_GATED |
| V2-M04 | MAJOR | 正式KeyStore档位未选择 | USER_DECISION_REQUIRED | G0用户决定 | OPEN_GATED |
| V2-m01 | MINOR | 默认chunkSize非性能结论 | REQUIRES_MINIMAL_PROTOTYPE | E6 | OPEN |
| V2-m02 | MINOR | HeaderRegistry URI/事件ABI待冻结 | REQUIRES_FORMAL_IMPLEMENTATION | I5 | OPEN |
| V2-m03 | MINOR | worker租约时钟边界需代码注释/测试 | REQUIRES_FORMAL_IMPLEMENTATION | I4/I6 | OPEN |
| V2-m04 | MINOR | DDL死锁顺序与迁移需验证 | REQUIRES_FORMAL_IMPLEMENTATION | I4 | OPEN |
| V2-m05 | MINOR | E7等效界值/样本量待预注册 | REQUIRES_MINIMAL_PROTOTYPE | I9/I10 | OPEN |
| V2-m06 | MINOR | Schema跨字段规则需语义验证器 | REQUIRES_FORMAL_IMPLEMENTATION | I3 | OPEN |
| V2-E01 | EDITORIAL | 统一“前瞻性撤销” | CLOSED_BY_DESIGN_EVIDENCE | 文档词表 | CLOSED |
| V2-E02 | EDITORIAL | 不写“已证明恢复” | CLOSED_BY_DESIGN_EVIDENCE | 主张门 | CLOSED |
| V2-E03 | EDITORIAL | 不写总撤销O(1) | CLOSED_BY_DESIGN_EVIDENCE | 主张门 | CLOSED |
| V2-E04 | EDITORIAL | IPFS不等于永久可用 | CLOSED_BY_DESIGN_EVIDENCE | 存储边界 | CLOSED |

没有问题授权当前任务进入实现；所有OPEN_GATED项必须由对应阶段证据或用户决定关闭。
