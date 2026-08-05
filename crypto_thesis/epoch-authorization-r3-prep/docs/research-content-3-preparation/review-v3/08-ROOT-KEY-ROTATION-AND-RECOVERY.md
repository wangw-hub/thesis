# ROOT_KEK 轮换与恢复

## 版本状态

- `ACTIVE_KEY_VERSION`：仅一个，包装新 CK。
- `DECRYPT_ONLY_KEY_VERSION`：可解包旧记录，不包装新记录。
- `RETIRED_KEY_VERSION`：所有记录迁移并过保留期后不可加载。
- `COMPROMISED_KEY_VERSION`：禁止新用；受影响记录必须紧急重包装或资源重加密。

## 轮换协议

1. 在独立安全域生成并备份新版本（I0/I1 不生成正式密钥）；
2. 安装为 ACTIVE，原 ACTIVE 原子降为 DECRYPT_ONLY；
3. 新 CK 只用新版本；
4. 后台按稳定主键批次读取旧记录，解包后以新 nonce 重包装；
5. `WHERE record_version=:expected AND protection_key_version=:old` CAS 更新；
6. 每批记录成功、失败和摘要审计；中断后从游标继续；
7. 全量扫描、抽样解包与备份验证完成后才 RETIRED；
8. 禁止缺失新密钥时回退为旧 ACTIVE。

## 后果

- ROOT_KEK 丢失且无独立备份：对应版本 CK 永久不可恢复，仍持有 CK 的用户可能读旧 Body，但服务无法重建 Header。
- ROOT_KEK 泄露：与该版本 CK 密文记录组合即可恢复所有对应 CK；立即标记 COMPROMISED、隔离服务、评估数据库暴露、轮换根密钥，并对高风险资源生成新 Body/CK。单独泄露 ROOT_KEK 而无记录仍是重大事件。
- 数据库和 ROOT_KEK 同时泄露：静态 CK 保护完全失效。
