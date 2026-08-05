# 密钥材料清单

| ID | 材料 | 所有者/持有者 | 秘密 | 用途 | 持久化与恢复 | 当前状态 |
|---|---|---|---|---|---|---|
| K-01 | 用户 X25519 HPKE 长期私钥 | 数据用户/用户客户端 | 是 | 解封装自身 AccessEnvelope | 仅客户端受保护存储；可选用户控制备份 | READY_FOR_USER_DECISION |
| K-02 | 用户 HPKE 公钥 | 用户；服务保存副本 | 否 | 生成 Envelope | 公开登记，绑定 userKeyId、userVersion、身份、状态和登记证明 | READY_FOR_I0 |
| K-03 | 每 Body 版本 CK | 资源所有者产生；KeyProtectionService 短暂使用 | 是 | AES-256-GCM Body 加解密、重建 Header | 仅以 EncryptedCKRecordV1 持久化；不得明文入库 | READY_FOR_I1_AFTER_I0 |
| K-04 | ROOT_KEK / CK_PROTECTION_KEY | R3 服务运维安全域 | 是 | 包装 K-03 | 数据库和仓库外；独立备份；版本化 | READY_FOR_USER_DECISION |
| K-05a | CAP2 Ed25519 私钥 | R2 Issuer | 是 | CAP2 签名 | 冻结 R2 托管，不由 R3 读取或重设计 | BLOCKED_ON_V13_RECONCILIATION |
| K-05b | Header Ed25519 私钥 | R3 Header Issuer | 是 | Header 摘要域签名 | 独立于 CAP2；仓库外加载和独立轮换 | READY_FOR_USER_DECISION |
| K-06 | ADMIN/OWNER/AUTHORIZER/REVOCATION/HEADER_COMMITTER 交易私钥 | 对应链角色 | 是 | 本地签名交易 | 分角色、仓库外、无 RPC 长期解锁；不由 ROOT_KEK 统一包装 | READY_FOR_I0 |
| K-07 | Besu 节点私钥 | 基础设施运维方 | 是 | 节点身份 | 不读取、不复制、不修改 | OUT_OF_SCOPE_FROZEN_INFRASTRUCTURE_SECRET |
| K-08 | PostgreSQL/RPC/存储网关连接秘密 | 服务运维方 | 是 | 服务认证 | 与密码密钥分离的凭据注入 | READY_FOR_I0 |

K-02 不是秘密。K-04 是本地静态保护密钥，不是公开 Header 密钥层次中的 `KEK_e`。K-03 必须持久化，是因为撤销后的 Header 重建需要为仍获授权用户重新封装同一个 Body CK；从用户 Envelope 恢复会要求服务取得用户私钥，违反信任边界。
