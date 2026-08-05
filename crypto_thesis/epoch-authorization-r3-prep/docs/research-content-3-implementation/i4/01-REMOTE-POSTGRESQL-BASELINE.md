# experiment-client PostgreSQL 创建前基线

采集日期：2026-07-30  
采集方式：仅通过 `thesis@192.168.6.133` 执行只读元数据命令。

## 主机身份

- hostname：`experiment-client`
- SSH用户：`thesis`
- sudo：非交互可用
- OS内核：Ubuntu Linux 6.8.0-136-generic

## PostgreSQL程序

- PostgreSQL：16.14（Ubuntu 16.14-0ubuntu0.24.04.1）
- `psql`：`/usr/bin/psql`
- `pg_isready`：`/usr/bin/pg_isready`
- `pg_createcluster`：`/usr/bin/pg_createcluster`
- `pg_lsclusters`：`/usr/bin/pg_lsclusters`
- server binary：`/usr/lib/postgresql/16/bin/postgres`

## 冻结正式集群

| 字段 | 值 |
|---|---|
| 版本/集群 | `16/main` |
| 端口 | `5432` |
| 状态 | `online` / systemd `active(running)` |
| MainPID | `52520` |
| 服务启动时间 | `Wed 2026-07-29 13:03:28 CST` |
| 数据目录 | `/var/lib/postgresql/16/main` |
| 配置目录 | `/etc/postgresql/16/main` |
| 日志 | `/var/log/postgresql/postgresql-16-main.log` |
| 服务 | `postgresql@16-main.service` |

正式集群创建前配置SHA-256：

- `postgresql.conf`：`d9899ba7b45305aee2dba18cedb26eee34c4f496fa5a27b0e7724f401864b035`
- `pg_hba.conf`：`e743a9e5ce869a9858285dda1a06f2c5a50384559f21100e73636ce99aea1c2f`
- `pg_ident.conf`：`b4dfef08731a7d20a3bb724ad4cf3e1cd91ec01fbe51349c6a3acc5704072965`

数据库名称仅记录为：`epoch_auth`、`postgres`、`template0`、`template1`。
角色名称仅记录为：`epoch_auth`、`postgres`。未查询任何业务表、Nonce、
授权记录、密码或pgpass。

