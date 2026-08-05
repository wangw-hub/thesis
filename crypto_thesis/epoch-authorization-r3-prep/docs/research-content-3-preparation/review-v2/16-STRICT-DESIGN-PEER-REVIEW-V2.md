# 严格设计同行审稿V2

## 1. 密码工程审稿人

- FATAL：0。
- MAJOR：具体pyca HPKE后端与RFC A.1向量尚未执行；BodyFormat nonce/截断拒绝也只有规范。
- MINOR：4 MiB默认块需以I1/E6验证，不应写成性能最优。
- 支持：Base HPKE+外部Ed25519职责清晰；V1拒绝KEK_e避免无证据复杂化。
- 结论：贡献不是新原语，而是安全组合与可验证边界。

## 2. 区块链系统审稿人

- FATAL：0。
- MAJOR：HeaderRegistry Solidity、角色和同交易跨合约快照CAS尚待I5。
- MINOR：headerReferenceDigest的URI规范与事件字段需在ABI冻结时定义。
- 支持：S3避免破坏R2 Artifact/CAP2，优于V2迁移。
- 风险：两个合约的客户端同块读取必须是强制接口，而非文档建议。

## 3. 分布式状态机审稿人

- FATAL：0。
- MAJOR：UNKNOWN交易、重组后已提交锚点和孤儿对象的补偿，只能由I7/E8关闭。
- MINOR：租约时钟只用于工作分配，不能决定链上有效性。
- 支持：授权生效点与可用恢复点分离，且窗口内不回退。

## 4. 数据库一致性审稿人

- FATAL：0。
- MAJOR：无新增；DDL给出唯一ACTIVE、CAS、事件/游标和UNKNOWN状态。
- MINOR：需在实现时验证外键/部分索引迁移和死锁顺序；`SKIP LOCKED`不可用于对账。
- 支持：blockHash不进入逻辑operationId的重组处理合理。

## 5. 实验方法审稿人

- FATAL：0。
- MAJOR：接收者列表内嵌上限/分片阈值及HPKE次数的工程可行性需最小原型；不得凭设计宣称可扩展。
- MINOR：等效性界值、PILOT样本量和缓存控制仍须正式预注册。
- 支持：E7明确Body负控制与F增长，E8以不变量而非“服务恢复”为终点。

## 6. 软件工程审稿人

- FATAL：0。
- MAJOR：KeyStore正式部署档位尚需用户选择，否则威胁模型与可复现成本不确定。
- MINOR：JSON Schema不能表达所有数值上限、数组排序和跨字段算术，必须有语义验证器。
- 支持：I0–I11门控可执行且没有自动跨阶段。

## 7. 学位论文盲审专家

- FATAL：0。
- MAJOR：无新增。
- MINOR：论文需把“标准组件组合”与贡献区分：贡献是版本锚定、撤销窗口、幂等恢复及可证伪成本模型。
- EDITORIAL：统一使用“前瞻性撤销”，避免“前向安全撤销”等可能暗示密码学新性质的措辞。
- 支持：R1→R2→R3逻辑递进清楚，边界诚实。

## 8. 反方审稿人

- FATAL：0。未发现必须修改CAP2或使R2证据失效的必然条件。
- MAJOR：强调四项残余门：HPKE/Body最小验证、envelope规模、恢复实现、KeyStore选择。
- MINOR：HeaderRegistry增加一次链读/交易与论文复杂度，应由S1–S5消融解释。
- EDITORIAL：不得把“可恢复设计”写成“已证明恢复”。

## 综合决定

去重后：FATAL=0，MAJOR=4，MINOR=6，EDITORIAL=4。四个MAJOR均已分配至明确门：两个`REQUIRES_MINIMAL_PROTOTYPE`、一个`REQUIRES_FORMAL_IMPLEMENTATION`、一个`USER_DECISION_REQUIRED`；它们阻止自动实施，但不构成设计FATAL。当前状态维持`PREPARATION_COMPLETE_AWAITING_ENTRY_DECISION`。
