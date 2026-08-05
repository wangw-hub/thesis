# 阶段3 Validator Key核验、隔离和分发报告

## 结论

阶段3通过。四套最终密钥按 Genesis `extraData` 顺序固定映射到四台 Validator，每台仅获得自己的私钥、公钥、Genesis和公共清单。`experiment-client` 仅获得 Genesis 和公共清单，不含 Validator 私钥。

## 固定映射

| 主机 | Validator地址 | 私钥权限 |
|---|---|---|
| besu-validator-1 | `0x6e86edb3d714dc28e149edd280625ded1436fadf` | `640 root:besu` |
| besu-validator-2 | `0x1583e3922a8b9477d08e00919418a30e619ed49c` | `640 root:besu` |
| besu-validator-3 | `0x599d6230371a00524208ad63164aae5f90ab5d36` | `640 root:besu` |
| besu-validator-4 | `0xd7716b03e26dba82368fd4bf2c263da6a76e086b` | `640 root:besu` |

四个私钥SHA-256、四个公钥/节点ID以及四个地址均互不相同。私钥正文未写入日志和报告。

## 远程文件

每台Validator：

```text
/etc/besu/genesis.json      644 root:besu
/etc/besu/key               640 root:besu
/etc/besu/key.pub           644 root:besu
/etc/besu/validators.json   644 root:besu
```

`experiment-client`仅安装：

```text
/etc/besu/genesis.json
/etc/besu/validators.json
```

其 `/etc/besu/key` 不存在。

## 执行修复

首次尝试因 Windows PowerShell 5 顶层JSON数组被重复包装而在远程写入前停止。第二次尝试在 `besu-validator-1` 完整安装后，验收读取未使用 `sudo -n`，被正确的目录权限拒绝。修复后脚本仅在完整文件集与预期哈希完全一致时接续，未覆盖既有私钥；其他主机按正常路径完成。

证据：

- `evidence/validators/failure-attempt-1.json`
- `evidence/validators/failure-attempt-2.json`
- `evidence/validators/key-distribution.json`
- `evidence/validators/summary.json`
- `evidence/validators/<hostname>.txt`

阶段3达到阶段4准入条件。尚未创建服务或启动Besu。
