# 依赖候选

| 依赖 | 版本 | 状态 | 用途/决定 |
|---|---:|---|---|
| Python | 3.13.11 | INSTALLED | I1本地解释器候选 |
| cryptography | 46.0.3 | INSTALLED/REJECTED_FOR_HPKE | 可提供现有AEAD/Ed25519，但无49.0新增原生HPKE |
| cryptography | 49.0.0 | CANDIDATE_NOT_INSTALLED | 首选RFC 9180 HPKE及AEAD/Ed25519统一后端 |
| rfc8785 | 0.1.4 | CANDIDATE_NOT_INSTALLED | JCS首选候选 |
| Web3.py | 7.16.0 | INSTALLED | 后续隔离链适配 |
| jsonschema | 4.26.0 | INSTALLED | Header/记录Schema |
| psycopg | 3.3.4 | CANDIDATE_NOT_INSTALLED | 后续r3_control访问 |
| pytest | 8.4.2 | INSTALLED | 现有测试运行器；I1是否升级另审 |
| solc | 0.8.30 | FROZEN_RC2/CANDIDATE_NOT_INSTALLED_LOCAL | I5前重新核验；I0不编译 |
| Besu | 26.5.0 | FROZEN_REMOTE/NOT_INSTALLED_LOCAL | 沿用RC2兼容边界 |
| PostgreSQL | 16.14 | FROZEN_REMOTE/CLIENT_NOT_INSTALLED_LOCAL | r3_control目标 |
| Kubo | 未选择 | CANDIDATE_NOT_INSTALLED | 推迟I8 |

所有候选只记录，不安装。I1必须在隔离环境以hash锁定实际wheel；本文件不是可安装锁文件。
