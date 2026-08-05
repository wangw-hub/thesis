# 第六章 版本化密文头部与前瞻性撤销闭环机制

> 研究内容三正式写回稿（I13 冻结候选）。编号按论文既有章节序列推定（第四章=研究内容一、第五章=研究内容二），最终编号以论文定稿目录为准。全部实验数字来源于冻结的 I12 Formal Results Package 与正式实验运行索引；本稿不修改任何既有章节文件。

## 6.1 问题定义与设计目标

在基于许可联盟链的可信授权执行基础上，数据共享还面临两类问题：其一，授权状态的变化需要与数据本身的密文对象状态保持一致，当授权被撤销或升级时，接收方不应继续获得新数据的解密能力；其二，链上状态、数据库任务记录与链下不可变对象之间需要形成可验证的闭合关系，在组件故障时能够恢复而不破坏一致性。

本章针对上述问题，研究版本化密文头部（VersionedHeaderV1）与前瞻性撤销（forward-looking revocation）闭环机制。设计目标如下：

1. 以版本化状态关系描述密文对象的更新：Header、Body 与内容密钥（CK）分别携带独立版本，任何更新路径都可被链上状态与数据库记录验证；
2. 撤销事件发生后，系统立即停止后续材料释放，并在新 Header 闭合前保持 Fail-Closed 语义；
3. 链上授权状态、数据库任务状态与链下对象存储形成可核验的闭合，故障恢复按预注册规则执行；
4. 通过受控的正式实验，在冻结配置范围内验证正确性、安全行为与工程开销。

本章工作属于系统组合与状态协议设计，使用 AES-256-GCM、HPKE（RFC 9180）、Ed25519 与 SHA-256 等标准密码原语，不构成新的密码算法或新的基础表示。

## 6.2 总体架构

系统由以下部分组成：链上合约（AuthorizationState 与 HeaderRegistry）负责授权状态与 Header 提交记录的权威存储；数据库控制面以任务状态机管理链上写入，并以 operationId 保证幂等；链下对象层由不可变 LocalObjectStore 与隔离的 Kubo 副本组成，对象以 SHA-256 内容摘要为完整性权威；版本化密文头部将上述部分绑定为可验证的 CompositeState。

数据流为：资源注册与授权状态写入链上；Header 与 Body 密文对象写入链下对象存储并可复制到 Kubo；数据库在链写前记录任务、在链写后固化提交；撤销与恢复组件分别负责事件驱动的 Fail-Closed 判定与对象一致性恢复。

## 6.3 版本化密文对象设计

密文对象由 Header 与 Body 两部分构成。Header 的核心字段由 HeaderCore 承载（资源标识、Header/Body/Key 版本、Body 摘要等），签名后形成 SignedVersionedHeader，并携带接收者信封（RecipientEnvelope）；Body 为分块 AES-256-GCM 密文。CK 按接收者使用 HPKE（X25519 + HKDF-SHA256 + AES-128-GCM）封装为 EncryptedCKRecord，每个 Body 版本使用独立 CK，V1 冻结语义为 keyVersion 等于 bodyVersion。材料释放判定由 AccessMaterialReleaseGuard 依据链上复合状态与 Header 对象完整性执行。

Header 使用 JCS（RFC 8785）规范序列化并以 Ed25519 签名，其摘要与对象摘要均进入链上 HeaderRegistry 的提交记录，从而将链下对象与链上状态绑定。

## 6.4 Header 与 Body 更新机制

版本语义冻结如下：

- INITIAL：headerVersion=1，bodyVersion=1，keyVersion=1；
- HEADER_ONLY：headerVersion 加 1，bodyVersion 与 keyVersion 不变，Body 与 CK 不变；
- BODY_ROTATION：headerVersion、bodyVersion、keyVersion 均加 1，生成新 CK 与新 Body。

HEADER_ONLY 用于授权语义变化（如撤销后的 Header 闭合）而不更换数据密钥；BODY_ROTATION 用于更换密文对象与密钥。二者是不同语义的操作，实验中分别分析，不作等价比较。

## 6.5 前瞻性撤销与 Fail-Closed

撤销边界为前瞻性撤销：撤销事件发生后，系统立即停止后续材料释放；在新 Header 闭合前，合法用户可能暂时不可访问，这是 Fail-Closed 设计代价。系统不主张追溯撤销，不能收回此前已获得的明文、旧 CK 或旧密文。

撤销流程为：链上 advanceEpoch 触发 EpochAdvanced 事件；事件扫描与受影响资源解析生成 Header 更新意图；在 Header 闭合前，材料释放判定保持 DENIED；Header 进入 current 状态后，合法材料恢复释放。整个过程以固定区块的事件与释放判定作为证据。

## 6.6 链上/链下状态一致性与任务状态机

AuthorizationState 保存 policyDigest、epoch、stateVersion 与资源状态；HeaderRegistry 保存 headerVersion、bodyVersion、keyVersion、摘要与操作身份。数据库控制面以任务状态机管理链写：JOB_CREATE 显式提交后可被独立连接读取，经 ChainWriteAdmission 准入后广播交易，以回执与固定区块状态验证后 DATABASE_FINALIZE 为 COMMITTED。数据库事务不跨链回执等待；operationId 保证重复执行幂等，COMMIT_UNKNOWN 等不确定结果按预注册规则处理。

## 6.7 故障恢复机制

链下对象以 LocalObjectStore 不可变存储，写入原子，SHA-256 内容寻址；Kubo 仅作为隔离副本定位，CID 不替代 SHA-256 的完整性权威。恢复由 RecoveryCoordinator 协调：读取候选对象、SHA 验证、结构验证、原子恢复，最终形成一致状态或 Fail-Closed 结果。受控故障包括对象损坏、CID 不一致与本地/副本同时缺失。

## 6.8 安全性/正确性讨论

正确性建立在版本关系的可验证性与 Fail-Closed 释放判定之上：任何状态更新必须满足版本单调性与摘要一致性；撤销窗口内释放判定为拒绝；恢复路径不因来源不同而放宽完整性要求。这些性质通过实现与正式实验验证，属于实验验证而非形式化证明。

## 6.9 实验环境与实验设计

正式实验在独立于 Pilot 的 Formal 环境中进行，避免与实验验证阶段资产混用：独立 PostgreSQL 集群（127.0.0.1:55433，数据库 epoch_auth_r3_formal，schema r3_formal）、隔离的 Kubo 仓库（独立 IPFS_PATH，零公网 peer）与独立单节点 QBFT 链（chainId 2026080201，单 Validator）。运行环境为 Ubuntu（内核 6.8.0-136），2 vCPU，3.07 GB 内存，Besu 26.5.0，PostgreSQL 16.14，Kubo 0.42.0，Python 3.12.3，OpenJDK 21。该环境仅用于应用层功能与受限工程测量，不用于评估多 Validator 共识性能。

实验按冻结预注册执行：29 个配置、每配置 5 次重复、145 个 measured RUN（另有 35 个 warm-up，不计入统计）；实验单位为 RUN，phase、transaction、request 等不作为独立样本；执行顺序由 seed 20260802 分块确定性随机化并在采集前冻结；统计以 RUN 为单位报告 median/IQR，使用 10 000 次 Bootstrap 的 95% percentile CI，比较采用 median difference、ratio 与 Cliff's delta，需要时在 RQ family 内进行 Holm 校正。

## 6.10 正式实验结果

### 6.10.1 E1：状态一致性与幂等性（RQ-1）

E1 覆盖 INITIAL、BODY_ROTATION、REVOCATION 与 RESTORE 四种路径，共 20 个 RUN，全部通过冻结状态不变量：状态一致性与幂等性检查通过，链/数据库/对象最终状态一致，未观察到错误材料释放。端到端时延中位数分别为 INITIAL 3080 ms、BODY_ROTATION 5120 ms、REVOCATION 7118 ms、RESTORE 3147 ms。结论限于本实验覆盖的配置范围。

### 6.10.2 E2：HEADER_ONLY 工程开销（RQ-2）

E2 在 HEADER_ONLY 语义下覆盖接收者规模 2/8/32 与受影响资源数 1/4，共 30 个 RUN，全部有效。各配置端到端时延中位数约 5115～5144 ms；接收者由 2 增至 32 时，中位数差约 27.0 ms（ratio 1.005，Cliff's delta 0.12）；受影响资源由 1 增至 4 时，中位数差约 12.5 ms（ratio 1.002，Cliff's delta 0.20）。不同接收者规模下的时延分布如图 6-1 所示。

结果表明，在冻结实验范围内，接收者与受影响资源规模增加对 HEADER_ONLY 端到端时延影响较小，主要成本由链上交易等待与固定流程主导；该观察为描述性结论，不与其他语义类比较。

### 6.10.3 E3：BODY_ROTATION 工程开销与正确性（RQ-3）

E3 覆盖 Body 规模 64 KiB/1 MiB/8 MiB 与接收者 2/8/32，共 45 个 RUN，全部有效。在接收者为 2 的条件下，Body 由 64 KiB 增至 8 MiB 时，端到端时延中位数由 5083 ms 增至 6696 ms（差 1613 ms，ratio 1.317，Cliff's delta 0.60）；其余配置中位数约 4.98～5.10 s。不同 Body 规模下的时延分布如图 6-2 所示。

密码与版本正确性方面，45/45 个 RUN 中旧 CK 无法解密新 Body、Body 摘要发生改变且版本关系正确。性能测量与正确性验证分开表述：性能为描述性工程测量，正确性为逐 RUN 不变量通过。

### 6.10.4 E4：撤销与 Fail-Closed（RQ-4）

E4 覆盖撤销后的 pending 窗口与 Header 闭合两条路径，共 10 个 RUN，全部有效。材料释放判定为：pending 窗口 5 次 DENIED，Header 闭合后 5 次 ALLOWED_AFTER_CURRENT_HEADER_ONLY；错误材料释放为 0。撤销事件触发后，Header 未闭合期间材料释放被拒绝，Header 进入 current 状态后合法材料恢复释放，状态转换可追踪。

### 6.10.5 E5：故障恢复与副本作用（RQ-5/RQ-6）

E5 覆盖 LOCAL_ONLY/KUBO_REPLICA 两种对象来源与 NONE、CORRUPT_RESTORE、CID_MISMATCH、BOTH_MISSING 四类故障，共 40 个 RUN，全部有效。恢复结果汇总见表 6-3，LOCAL_ONLY 与 KUBO_REPLICA 在匹配故障块内的时延对比如图 6-3 所示。

在对象损坏场景下，LOCAL_ONLY 无法从其他来源恢复，恢复结果为 UNRECOVERABLE（Fail-Closed，5/5）；KUBO_REPLICA 从隔离副本恢复，结果为 CONSISTENT 且修复动作数为 1（5/5）。无故障时两种来源均保持 CONSISTENT；CID 不一致与本地/副本同时缺失时均 Fail-Closed。在受限受控环境中，E5 端到端时延中位数约 3.1～3.2 s（具体数值见表 6-3）。

## 6.11 综合讨论与局限性

实验结果表明：版本化状态关系在冻结配置内保持闭合；撤销保持 Fail-Closed；Header 更新规模因素对端到端时延影响较小，主要成本来自链上等待；Body Rotation 在 8 MiB 规模下出现可观察的时延上升，同时正确性不变量全部保持；Kubo 副本的核心作用是在特定本地对象损坏场景下提供可验证的恢复来源，并未表现出稳定的正常路径性能优势（多数匹配块内 Cliff's delta 约 0.04，未观察到清晰性能效应）。该副本机制属于可用性收益与恢复成本之间的 trade-off。

研究内容三的适用范围限定如下：单节点 QBFT 环境，不评估多 Validator 共识性能；29 个冻结配置与 5 次重复构成有界工程精度样本，不作总体推断；受控隔离环境，故障类别覆盖冻结的 4 类对象故障；仅前瞻性撤销；Body/接收者规模范围有限；实验验证不构成形式化证明。

## 6.12 本章小结

本章提出了版本化密文头部与前瞻性撤销闭环机制，将链上授权状态、数据库任务状态与链下不可变对象组织为可验证的闭合关系。正式实验在受控单节点环境中完成 145 个有效运行：正确性与安全不变量全部满足，未观察到错误材料释放；HEADER_ONLY 与 BODY_ROTATION 的成本结构分别描述；恢复机制在损坏场景下提供可验证的恢复来源，并如实报告未观察到清晰性能效应的副本结果。以上结论以冻结配置、预注册统计与不可变运行记录为边界。

---

**图 6-1（E2）** 不同接收者与受影响资源规模下 HEADER_ONLY 操作端到端时延分布（n=5/配置）
来源：`experiments/r3/formal/figures/i12-final/fig-rq2-header-only-duration.png`；正文先引用后出现。

**图 6-2（E3）** 不同 Body 规模与接收者规模下 BODY_ROTATION 操作端到端时延分布（n=5/配置）
来源：`experiments/r3/formal/figures/i12-final/fig-rq3-body-rotation-duration.png`。

**图 6-3（E5）** 匹配故障块下 LOCAL_ONLY 与 KUBO_REPLICA 恢复运行端到端时延对比（n=5/单元格）
来源：`experiments/r3/formal/figures/i12-final/fig-rq5-recovery-local-kubo.png`。

**表 6-1** 正式实验配置与运行汇总（29 配置 / 35 warm-up / 145 measured）
来源：`experiments/r3/formal/tables/i12-final/table-run-flow-eligibility.json`。

**表 6-2** E2/E3 各配置端到端时延中位数、IQR 与 95% bootstrap CI
来源：`experiments/r3/formal/tables/i12-final/table-within-class-duration.json`。

**表 6-3** E5 恢复结果与时长汇总（按故障与对象来源）
来源：`experiments/r3/formal/tables/i12-final/table-matched-local-kubo-recovery.json`。

**表 6-4** E4 材料释放判定结果
来源：`experiments/r3/formal/tables/i12-final/table-release-decision-outcome.json`。

**表 6-5** 正式实验环境（硬件、OS、软件版本、链/数据库/Kubo 配置）
来源：`experiments/r3/formal/tables/i12-final/table-environment-fingerprint.json`。
