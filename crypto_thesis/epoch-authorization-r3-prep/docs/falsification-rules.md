# Falsification Rules

Baseline-I与Proposed-C共享同一策略、`I*`、`policyDigest`、用户、Epoch、
签名算法、Nonce数据库、CAP1安全字段、状态读取、请求序列和运行环境。

冻结假设：

- H-C1：两方案授权语义一致。
- H-C2：连续窗口或重复槽请求下，节点级复用可能降低匹配或缓存管理成本。
- H-C3：额外令牌、内存和状态开销不应超过节省收益。
- H-C4：碎片率升高时收益下降并可能消失。

若Proposed-C未实际消费Cover、无稳定收益、仅在人为场景占优、同等缓存可使
Baseline-I获得相同收益、长期更慢或额外开销超过收益，则将`C(P)`降级为
可选派生结构。不得依据结果修改Baseline-I或删除不利工作负载。
