# 阶段A 基础设施审计与Git冻结报告

## 结论

阶段A未通过，并触发硬性停止。当前五节点QBFT基础设施本身仍满足已冻结的
运行条件，但Git安全审计确认一个已跟踪的历史开发链脚本硬编码了真实Besu节点
私钥。根据本轮任务的硬性规则，后续阶段B至I不得开始。

## 已通过的只读基础设施检查

- 五台Besu服务均为active。
- 五台Besu版本均为26.5.0，Java为21。
- chainId为2026072801（`0x78c36ae1`）。
- 当前采样区块高度为`0x49f`，peerCount为4。
- Validator集合数量为4，且与公共清单一致。
- 本地Genesis SHA-256为
  `7ad57e14684a1e7b224ab3b83078bb59eee0e63d438ad2243339a6f5e8a7155a`，
  与冻结值一致。
- 当前五节点私密目录未被Git跟踪。

## 硬性停止原因

`blockchain/besu/scripts/prepare.ps1` 的第15行包含一个硬编码32字节十六进制
私钥，并将其写入Besu节点`key`文件。该文件由Git跟踪。这不是文件名或注释
造成的误报；已通过脱敏上下文确认其用途。私钥正文未写入本报告或证据。

另外五项扫描命中中，Genesis的`mixHash`和`extraData`属于公开链配置，
`PRIVATE KEY`文本位于注释或错误信息；它们不构成该硬停的直接原因。

## 未执行事项

- 未创建基础设施冻结提交。
- 未安装或配置PostgreSQL。
- 未生成正式角色账户。
- 未部署AuthorizationState合约。
- 未接入CAP2、Gateway或服务实例。
- 未执行安全、并发、故障或PILOT_ONLY实验。

## 恢复前必须完成的事项

1. 判定该历史开发链私钥是否仍可用；若可用，应撤销并生成新密钥。
2. 将私钥从`prepare.ps1`移出，改为受忽略的秘密文件或运行时环境输入。
3. 在明确授权下清理可达Git历史，或建立新的无秘密历史基线。
4. 重新执行`08-audit-infrastructure-freeze.ps1`，要求零真实秘密候选后方可继续。

证据：`evidence/infrastructure-freeze/audit.json`、
`evidence/infrastructure-freeze/hard-stop-secret-tracked.json`。
