# 密钥所有权与信任边界

## 信任域

1. **用户客户端域**：唯一持有 K-01；服务端无恢复后门。多设备应为每设备独立公钥/recipientKeyId，或由用户在客户端安全迁移私钥；V1 不把同一私钥静默复制到多设备。
2. **R3 内容保护域**：短暂持有明文 CK 和 ROOT_KEK；数据库只收到 CK 密文记录。服务启动失败、解包失败或版本未知均 fail-closed。
3. **签名域**：CAP2 与 Header 私钥逻辑和物理标识分离；调用者提交固定域摘要，不允许通用“签任意 bytes”接口。
4. **链交易域**：每个链角色独立账户，本地签名；不共享 ROOT_KEK、签名密钥文件或连接凭据目录。
5. **基础设施域**：Besu 节点身份和连接秘密不属于 R3 密钥层次。

## 服务可见性

| 组件 | 可见秘密 | 明确不可见 |
|---|---|---|
| 用户客户端 | 自身 K-01、解封装后的 CK | ROOT_KEK、其他用户私钥、服务交易密钥 |
| Issuer | CAP2 签名能力；用户公钥 | K-01、ROOT_KEK、交易私钥 |
| RevocationAgent/HeaderBuilder | 受控 CK 使用能力、Header 签名能力 | K-01、CAP2 私钥原始字节、ROOT_KEK 原始导出接口 |
| ContentKeyRepository | EncryptedCKRecordV1 | CK、ROOT_KEK |
| Transaction submitter | 对应角色签名能力 | CK、用户私钥、签名私钥 |

软件 KeyStore 只抵抗仓库泄露、普通非特权用户和数据库单独泄露；不能抵抗 root、调试器/进程内存读取或完全主机失陷，分类为 `ACCEPTED_LIMITATION`。
