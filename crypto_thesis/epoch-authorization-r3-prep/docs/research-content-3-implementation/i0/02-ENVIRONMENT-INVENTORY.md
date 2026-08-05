# I0环境清单

## Windows工作机只读实测

| 项目 | 结果 | 状态 |
|---|---|---|
| Windows | Registry ProductName=`Windows 10 Home China`，DisplayVersion=`25H2`，build=`26200`；OSVersion=`10.0.26200.0` | INSTALLED；保留原始标识，不推断产品营销名 |
| PowerShell | `5.1.26100.8875` | INSTALLED |
| Git | `2.53.0.windows.1` | INSTALLED |
| Python | `3.13.11`，`D:\Dev_Tools\Miniconda3\python.exe` | INSTALLED |
| Java | `17.0.12` | INSTALLED_LOCAL_ONLY |
| cryptography | `46.0.3` | INSTALLED_BUT_NO_NATIVE_HPKE |
| Web3.py | `7.16.0` | INSTALLED |
| jsonschema | `4.26.0` | INSTALLED |
| pytest | `8.4.2` | INSTALLED |
| PostgreSQL client | 未发现 | CANDIDATE_NOT_INSTALLED |
| solc/Besu/Kubo | 未发现 | CANDIDATE_NOT_INSTALLED |
| rfc8785/psycopg | 未发现 | CANDIDATE_NOT_INSTALLED |

## 五VM冻结证据

既有验收报告记录五机为Ubuntu 24.04 LTS、Java 21；V13冻结记录Besu 26.5.0、PostgreSQL 16.14。I0尝试以只读SSH查询五机systemd，连接成功到认证阶段但因无可用凭据全部拒绝；没有执行远程命令或触碰服务。

| 项目 | 状态 |
|---|---|
| Ubuntu 24.04 LTS | FROZEN_EVIDENCE |
| Java 21 | FROZEN_EVIDENCE |
| Besu 26.5.0 | FROZEN_INTERFACE |
| PostgreSQL 16.14 | FROZEN_INTERFACE |
| systemd精确版本/LoadCredentialEncrypted | NOT_VERIFIED_REMOTE_AUTH_UNAVAILABLE；I1前硬门 |

正式注入优先级因此冻结为：systemd能力核验通过则使用Credential；否则使用专用服务账户严格权限的仓库外文件。不得退回环境变量或命令行。
