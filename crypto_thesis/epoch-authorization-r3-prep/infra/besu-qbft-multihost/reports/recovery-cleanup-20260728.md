# 旧 Besu 资产受控清理报告

## 授权与范围

用户明确授权清理旧 Besu 安装后重新部署。本次仅清理四台 Validator 上已由只读核验确认的旧 Besu 资产；`experiment-client` 未发现目标资产，未作修改。

## 实际远程变更

在 `besu-validator-1` 至 `besu-validator-4` 上，恢复脚本仅删除了以下精确路径（存在时）：

```text
/opt/besu
/opt/besu-26.5.0
/etc/besu
/var/lib/besu
/var/log/besu
```

脚本先拒绝在存在 Besu 进程或 `besu*` systemd 单元时执行；本次未发现二者。若存在 `besu` 系统用户，脚本会在路径删除后删除该用户；本次每台均报告用户不存在。没有修改网络、Java、SSH、主机名、IP、`thesis` 用户、Genesis、密钥或防火墙。

## 执行结果与证据

四台目标主机均返回退出码 `0`：

| 主机 | 清理证据 SHA-256 |
|---|---|
| besu-validator-1 | `275F4B356927499ADE09DB99B617767691101F224296AE0AAADB0D36E3345727` |
| besu-validator-2 | `7E46E5AABEF6B420923A78D89AFBEEB7CAC25895D1544859CDD99D73F08D7912` |
| besu-validator-3 | `3401A41A8831CFAA1C84EDDFA604F1DA11542D236051B7DF18118C39BEE08707` |
| besu-validator-4 | `27C14EDAABB0D606DC790A1B665F8A35A413F30AF2C9C64F718FAC7B360714CA` |

原始记录位于 `evidence/recovery/`，汇总见 `evidence/recovery/summary.json`。

## 回滚与限制

旧 Besu 分发文件和可能存在的旧链数据已经删除，不能从本次恢复动作中还原。后续阶段1将使用同一份 Besu 26.5.0 官方安装包重新建立基础软件目录。

