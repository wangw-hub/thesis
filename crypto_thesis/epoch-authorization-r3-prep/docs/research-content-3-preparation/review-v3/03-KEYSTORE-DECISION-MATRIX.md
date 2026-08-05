# KeyStore 决策矩阵

评分：3=适合，2=可用但有条件，1=弱，0=不适用。

| 指标 | KS-1 | KS-2 | KS-3 | KS-4 | KS-5 | KS-6 |
|---|---:|---:|---:|---:|---:|---:|
| 用户私钥隔离 | 3 | 3 | 3 | 2 | 2 | 3 |
| CK静态保护 | 3 | 3 | 2 | 3 | 3 | 3 |
| root攻击边界 | 0 | 1 | 1 | 2 | 2 | 3 |
| 自动化/systemd | 2 | 3 | 1 | 2 | 2 | 1 |
| Windows开发 | 2 | 0 | 3 | 2 | 2 | 1 |
| 五VM适配 | 3 | 3* | 1 | 2 | 0 | 0 |
| 轮换/备份/审计 | 2 | 2 | 1 | 3 | 3 | 3 |
| 可复现性 | 3 | 3 | 2 | 1 | 0 | 1 |
| 低复杂度/周期可完成 | 3 | 3 | 2 | 0 | 0 | 0 |
| 外部依赖少 | 3 | 3 | 3 | 0 | 0 | 1 |
| 推荐等级 | RECOMMENDED_FOR_THESIS_PROTOTYPE | CONDITIONALLY_RECOMMENDED | CONDITIONALLY_RECOMMENDED | FUTURE_ENGINEERING_OPTION | NOT_RECOMMENDED | FUTURE_ENGINEERING_OPTION |

`*` systemd 版本及 `LoadCredentialEncrypted` 支持状态为 `REQUIRES_I0_ENVIRONMENT_CHECK`，本轮不探测远程主机。

决定建议：以 KS-1 为可移植基线，Ubuntu 在 I0 支持时用 KS-2 注入，Windows 开发可用 KS-3 适配；三者遵守同一抽象契约。Vault、云 KMS 和 HSM 不进入当前实施范围。
