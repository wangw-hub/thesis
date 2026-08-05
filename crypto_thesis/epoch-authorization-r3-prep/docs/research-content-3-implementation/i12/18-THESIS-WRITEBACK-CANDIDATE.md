# Thesis Writeback Candidate

以下为候选段落（正式学术中文），数字均带 source reference（`formal-analysis/*.json` 与 `docs/…/i12/formal-rq-results.json`）。

**实验环境**：本实验在独立 Formal 环境中进行：单节点 QBFT 链（chainId 2026080201）、独立 PostgreSQL 集群（16/formal_r3，127.0.0.1:55433）与零公网 peer 的隔离 Kubo；环境指纹 digest 见 `formal-fingerprint.json`。该环境仅用于应用层功能与受限工程测量，不评估多 Validator 共识性能。

**实验设计**：依据冻结预注册，29 个配置 × 5 次重复 = 145 个 measured RUN（另 35 个 warm-up，不计入统计）；实验单位 RUN；执行顺序由 seed 20260802 分块确定性随机化并在采集前冻结。

**RQ-1 结果**：E1 的 20 个 RUN 全部通过冻结不变量（状态一致性与幂等性检查通过，错误材料释放为 0）；该结论限于本实验配置范围（source: E1 20/20，`formal-rq-results.json`）。

**RQ-2 结果**：HEADER_ONLY 下，端到端时长中位数在各配置间差异小（recipient 2→32 中位数差约 27.0 ms，ratio 1.005；affected 1→4 差约 12.5 ms），链上交易等待占主导；仅为描述性观察（source: `formal-rq-results.json` RQ-2）。

**RQ-3 结果**：BODY_ROTATION 下，body 64KiB→8MiB（recipient=2）端到端时长中位数由约 5083 ms 升至约 6696 ms（差 1613.1 ms，ratio 1.317）；45/45 RUN 中旧 CK 无法解密新 Body、body digest 改变且版本关系正确（source: `formal-rq-results.json` RQ-3）。

**RQ-4 结果**：撤销事件后，pending 窗口内材料释放判定为 DENIED，header 闭合后恢复一致；10/10 RUN 错误材料释放为 0（source: `formal-rq-results.json` RQ-4）。

**RQ-5/RQ-6 结果**：40/40 RUN 恢复正确性成立；LOCAL_ONLY 与 KUBO_REPLICA 在匹配故障块内的端到端与恢复成本差异见 `effect-sizes.json`，多数单元格未观察到稳定差异，个别恢复路径成本不同（source: `formal-rq-results.json` RQ-5/RQ-6）。

**综合讨论与局限**：以上结果仅在冻结配置、5 次重复、受控单节点环境内成立；未评估多 Validator 共识性能（C-07 禁止）；实验验证不构成形式化证明。
