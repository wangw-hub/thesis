# Besu 接入前后授权语义一致性报告

## 方法

内存后端与 Besu 后端复用相同 Issuer、Verifier、执行器、策略仓库、CAP 字段和拒绝顺序。Besu 仅替换授权状态来源，并把 CAP1 升级为带链上下文和状态版本的 CAP2。

## 结果

本地既有语义与 CAP2 自动测试通过。真实 Besu 检查在 chainId 20260728、合约 `0xc705...898B` 上得到：

| 场景 | 结果 |
|---|---|
| 当前状态 CAP2 | 接受 |
| Proposed-C 当前状态 CAP2 | 接受 |
| 已消费 CAP2 再次提交 | `NONCE_REPLAY` |
| 错误合约地址 | `CHAIN_CONTEXT_MISMATCH` |
| 策略更新后的旧 CAP2 | `POLICY_DIGEST_MISMATCH` |
| Epoch 推进后的旧 CAP2 | `EPOCH_MISMATCH` |
| 用户密钥轮换后的旧 CAP2 | `USER_VERSION_MISMATCH` |
| 错误 chainId | `CHAIN_CONTEXT_MISMATCH` |
| 暂停用户 | `USER_INACTIVE` |
| 撤销资源 | `RESOURCE_INACTIVE` |

证据为 `blockchain/besu/semantic-check.json`。该结果支持“接入后未改变已定义授权语义”，不等价于对所有实现和网络条件的形式化等价证明。
