# I2 可复现性报告

环境：Windows 11 10.0.26200、Python 3.13.11，沿用 `requirements-r3-i1-v2.lock`，未新增第三方依赖。

命令：`.venv-r3-hpke-pyhpke/Scripts/python.exe -m pytest tests/r3/i2 -q --confcutdir=tests/r3/i2`。

结果：49 项全部通过。测试仅使用 pytest 临时目录和人工非敏感数据，不访问网络、Besu、PostgreSQL 或 IPFS；并发只验证正确性，未记录吞吐、延迟或性能比较。
