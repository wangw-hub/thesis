# Epoch状态机规范

正式转换表与图见[docs/state-machine.md](docs/state-machine.md)。

冻结不变量：

```text
INV-1 Accepted(Cap) => Cap.epoch = CurrentEpoch(Cap.resourceId)
INV-2 Accepted(Cap, pk) => SHA256(pk) = Cap.userKeyId
INV-3 同一(resourceId, epoch, nonce)最多成功消费一次
INV-4 Accepted(Cap) => Cap.policyDigest = CurrentPolicyDigest(resourceId)
INV-5 SUSPENDED或REVOKED资源不得签发新能力
```

INV-1、INV-3至INV-5由状态机和验证顺序保证；INV-2同时依赖标准SHA-256与
Ed25519签名绑定。自动测试验证Python实现是否遵守这些规则，不替代密码学证明。
