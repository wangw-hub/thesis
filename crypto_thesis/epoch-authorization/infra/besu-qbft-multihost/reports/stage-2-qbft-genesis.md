# 阶段2 QBFT Genesis及网络材料报告

## 结论

阶段2通过。Besu 26.5.0 官方 `operator generate-blockchain-config` 在 `experiment-client` 上生成一次最终网络材料；正式 Genesis、四套互异 Validator 材料、公共地址和节点ID均已核验。私钥仅保存在本地 Git 忽略目录，远端暂存已经删除，尚未向 Validator 分发，未启动Besu。

## 冻结参数

| 参数 | 值 |
|---|---|
| chainId | `2026072801` |
| consensus | QBFT |
| block period | 2秒 |
| request timeout | 4秒 |
| epoch length | 30000 |
| gasLimit | `0x1fffffffffffff` |
| zeroBaseFee | false |
| 初始Validator | 4 |
| alloc | 空 |

仓库此前只有受控开发链 `20260728`，因此按正式多主机规则选用未出现且不同的新值 `2026072801`。完整依据见 `genesis/parameter-freeze.json`。

## 官方CLI行为

实际帮助确认生成命令在一次调用中同时生成 Genesis、Validator私钥和公钥：

```text
/opt/besu/bin/besu operator generate-blockchain-config
  --config-file=/tmp/besu-qbftConfigFile-2026072801.json
  --to=/tmp/besu-qbft-stage2-2026072801
```

未手工拼接 `extraData`，未使用第三方密钥生成器。

## 最终材料

Genesis SHA-256：

```text
7ad57e14684a1e7b224ab3b83078bb59eee0e63d438ad2243339a6f5e8a7155a
```

固定映射按 Genesis `extraData` 解码顺序确定：

| 序号 | 主机 | Validator地址 |
|---:|---|---|
| 1 | besu-validator-1 | `0x6e86edb3d714dc28e149edd280625ded1436fadf` |
| 2 | besu-validator-2 | `0x1583e3922a8b9477d08e00919418a30e619ed49c` |
| 3 | besu-validator-3 | `0x599d6230371a00524208ad63164aae5f90ab5d36` |
| 4 | besu-validator-4 | `0xd7716b03e26dba82368fd4bf2c263da6a76e086b` |

四个地址、节点ID、私钥SHA-256均唯一。私钥哈希只保存在被忽略的私密目录，不在本报告中展开。

## 失败与修复记录

前两次尝试均在官方生成成功后的 RLP 解码验收步骤失败，原因分别为把整个 Genesis 和带JSON引号的字符串作为解码输入。每次失败产生的密钥均只存在于固定远端暂存路径，未拉回或分发，并在重试前完整删除。第三次使用原始 `0x...` extraData文本通过。

初版公共映射曾按地址字典序排列。交叉核验发现该顺序与 Genesis 编码顺序不同；在分发前已使用 `besu rlp decode --type=QBFT_EXTRA_DATA` 顺序修正，未改变或重生成最终 Genesis和密钥。

证据：

- `evidence/genesis/failure-attempt-1.json`
- `evidence/genesis/failure-attempt-2.json`
- `evidence/genesis/mapping-correction.json`
- `evidence/genesis/decoded-validators.txt`
- `evidence/genesis/summary.json`

## 安全与准入

- `infra/besu-qbft-multihost/private/` 已被 `.gitignore` 忽略；
- `git ls-files` 未发现私密目录文件；
- `experiment-client` 上固定阶段2暂存路径均不存在；
- Genesis尚未部署；
- 没有Besu进程或服务启动。

阶段2达到阶段3准入条件。
