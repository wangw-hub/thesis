# KeyStore 问题登记

| ID | 级别 | 问题 | 状态 | 关闭门 |
|---|---|---|---|---|
| KS-M01 | MAJOR | EncryptedCKRecord/HPKE/Body向量尚未执行 | READY_FOR_I1_AFTER_I0 | I1全部正负向测试通过 |
| KS-M02 | MAJOR | ROOT_KEK备份、双版本轮换和恢复尚无运行证据 | READY_FOR_I0 | I0冻结流程；I4/I7验证 |
| KS-M03 | MAJOR | 五VM systemd Credentials能力未知 | READY_FOR_I0 | I0逐机只读版本/能力核验 |
| KS-m01 | MINOR | KeyStore是服务可用性单点 | ACCEPTED_LIMITATION | 论文限制与恢复SLO |
| KS-m02 | MINOR | DPAPI不可作为Linux统一机制 | CLOSED_BY_DESIGN_EVIDENCE | 仅开发适配 |
| KS-m03 | MINOR | Python内存不能保证所有副本清零 | ACCEPTED_LIMITATION | 缩短生命周期并诚实表述 |
| KS-m04 | MINOR | 多设备使Envelope线性增长 | ACCEPTED_LIMITATION | E7测量 |
| KS-m05 | MINOR | 数据库+ROOT_KEK联合泄露全量失效 | ACCEPTED_LIMITATION | 分域、审计、应急方案 |
| KS-e01–03 | EDITORIAL | 术语、图例和论文措辞统一 | READY_FOR_I0 | I0文档编辑检查 |

用户选择项 OD-13 维持 `USER_DECISION_REQUIRED/READY_FOR_USER_DECISION`；V2最小原型项维持开放并映射I1。
