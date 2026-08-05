# D1-D12崩溃恢复矩阵

D1事件写入前、D2事件后job前、D3 job后领取前、D4领取后Header前、D5对象后登记前、
D6 storage后header_version前、D7版本后job更新前、D8 READY后attempt前、D9 PREPARED、
D10 BROADCAST_UNKNOWN、D11确认前后边界、D12审计返回边界均用事务故障注入覆盖。

12个点均未产生部分数据库提交；可恢复状态保持幂等或fail-closed。对象存储位于数据库
事务外的孤儿对象仍由I2摘要幂等和后续对账处理，不被误称为跨系统原子事务。

