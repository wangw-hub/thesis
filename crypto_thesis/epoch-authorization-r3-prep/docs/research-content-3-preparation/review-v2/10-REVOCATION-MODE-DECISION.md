# 撤销模式决定

| 模式 | 安全生效 | 可用性/成本 | 决定 |
|---|---|---|---|
| R1同步逐Header后返回 | 直观 | F大时阻塞链事务/调用方 | 不采用 |
| R2纯惰性 | 旧材料窗口易被误用 | 首次访问突发 | 拒绝 |
| R3立即停止授权、Header按需 | 安全明确 | 合法用户不可用窗口不确定 | 可作降级，不作默认 |
| R4全批量资源更新 | 可控 | 峰值、失败域大 | 不采用 |
| R5立即停止授权+有界异步逐资源更新 | 最早fail-closed | 可限流、可恢复、总成本O(F) | **采用** |

两个生效点严格分离：

1. **授权撤销生效点**：AuthorizationState的epoch/status/stateVersion变更达到确认深度；Issuer从此拒绝旧快照并不向撤销用户生成任何未来envelope。
2. **数据可用恢复点**：资源的新Header在Storage中验证完成且HeaderRegistry COMMITTED达到确认深度；合法用户从此可取得新材料。

中间窗口内撤销用户和合法用户都不能用旧Header获取新材料；系统不得回退。任务按resourceId稳定排序、有限并发和重试预算处理，避免一次撤销把F伪写成O(1)。超SLO进入告警/死信，不放宽接受条件。

推荐名称：`IMMEDIATE_AUTHORIZATION_CUTOFF_BOUNDED_ASYNC_HEADER_REBUILD`。
