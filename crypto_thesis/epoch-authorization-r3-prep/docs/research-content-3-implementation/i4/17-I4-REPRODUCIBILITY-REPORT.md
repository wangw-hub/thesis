# I4可复现性报告

- PostgreSQL 16.14独立集群`16/r3_i4`
- Python 3.13.11；psycopg/psycopg-binary 3.3.4
- 测试数据库/角色：`epoch_auth_r3_i4_test`
- Windows本地65432经SSH转发至远程loopback 55432
- 外部passfile注入，不记录密码
- I4命令：`pytest tests/r3/i4 ... --basetemp C:\tmp\epoch-auth-r3-i4-pytest-final`
- I4：49/49；I1：49/49；I2：49/49；I3：48/48

没有收集TPS、时延、p95或worker性能比较。

