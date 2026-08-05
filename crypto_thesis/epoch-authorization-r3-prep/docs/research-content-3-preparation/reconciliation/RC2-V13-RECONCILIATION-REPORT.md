# RC2 V13 到 RC3 只读接口对账报告

## 结论

- RC2最终状态：`COMPLETED_WITH_VALID_RERUN_EVIDENCE`
- 当前主仓库HEAD：`b39e8a57bf9cf9f688ff5ff09b8b8ae067aa37aa`
- 审计源码基线：`26ef5bc8dc7b09e683aae8c7d7012f779f6847ed`
- V13预注册/实验代码提交：`8a3d795e22e5d9373c3053245e3b4040cd062dd5`
- 接口manifest SHA-256：`15e958a87e4e6b77711556f2554100d4b614763170890f96c8d6311ea8349898`
- V13终态artifact错误：0；冻结源码hash错误：0
- 最终判定：`RECONCILIATION_PASSED`

没有 `PROTOCOL_INTERFACE_CHANGE` 或 `EVIDENCE_INVALIDATING_CHANGE`。RC3不需要修改CAP2、AuthorizationState、RC2 PostgreSQL表或Fail-Closed语义，可以继续I0。

## R-01至R-10

| ID | 冻结事实 | 与RC3 V2/V3准备包对账 | 分类 |
|---|---|---|---|
| R-01 BesuStateGateway | 输入resource_id/user_id；同一确认块输出block number/hash及资源/用户状态；缺失或RPC错误抛GatewayUnavailable；无旧状态fallback | RC3继续组合只读Gateway；把“UNKNOWN值”收敛为异常/不可用状态，不放宽接受 | COMPATIBLE_INTERFACE_REFINEMENT |
| R-02 chain_read | V13每请求三次真实链读：Issuer初读、签名前复读、Verifier读；不存在状态缓存 | 三读属于实验请求边界，不要求RC3复制固定次数；采集/trace改动未改变协议 | PERFORMANCE_ONLY |
| R-03 Verifier | canonical、签名、链状态、资源/用户、策略、epoch、上下文、版本、key、operation、时间、策略、Nonce顺序冻结 | Nonce仍最后原子消费；数据库故障拒绝；无旧状态路径 | NO_DIFFERENCE |
| R-04 Issuer | 签发前读取与签名前复读必须一致；不确定/竞态返回SYSTEM_STATE_UNAVAILABLE | 与RC3材料释放fail-closed边界一致 | NO_DIFFERENCE |
| R-05 PostgreSQL | consumed nonce唯一键及单事务INSERT冻结；交易nonce单调；RC3只可新增r3_control | 完全支持独立r3_control，不修改RC2表 | NO_DIFFERENCE |
| R-06 CAP2 | 18个必选字段及3个可选cover字段、big-endian编码、Ed25519签名冻结 | RC3不扩展CAP2；Header绑定独立完成 | NO_DIFFERENCE |
| R-07 拒绝顺序 | 18步拒绝后才消费Nonce和ACCEPT；RPC/DB故障fail-closed | 无回退旧状态、旧Header或内存Nonce路径 | NO_DIFFERENCE |
| R-08 服务配置 | chainId 2026072901、AuthorizationState地址固定；chain mode拒绝CAP1/错误上下文 | RC3将显式注入两个合约地址；无隐式默认和跨链回退 | COMPATIBLE_INTERFACE_REFINEMENT |
| R-09 Git基线 | 治理HEAD、源码审计HEAD、V13代码HEAD均可定位；manifest/artifact可复算 | RC3依赖SHA从暂定基线更新为最终冻结SHA | PERFORMANCE_ONLY |
| R-10 RC2终态 | V13为唯一有效正式性能证据；无需再跑；接口FROZEN | 清除`BLOCKED_ON_RC2_V13`外部依赖 | COMPATIBLE_INTERFACE_REFINEMENT |

## 差异计数

- PERFORMANCE_ONLY：2
- COMPATIBLE_INTERFACE_REFINEMENT：3
- PROTOCOL_INTERFACE_CHANGE：0
- EVIDENCE_INVALIDATING_CHANGE：0

## 接口适配要求

1. 使用部署artifact ABI和`AuthorizationState.sol`；禁止使用缺少stateVersion的历史`IAuthorizationState.sol` stub。
2. Gateway不可用统一视为不可接受；不得把缺失状态猜测成可继续的业务状态。
3. RC3契约测试固定chainId、AuthorizationState地址、CAP2 canonical字段和Verifier拒绝顺序。
4. HeaderRegistry是新组合合约，不迁移或替换AuthorizationState。
5. RC3数据库只能使用独立`r3_control` schema。

本报告只读取冻结文档、manifest和列入manifest的源码；未读取或修改V13原始数据，未访问正式链或数据库。
