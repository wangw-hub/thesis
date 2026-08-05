# 用户 KeyStore 最终决策

状态：`OPTION_A_APPROVED`。

用户于2026-07-30明确批准选项A。本文件记录该决定；它不授权I1。

## 选项 A：软件 KeyStore 原型边界（推荐）

- 用户 HPKE 私钥仅客户端持有；
- CK 以 AES-256-GCM 加密记录持久化；
- ROOT_KEK 位于仓库和数据库之外；
- Ubuntu 优先 systemd Credential，I0 不支持时使用严格权限的仓库外文件；
- CAP2、Header、链交易密钥独立；
- 不声称 HSM、不可提取或防 root。

推荐等级：`RECOMMENDED_FOR_THESIS_PROTOTYPE`。

## 选项 B：本期引入 Vault

- 增加 Vault 服务、认证、审计、备份和故障恢复；
- 需要扩展 I0–I7、实验变量和威胁模型；
- 工作量和单点故障面明显增加。

推荐等级：`FUTURE_ENGINEERING_OPTION`；仅在用户愿意扩大论文工程范围时选择。

## 选项 C：HSM 或云 KMS

- 潜在更强隔离，但当前设备、供应商、网络和可复现证据不足；
- 不适合当前五 VM 和论文周期。

推荐等级：`FUTURE_WORK`。

## 冻结结论

采用选项A。选项B与C不纳入本论文正式实现，保留为未来工程增强。V13只读对账已通过，本轮用户已单独批准执行I0；I1仍需新的明确批准。
