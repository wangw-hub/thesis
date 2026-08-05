# 用户 HPKE 私钥边界

- K-01 由用户生成和拥有，只在用户客户端使用；Issuer、Verifier、RevocationAgent、HeaderBuilder 和数据库永不接触。
- K-02 登记必须绑定用户标识、recipientKeyId、公钥、userVersion、状态和登记证明；公钥轮换将 userVersion 单调增加，旧版本停止用于新 Header。
- 丢失：无法从服务端恢复；用户以新密钥重新登记，未来 Header 使用新版本。没有旧私钥且没有用户备份时，旧 Envelope 永久不可解封装。
- 泄露/主动共享：立即撤销旧 userVersion、登记新公钥并重建未来 Header；不能撤回攻击者已获得的 CK 或明文。
- 备份：由用户选择受口令保护的导出或 OS 凭据存储；备份仍属于用户信任域。服务不得托管“恢复副本”。
- 多设备：V1 推荐每设备独立密钥和 recipientKeyId；同一用户可有多个 ACTIVE 设备记录，规模成本由 E7 计入。
- 内存：实现应缩短明文私钥/CK 生命周期并覆盖可变缓冲区；Python 运行时无法保证所有不可变 bytes 副本可可靠清零，这是 `ACCEPTED_LIMITATION`。
