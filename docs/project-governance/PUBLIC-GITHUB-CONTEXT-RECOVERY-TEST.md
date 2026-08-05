# PUBLIC GITHUB CONTEXT RECOVERY TEST — 公开模式 30 问核验

> 模拟对象：全新 GPT，仅持 https://github.com/wangw-hub/thesis，无 D:\Research、无 raw、
> 无 .git-backups、无聊天历史。
> 允许先读取：README.md、CURRENT-SNAPSHOT.md、AUTHORITY-MAP.md、current-project-state.json、SUPERSEDED-DESIGNS.md。
> 结果：**30/30 PASS**（2026-08-05）。

| # | 问题 | 可恢复答案（来自公开文件） | 来源 |
|---|---|---|---|
| 1 | 论文题目？ | 面向非连续时间约束的区块链数据共享关键技术研究及实现（计算机技术专业硕士，电子科技大学） | README/CURRENT-SNAPSHOT §1 |
| 2 | 三项研究内容？ | RC1 非连续时间策略确定性编译；RC2 许可联盟链授权状态执行；RC3 版本化密文头部与前瞻性撤销闭环 | CURRENT-SNAPSHOT §2 |
| 3 | RC1 最终贡献？ | 确定性规范化编译：`I*` 唯一语义表示 + NTP1 + SHA-256 policyDigest | §3 |
| 4 | I* 是什么？ | 规范化半开区间有序列表，唯一语义主表示与 digest 输入 | §3 |
| 5 | C(P) 最终定位？ | 由 I* 确定性派生的 dyadic cover 执行 IR（可选/对照/ablation），非主表示 | §3/§7 |
| 6 | RC1 负结果？ | C(P) 对区间列表 0/108 更小、72/108 更大；无普遍 O(log U)；中位查询 interval≈561ns vs dyadic≈1984.7ns | §3/§7 |
| 7 | RC2 为什么使用许可联盟链？ | 锚定授权状态以获得可验证、防重放、Fail-Closed 的授权执行；非可信时钟/机密性来源 | §4 动机注 |
| 8 | CAP2 主要绑定什么？ | chainId、contractAddress、policyDigest、epoch、stateVersion、userVersion、userKeyId、operation、validity interval、Nonce | §4 |
| 9 | shared Nonce 的目的？ | PostgreSQL 原子共享 Nonce，防跨实例重放（50/100/500 并发仅一次成功） | §4 |
| 10 | RC2 V13 正式实验规模？ | 108 因子/324 种子/9,720 blocks/77,760 请求/233,280 链读 | §4 |
| 11 | RC2 最大性能发现？ | 逐请求链读主导端到端时延（98.66%–98.80%） | §4/§7 |
| 12 | cache/C(P) 是否有稳定优势？ | 否（负结果：无稳定端到端收益；C(P) REFUTED_AS_ADVANTAGE） | §4/§7 |
| 13 | RC3 核心问题？ | 授权状态变化后保证链下密文对象安全释放，仅承诺前瞻性撤销 | §5 |
| 14 | HEADER_ONLY/BODY_ROTATION 区别？ | HEADER_ONLY 仅更新密文头部（密钥/状态版本），数据体不变；BODY_ROTATION 重封装数据体密文 | §5 |
| 15 | forward-looking revocation 是什么？ | 约束新状态下的访问/释放窗口；不追溯已获材料 | §5/§8 |
| 16 | 已获得 CK 可否追回？ | 不能（禁止追溯撤销/追回已释放 CK/明文） | §8 |
| 17 | I11 measured runs 数量？ | 145（35 warmup 不计入统计） | §5/§6 |
| 18 | wrong material release 结果？ | 0（145/145 有效；120 VALID_SUCCESS + 25 VALID_EXPECTED_FAIL_CLOSED） | §5 |
| 19 | Kubo 主要价值？ | 提供可验证恢复来源（CORRUPT_RESTORE 下 KUBO_REPLICA 可 CONSISTENT 恢复）；时长无清晰效应 | §5/§7 |
| 20 | C-07 是什么？ | 禁止 QBFT 共识吞吐/延迟/多验证节点可扩展性结论 | §5/§8 |
| 21 | Pilot 与 Formal 区别？ | Pilot 仅开发验证（I9 93/93、RC2 pilot），不构成正式结论；Formal 有预注册/完整性/统计边界 | §6 |
| 22 | 哪个 RC2 实验 invalidated？ | 首轮 `formal_auth_multihost_20260729_34af4ff`（103,680 记录，协议偏差） | §4/§6 |
| 23 | Integrated thesis 状态？ | I14 集成母本冻结 + I15 文献完成 + I16/I17 格式候选；NOT SUBMISSION_READY | §9 |
| 24 | Midterm 状态？ | FINAL-CLEAN 最终固化（37 页），READY_FOR_ADVISOR_REVIEW | §10 |
| 25 | Small paper 状态？ | P0_APPROVED_NOT_YET_EXECUTED（创新性检索/选题/投稿蓝图，尚未执行） | §11 |
| 26 | 唯一 CURRENT NEXT ACTION？ | 小论文 P0：创新性检索、选题切割与投稿蓝图冻结 | §12 |
| 27 | 哪些 raw 是 LOCAL_ONLY？ | RC1 E1 raw、RC2 V13 raw、RC3 I11 raw（及 pilots、图 4-2..4-5、RC3 图） | §6/AUTHORITY-MAP/EXPERIMENT-DATA-MANIFEST |
| 28 | GitHub 能否独立重算所有实验？ | 不能（PUBLIC UNDERSTANDING ≠ FULL RAW REPRODUCTION） | LOCAL-VS-PUBLIC-ASSETS |
| 29 | 历史 ABE/threshold 方案是否 current？ | 否（SUPERSEDED：S-01/S-02 等，禁止恢复） | SUPERSEDED-DESIGNS |
| 30 | 新 GPT 接下来应读哪个文件？ | 按任务读 AUTHORITY-MAP 的 Public GitHub Authority 列（默认：current-project-state.json 或对应 RC 权威材料） | AI-CONTEXT-RECOVERY |

## PUBLIC_PATH_CHECK 结果

- 既有公开权威路径：28/28 tracked 且 HTTP 200（GitHub raw HEAD 实测，2026-08-05）。
- 公开图片：22/22 HTTP 200。
- 本轮新增 4 个治理文件：提交后 tracked，HTTP 待推送后验证（PENDING_PUSH）。
- BROKEN_PUBLIC_PATH = 0；无伪报 HTTP PASS。

## 结论

**PUBLIC_GITHUB_CONTEXT_RECOVERY_TEST = PASS（30/30）**
