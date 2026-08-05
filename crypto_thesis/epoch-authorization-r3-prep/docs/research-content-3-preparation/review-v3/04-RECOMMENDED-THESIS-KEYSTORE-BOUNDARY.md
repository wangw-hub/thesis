# 推荐的论文 KeyStore 边界

推荐 `SOFTWARE_KEYSTORE_PROTOTYPE_BOUNDARY_V1`：

- 用户 HPKE 私钥仅在客户端；
- 用户公钥及版本可公开登记；
- CK 以 AES-256-GCM EncryptedCKRecordV1 保存；
- ROOT_KEK 位于仓库和数据库之外；
- Ubuntu 首选 systemd Credential，条件不满足时使用专用服务账户可读的严格权限文件；
- Windows 仅开发适配，可使用用户范围 DPAPI；
- CAP2、Header、链交易密钥分离；
- 连接秘密与密码密钥分离；
- 不生成通用秘密导出/日志接口；
- 所有未知版本、认证失败和密钥缺失 fail-closed。

论文允许表述：“受操作系统访问控制保护的软件密钥托管原型，可阻止仓库或数据库单独泄露直接得到 CK。”

禁止表述：“硬件级安全”“不可提取”“能抵抗 root”“绝对安全”“生产级企业 KMS”。

用户已批准该边界，状态为 `OPTION_A_APPROVED`。该批准允许按I0清单冻结实施基线，但不授权I1、正式密钥生成或密码原型执行。
