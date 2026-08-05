# 威胁边界冻结

| 威胁 | 冻结行为 |
|---|---|
| 数据库/CK记录泄露 | 无ROOT_KEK不能解CK |
| 存储/Header泄露 | 对象可公开复制；摘要、签名和链锚验证真实性/当前性 |
| Header篡改/旧版回滚 | JCS摘要、previousDigest、Registry当前锚和同块授权状态共同拒绝 |
| RPC中断/状态缺失 | GatewayUnavailable，停止签发和接受 |
| PostgreSQL中断 | Nonce无法消费即拒绝 |
| 存储中断 | 候选不COMMITTED；不回退旧Header |
| 代理崩溃/重复事件 | operationId、CAS、receipt对账和死信恢复 |
| 用户私钥泄露/共享 | 撤销旧userVersion，只阻止未来材料；既得CK不可追回 |
| ROOT_KEK泄露 | 结合密文记录可批量恢复CK；隔离、COMPROMISED、轮换并评估新Body |
| root/内存读取/完全主机失陷 | 软件KeyStore无法抵抗，接受限制 |
| 已取得明文或CK | 不可追溯撤回，明确非目标 |

论文主张只覆盖经实现和测试的边界，不把测试等同形式化安全证明，不把操作系统权限描述为HSM级隔离。
