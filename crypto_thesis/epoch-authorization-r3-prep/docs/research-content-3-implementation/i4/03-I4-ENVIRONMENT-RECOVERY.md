# I4 环境恢复记录

日期：2026-07-30  
结果：`BLOCKED_ON_SSH_AUTHENTICATION`

## 授权目标

- 唯一允许目标：`thesis@192.168.6.133`
- 预期 hostname：`experiment-client`
- 请求模式：`BatchMode=yes`
- 连接超时：10秒

## 只读身份核验结果

执行了用户指定的第一道只读命令：

```text
ssh -o BatchMode=yes -o ConnectTimeout=10 thesis@192.168.6.133 "hostname && id && uname -a"
```

SSH 在远程命令执行前拒绝认证：

```text
Permission denied (publickey,password).
```

因此：

- 未取得远程 shell；
- 未读取远程 hostname、用户、操作系统或 PostgreSQL 元数据；
- 未执行 `sudo`；
- 未访问现有 PostgreSQL 集群或数据库；
- 未创建 `16/r3_i4`；
- 未生成数据库密码；
- 未创建 SSH 隧道；
- 未执行 I4。

## 硬停止依据

当前连接需要未配置的公钥或交互密码。任务明确规定，若需要交互密码且无法安全
处理，应停止并输出用户手工完成的命令。密码不得写入提示词、日志、命令参数或
Git，因此本任务没有改用 `sshpass`、管道、环境变量或明文文件绕过认证。

## 用户手工解除方式

用户应在本机交互终端中完成现有 SSH 密钥配置或代理加载，然后验证以下命令能够
无密码、非交互成功：

```powershell
ssh -o BatchMode=yes -o ConnectTimeout=10 thesis@192.168.6.133 "hostname && id && uname -a"
ssh -o BatchMode=yes thesis@192.168.6.133 "sudo -n true"
```

第一条必须返回 hostname `experiment-client`，第二条必须以退出码0完成且不得提示
密码。满足后可重新恢复本任务；届时仍需从正式 PostgreSQL 资产只读快照开始，
不得直接创建集群。

## 后续状态演变

用户完成独立OpenSSH密钥配置后，本任务重新执行两道命令并确认：

- hostname：`experiment-client`
- SSH用户：`thesis`
- sudo：`SUDO_OK`
- 状态事件：`SSH_AUTHENTICATION_BLOCKER_RESOLVED_BY_USER`

随后冻结正式集群基线，创建并审计`16/r3_i4`，通过SSH隧道完成I4。原失败事实
仍保留在本文件前半部分，没有删除或改写。

