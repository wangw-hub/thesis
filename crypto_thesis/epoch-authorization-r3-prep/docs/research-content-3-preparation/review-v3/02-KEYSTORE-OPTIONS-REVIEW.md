# KeyStore 方案审查

| 方案 | 结论 | 适用性与限制 |
|---|---|---|
| KS-0 明文文件 | PROHIBITED | 权限位不等于静态密码保护；不得保存明文 CK、用户私钥或服务私钥 |
| KS-1 OS 权限软件 KeyStore | RECOMMENDED_FOR_THESIS_PROTOTYPE | 仓库外、专用账户、最小文件权限；可复现且工作量可控；不抗 root |
| KS-2 systemd Credentials | CONDITIONALLY_RECOMMENDED | Ubuntu 服务首选注入候选；`LoadCredentialEncrypted`、运行时目录和具体 systemd 版本须 I0 本机核验 |
| KS-3 OS 凭据管理器 | CONDITIONALLY_RECOMMENDED | Windows DPAPI 适合开发机；用户/机器绑定和无桌面 Linux 自动化差异使其不作为五 VM 统一方案 |
| KS-4 Vault | FUTURE_ENGINEERING_OPTION | 审计、动态认证和集中轮换更强，但引入服务、认证、HA、备份和新故障面，超出当前论文贡献 |
| KS-5 云 KMS | NOT_RECOMMENDED | 网络/成本/供应商依赖削弱本地五 VM 可复现性 |
| KS-6 HSM/PKCS#11 | FUTURE_ENGINEERING_OPTION | 当前无设备、驱动与复现实证；不得声称已经具备硬件不可提取保护 |

KS-1 与 KS-2 可组合：安全属性的核心是仓库外、数据库外、专用身份和最小暴露；KS-2 是 Ubuntu 注入机制，不是新的密码根。若 I0 发现 systemd 版本不支持加密凭据，则退回严格权限文件，不退回环境变量或命令行。

依据：[systemd.exec Credentials](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html#Credentials)、[systemd-creds](https://www.freedesktop.org/software/systemd/man/latest/systemd-creds.html)、[Microsoft DPAPI](https://learn.microsoft.com/en-us/windows/win32/api/dpapi/nf-dpapi-cryptprotectdata)、[NIST SP 800-57 Part 1 Rev.5](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final)。
