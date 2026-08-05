# I4 准入审计

审计日期：2026-07-30  
结论：`I4_BLOCKED_ON_ISOLATED_POSTGRESQL_ENVIRONMENT`

## 已通过项目

- 用户授权范围为 `APPROVE_I4_ONLY=true`，未授权 I5。
- I3 状态为 `I3_COMPLETED_AWAITING_I4_APPROVAL`。
- I3 文档证据 SHA-256 校验错误数为 0。
- I1、I2、I3 独立回归分别为 49/49、49/49、48/48。
- RC2 接口 manifest 可定位，SHA-256 为
  `15e958a87e4e6b77711556f2554100d4b614763170890f96c8d6311ea8349898`。
- 当前分支为 `research-content-3-preparation`，准入前 HEAD 为
  `a5f3394468127a6d518fe9f15e4a58e30f6d45a1`。
- 主仓库 HEAD 仍为 `dac223468f550224257986a169304ed2c3dcf5af`，本任务未修改主仓库。
- I4 设计不要求修改 CAP2、AuthorizationState 或研究内容二数据库表。
- 本任务未访问正式链、正式数据库或 IPFS。

## 阻塞证据

对当前 Windows 主机进行低负载、只读本机核验：

| 核验项 | 结果 |
|---|---|
| Windows PostgreSQL 服务 | 0 |
| `postgres` 进程 | 0 |
| 5432/5433/5434 本机监听 | 0 |
| `psql` 命令 | NOT_FOUND |
| `pg_isready` 命令 | NOT_FOUND |
| `C:\Program Files\PostgreSQL` | NOT_FOUND |
| 可用 WSL 发行版 | 无 |

因此无法使用真正 PostgreSQL 验证 `FOR UPDATE SKIP LOCKED`、部分唯一索引、
事务回滚、CAS 和并发领取。SQLite 不具备等价语义，不能替代。用户同时禁止
自动启动 Docker、系统级安装 PostgreSQL，以及连接研究内容二或五台虚拟机。

## 执行边界

本轮没有：

- 创建 `.venv-r3-i4` 或安装数据库客户端；
- 创建数据库、用户、Schema、表或迁移；
- 编写可被误报为已验证的 PostgreSQL 实现；
- 使用 SQLite、模拟数据库或正式数据库绕过准入；
- 执行 I4 并发、CAS、租约、游标或故障恢复测试；
- 进入 I5。

## 可恢复路径

用户可在后续单独选择并批准一种环境准备方式：

1. 提供已经启动、仅监听 loopback 的独立 PostgreSQL 16.x 实例，以及通过仓库外秘密注入的独立测试凭据；
2. 单独批准在本机安装 PostgreSQL 16.x，并明确系统级变更边界；
3. 单独扩大范围，批准使用隔离 Docker PostgreSQL；当前指令明确禁止自动启动 Docker。

任何方案均不得复用研究内容二数据库、用户或密码。环境就绪后应重新执行完整
I4 准入审计，而不是从本次阻塞状态推定通过。

