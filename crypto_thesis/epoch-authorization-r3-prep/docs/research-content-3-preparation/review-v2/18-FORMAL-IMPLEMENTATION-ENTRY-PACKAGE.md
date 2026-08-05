# 研究内容三正式实现准入审批包

## 1. 审批结论

- 当前状态：`PREPARATION_COMPLETE_AWAITING_ENTRY_DECISION`
- 是否已经进入正式实现：否
- 建议：在完成用户密钥托管选择、HPKE/分块格式最小原型以及研究内容二 V13 只读对账后，允许由用户单独批准 I0；本文件不构成自动批准。
- 研究内容二 V13：视为仍在运行，本轮未读取其结果、原始数据或进程状态。

## 2. 问题收敛摘要

| 集合 | 总数 | 分类摘要 |
|---|---:|---|
| 原 7 个 MAJOR | 7 | CLOSED_BY_DESIGN_EVIDENCE 4；REQUIRES_MINIMAL_PROTOTYPE 1；REQUIRES_FORMAL_IMPLEMENTATION 1；ACCEPTED_LIMITATION 1 |
| 原 14 个开放决策 | 14 | CLOSED_BY_DESIGN_EVIDENCE 8；BLOCKED_ON_RC2_V13 1；USER_DECISION_REQUIRED 1；REQUIRES_MINIMAL_PROTOTYPE 3；REJECTED_OPTION 1 |
| V2 严格审稿问题 | 14 | FATAL 0；MAJOR 4；MINOR 6；EDITORIAL 4 |

剩余 MAJOR 均有明确阶段门：HPKE/Body 测试向量、接收者规模阈值在 I1 验证；恢复闭环在 I7 验证；KeyStore 由用户在 I0 前决定。它们不应被伪装为已经实现或验证。

## 3. 冻结建议

1. **链上状态**：不修改 `AuthorizationState`，不部署迁移型 `AuthorizationStateV2`；新增职责单一的 `HeaderRegistry`，在同一提交交易中读取并核验旧授权状态。
2. **CAP2**：不增加字段，不改变签名、nonce、epoch、stateVersion、userVersion、policyDigest 或 chain binding 语义。
3. **Body**：新 bodyVersion 使用新随机 256-bit CK；分块 AES-256-GCM；96-bit nonce 为 64-bit 随机 nonceBase 与 32-bit chunkIndex 的无歧义组合；完整性失败立即拒绝。
4. **HPKE**：RFC 9180 Base mode，X25519/HKDF-SHA256/AES-128-GCM；每个接收者直接封装 CK；发行者以 Ed25519 对完整 Header 摘要签名。实现库和测试向量须经 I1 准入。
5. **密钥层次**：V1 不引入 KEK_e；用户私钥托管方案尚需用户选择。
6. **Header**：JCS 规范化 JSON；所有安全相关无符号字段进入 `headerDigest`；签名字段本身不进入被签摘要；二进制使用无填充 base64url。
7. **提交协议**：授权状态先变化，候选对象链下写入并回读校验，再通过 `HeaderRegistry` 一次提交为 COMMITTED；不设置可接受的 PENDING 窗口。
8. **撤销**：授权立即 fail-closed，Header 按资源异步重建；合法用户在新 Header COMMITTED 前可能短暂不可用，不回退旧 Header。
9. **幂等**：以固定二进制编码的域、chainId、两个合约地址、事件签名、txHash、logIndex、resourceId、epoch、stateVersion、keyVersion 计算 SHA-256；blockHash 独立保存用于重组证据。
10. **存储顺序**：LocalObjectStore → 故障恢复验证 → IPFS/Kubo；IPFS 不是密码完整性的唯一依据。

## 4. 主要贡献定位

研究内容三的贡献不是发明新密码原语，而是面向非连续时间约束，把冻结授权状态、版本化加密 Header、前瞻性撤销、可恢复提交状态机和可证伪实验组织为一套 fail-closed 协议。可成立的主张限于：

- 撤销后的未来材料释放与新版本访问被链状态和 Header 锚点共同约束；
- 单资源 Header 更新与 Body 字节数解耦，但总成本仍随受影响资源数和接收者数增长；
- 崩溃、重复事件和部分失败可由幂等任务与对账恢复；
- 不主张撤回已泄露明文、已取得 CK 或旧密文。

## 5. 最大风险

- 最大工程风险：链上事件、链下对象、数据库任务三者跨边界恢复不闭合。
- 最大论文风险：把成熟密码组件组合描述为原语创新，或把前瞻性撤销夸大为追溯撤销。
- 最大依赖风险：V13 后研究内容二接口发生协议性变化；此时必须执行差异审计，不能直接准入。

## 6. 准入前置条件

- [ ] 用户选择生产私钥托管边界。
- [ ] V13 最终审稿后按 `20-RC2-V13-RECONCILIATION-PLAN.md` 完成只读对账。
- [ ] I0 固定实现依赖、版本和威胁边界。
- [ ] I1 用 RFC 9180/NIST 测试向量完成最小原型，不做性能实验。
- [ ] 用户明确批准进入正式实现。

当前只满足“准入候选”的文档条件，不满足“已经正式进入研究内容三”的授权条件。
