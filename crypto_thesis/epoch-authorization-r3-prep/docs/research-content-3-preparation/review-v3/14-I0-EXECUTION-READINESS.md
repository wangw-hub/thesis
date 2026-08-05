# I0 执行准备清单（尚未执行）

| 项目 | I0输出 | 当前状态 |
|---|---|---|
| Python版本 | `python --version`与解释器SHA/来源 | TO_VERIFY_DURING_I0 |
| cryptography/HPKE | 精确版本、wheel/hash、后端、许可证 | 候选49.0.0；TO_VERIFY_DURING_I0 |
| JCS库 | 版本、RFC 8785行为、许可证、hash | TO_VERIFY_DURING_I0 |
| Web3.py | 精确版本、依赖hash | TO_VERIFY_DURING_I0 |
| solc | 精确版本与二进制hash | TO_VERIFY_DURING_I0 |
| PostgreSQL | 正式目标版本和驱动 | R2记录16.14；须V13对账/I0确认 |
| Besu | 正式目标版本 | R2记录26.5.0；须V13对账/I0确认 |
| Kubo | I8候选版本，不在I0启动 | TO_VERIFY_DURING_I0 |
| systemd/OS | 五VM发行版、kernel、systemd Credentials能力 | TO_VERIFY_DURING_I0；本轮未探测 |
| 许可证 | 依赖许可证清单及论文分发影响 | TO_VERIFY_DURING_I0 |
| 依赖哈希 | lock/离线包/镜像摘要 | TO_VERIFY_DURING_I0 |
| KeyStore选择 | 用户A/B/C审批记录 | READY_FOR_USER_DECISION |
| 威胁边界 | review-v3 01/04/12冻结 | READY_FOR_I0 |
| 项目/秘密目录 | 只记录类别和权限模板，不记录秘密 | TO_VERIFY_DURING_I0 |
| 环境变量规则 | 只允许非秘密配置；秘密禁入env/CLI | READY_FOR_I0 |
| 日志脱敏 | denylist字段、异常映射、扫描规则 | READY_FOR_I0 |
| 测试向量 | RFC 9180 Appendix A.1、Ed25519、AEAD/Body黄金向量来源 | READY_FOR_I0 |

I0 PASS 必须同时满足：用户已选 KeyStore、V13 只读对账通过、依赖及许可证可冻结、秘密目录不在仓库、测试向量来源可追溯、无须修改 CAP2/AuthorizationState。当前仅“执行材料就绪”，未执行、未批准。
