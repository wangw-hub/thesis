# 用户决策矩阵

## 必须决策

| ID | 决策 | 推荐项 | 备选项 | 决策截止点 | 不决策的结果 |
|---|---|---|---|---|---|
| UD-01 | 正式环境用户 HPKE 私钥托管 | 操作系统/组织既有密钥托管或 HSM/KMS 抽象，私钥不进入数据库和仓库 | 受口令保护的本地密钥库，仅限单机试验；硬件钱包/外部签名代理 | I0 退出前 | 不允许进入 I1 之后的集成实现 |
| UD-02 | 是否正式批准启动研究内容三 I0 | 在 V13 对账和 UD-01 完成后单独批准 | 要求修订设计 | 所有准入前置条件完成后 | 保持 `PREPARATION_COMPLETE_AWAITING_ENTRY_DECISION` |

## 不需要用户替代工程证据的项目

以下事项应由阶段证据关闭，不能通过“用户选择”跳过：

- HPKE 库、suite 和 RFC 9180 测试向量：I1 最小原型；
- envelope 列表规模、Header 字节阈值：I1/I3 小规模边界验证；
- 重组、UNKNOWN、孤儿对象和死信恢复：I7 正式实现与故障注入；
- PostgreSQL 锁、CAS 和事务边界：I4 测试；
- HeaderRegistry gas 与提交路径：I5 后的 PILOT_ONLY。

## 已由设计证据作出的选择

- 不修改 `AuthorizationState`，不迁移到 `AuthorizationStateV2`；
- 不修改 CAP2；
- V1 不引入 KEK_e；
- 选择独立 `HeaderRegistry`；
- 选择链下候选上传后一次 COMMITTED；
- 选择立即授权撤销与逐资源异步 Header 更新；
- 选择 LocalObjectStore 先于 IPFS。
