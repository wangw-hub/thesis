# SUPERSEDED DESIGNS — 历史废弃方案清单

> 目的：防止未来 AI 在检索旧文档时重新启用已废弃方案。
> 每项记录：旧设计 / 为什么废弃 / 替代方案 / 当前权威来源。
> 历史文档保留原样；本文件是外部标记，不修改冻结证据。

| # | 旧设计 | 为什么废弃 | 替代方案 | 当前权威来源 |
|---|---|---|---|---|
| S-01 | 自研 ABE 密码体制 | 无完整 Setup/KeyGen/Encrypt/TrapdoorGen/Decrypt 与归约证明，无法实现/验证 | 标准密码组件组合（HPKE RFC 9180、AES-256-GCM、JCS、Ed25519） | 开题审查报告；RC3 设计文档 |
| S-02 | 门限解封装旧路线 | 构造不成立，公开 EVM 不能安全保存主秘密或其可恢复碎片 | 版本化密文头部 + 前瞻性撤销（HeaderRegistry） | RC3 i0–i8 设计文档；SUPERSEDED 标记 |
| S-03 | 链上秘密陷门 | 哈希绑定 ≠ 抗合谋证明；EVM 公开状态不适合存主秘密 | 链上状态锚定 + 链下 HPKE 密钥封装 | 开题审查报告；RC2 CAP2 |
| S-04 | `C(P)` 作为核心压缩优势 | E1 正式结果：0/108 更小、72/108 更大；无普遍压缩优势 | `I*` 为主表示，`C(P)` 为派生执行 IR（ablation） | RC1 E1 正式报告；第四章 V1.2 |
| S-05 | 任意碎片化策略 `O(log U)` 压缩 | 层次覆盖不保证任意碎片集合 `O(log N)` | 只报告实测边界，不作普遍渐近声明 | RC1 E1 负结果 |
| S-06 | 追溯撤销（retroactive revocation） | 已获得明文/旧数据密钥的用户无法被追溯撤销 | 前瞻性撤销（forward-looking）：约束新状态访问 | RC3 L-05；CURRENT-SNAPSHOT §8 |
| S-07 | 联盟链作为绝对可信时间源 | 联盟链不提供绝对可信时钟语义 | 将链状态作为授权状态锚点（非时钟） | 项目宪法 Non-Goals |
| S-08 | 缓存稳定性能优势 | V13 paired 分析：无稳定端到端收益（robust effect ~0.02） | 如实报告缓存仅影响命中率，不主张收益 | RC2 V13 independent-analysis-summary.json |
| S-09 | QBFT 共识性能主张 | C-07 FORBIDDEN：单节点/受控环境不产生共识性能结论 | 只报告应用层端到端与链读占比 | RC3 i12 claim 矩阵；C-07 |
| S-10 | 联盟链提供数据机密性/秘密执行环境 | 超出联盟链能力边界 | 机密性由链下 HPKE/AES-GCM 承担 | 项目宪法 Non-Goals |
| S-11 | 早期 `ResourceState` 命名 | 与当前实现命名不一致 | `AuthorizationState`（当前合约名） | RC2 contracts/AuthorizationState.sol |
| S-12 | 旧链 chainId 2026072801 作为正式性能来源 | 无资金/未部署正式合约，阶段 C 硬停止 | 独立正式授权链 chainId 2026072901 + V13 复跑 | RC2 总验收报告（HISTORICAL）；V13 manifest |
| S-13 | 首轮 103,680 记录运行作为正式性能证据 | 采集协议偏差（INVALIDATED_PROTOCOL_DEVIATION） | V13 有效复跑（77,760 请求） | RC2 claim/experiment registry |
| S-14 | 工程测试等价于密码学证明 | 不变量仅对所测配置成立 | 实验验证 + 明示局限（L-08） | RC3 i12 limitations |
