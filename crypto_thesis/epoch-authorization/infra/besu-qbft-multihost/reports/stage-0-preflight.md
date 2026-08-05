# 阶段0只读预检报告

## 执行结论

阶段状态：失败并停止。第一台主机 `besu-validator-1` 在接收远程 Bash 脚本时返回退出码 1，其余四台未执行，阶段1未开始。

## 失败信息

```text
bash: line 137: $'\r': command not found
```

Windows PowerShell 读取脚本后保留了 CRLF，SSH 标准输入将其原样发送给 Bash。错误发生在远程脚本解析阶段，不代表 Ubuntu、SSH、sudo、Java、网络或 Besu 资产检查失败。

## 远程变更

无。阶段0脚本只执行只读命令，且本次在脚本解析时退出，没有创建、修改或删除远程文件。

## 原始证据

- `evidence/preflight/failure-20260728T092003Z.json`
- `evidence/preflight/failure-20260728T092003Z.txt`

## 修复与回滚

无需远程回滚。建议仅修改 `00-preflight.ps1`，在内存中将脚本载荷的 CRLF 规范化为 LF：

```powershell
$scriptText = $scriptText -replace "`r`n", "`n"
```

随后从 `besu-validator-1` 重新执行完整阶段0，不复用本次失败作为任何主机通过证据。

## 阶段记录

| 项目 | 值 |
|---|---|
| 执行时间UTC | 2026-07-28T09:20:03.7016507Z |
| Git提交 | `015973261556b614c47adc17a57b266ed6933920` |
| 工作区 | dirty |
| 涉及主机 | 仅尝试 `besu-validator-1` |
| 成功预检主机 | 0/5 |
| 阶段1 | 未开始 |
| 下一阶段准入 | 否 |

## 第二次尝试

用户确认重试后，控制端先在内存中将 CRLF 替换为 LF，但 PowerShell 原生管道向 `ssh.exe` 写入字符串时仍附加 Windows 换行。`besu-validator-1` 再次在第137行解析失败，退出码为1。

第二次尝试仍未修改远程系统，未执行其余四台主机，未进入阶段1。新增证据：

- `evidence/preflight/failure-20260728T092249Z.json`
- `evidence/preflight/failure-20260728T092249Z.txt`

下一次修复必须取消 PowerShell 管道，改用 `System.Diagnostics.ProcessStartInfo` 的重定向标准输入直接写入 LF 载荷。阶段0保持失败状态，等待再次确认。

## 第三次尝试

第三次尝试在本地 PowerShell 解析阶段失败，尚未建立 SSH 连接。错误为插值字符串中的 `$jsonExit:` 与 `$textExit:` 未使用变量边界，导致 ParserError。

新增证据：

- `evidence/preflight/failure-20260728T092436Z.json`
- `evidence/preflight/failure-20260728T092436Z.txt`

修复仅需将变量写为 `${jsonExit}` 和 `${textExit}`，并在下一次远程执行前先进行本地 PowerShell 语法检查。阶段0仍未完成，等待再次确认。

## 第四次尝试

第四次尝试已通过本地 PowerShell 语法检查，但在创建 `ProcessStartInfo` 时发现当前 Windows PowerShell 运行时没有 `StandardInputEncoding` 属性。失败发生在 SSH 连接前，远程机器没有变更。

新增证据：

- `evidence/preflight/failure-20260728T092604Z.json`
- `evidence/preflight/failure-20260728T092604Z.txt`

下一次仅删除不兼容属性。Bash 载荷为 ASCII 且已移除 CR 字符，仍可通过重定向标准输入安全传输。阶段0继续等待确认。

## 第五次尝试：远程资产阻断

第五次尝试已通过本地 PowerShell 语法检查，并成功在 `besu-validator-1` 完成只读采集。此前脚本的两个误报已经消除：空目录不再被视为 Besu 资产，`systemctl` 表头也不会被视为服务单元。

本次失败不是控制脚本问题。采集结果表明该主机已经存在实际 Besu 分发目录：

```text
/opt/besu/besu-26.5.0/   # 已包含 bin、lib、LICENSE、README 等文件
/opt/besu/current -> besu-26.5.0
```

附加只读核验确认 `/opt/besu` 及其内容当前由 `thesis:thesis` 所有。根据阶段0准入规则，发现既有 Besu 资产时必须停止，不能通过反复重试、覆盖或删除来取得“通过”结果。其余四台主机和阶段1均未执行。

新增证据：

- `evidence/preflight/besu-validator-1.json`
- `evidence/preflight/besu-validator-1.txt`
- `evidence/preflight/summary.json`
- `evidence/preflight/failure-20260728T093002Z.json`

要继续，必须先明确该安装是否为允许复用的受控既有安装；若不是，则需要单独授权清理并重新部署。阶段0在当前规则下保持阻断状态。

## 已授权恢复：清理前资产清单重试

用户已明确授权清理后重新部署。首次对五台主机执行清理前只读资产清单时，Windows PowerShell 到 Bash 的引号转义错误导致远程 Bash 在解析时退出；没有执行清理命令，也没有远程变更。该控制端失败记录为 `evidence/preflight/failure-20260728T093300Z.json`。后续将以固定路径、无嵌套变量的只读命令重新核验，然后只清理已确认的旧 Besu 资产。

## 最终阶段0结果：通过

在用户授权的旧资产清理完成后，阶段0于 `2026-07-28T10:12:52.8420657Z` 重新执行并通过。五台主机均完成只读采集（`5/5`），失败列表为空。所有主机均匹配冻结的主机名、IPv4和角色；`machine-id` 唯一；系统为 Ubuntu 24.04 LTS；Java 主版本为21；`thesis` 用户的 `sudo -n` 可用；五机互通；端口30303、8545、8546未占用；未发现 Besu 进程、Besu 服务或会被覆盖的 Besu 路径。

本次成功预检的原始证据保存在：

- `evidence/preflight/<hostname>.json`
- `evidence/preflight/<hostname>.txt`
- `evidence/preflight/summary.json`

阶段0验收命令为 `scripts/powershell/00-preflight.ps1`；其汇总记录的本地 Git 提交为 `015973261556b614c47adc17a57b266ed6933920`，工作区状态为 dirty（本阶段新增脚本与证据尚未提交）。阶段0已达到阶段1准入条件；阶段1尚未开始。
