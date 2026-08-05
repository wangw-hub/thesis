# M6 → M7 变更说明（CHANGELOG）

- 日期：2026-08-04
- 基线：`docs/midterm-report/m6/M6-MIDTERM-SOURCE.md`（M6 候选稿，35 页）
- 原则：内容守恒、事实冻结、不做篇幅扩张；只做公式/算法/表格/引用/措辞/版式收口。

## 1. 公式系统（17 → 16）

1. 式(1) `S(P)` 与式(3) `C(P)`：修复 OMML 空 nary 基（`<m:e/>`）导致的 Word 虚线方框占位符；并集参数改用 `\left...\right`。
2. 删除原式(10) `release ⇒ status=ACTIVE ∧ dbAvailable`（信息量低、与材料释放判定重复）。
3. 研究内容三公式全部按冻结源码重写：
   - 密文头部摘要：区分 `headerCoreDigest = SHA-256(D_H‖JCS(HeaderCore))` 与 `headerObjectDigest = SHA-256(signedHeader)`，正文另述 `bodyObjectDigest`；
   - HPKE：补充 `Info(ctx)`/`AAD(ctx)` 上下文绑定，正文说明绑定字段；
   - 密文主体：改为分块 `C_j = AES-256-GCM(CK,N_j,M_j,AAD(ctx,j))`，`N_j = N0‖BE32(j)`；
   - 材料释放：由不完整的 `release iff …` 改为必要条件式 `ReleaseAllowed(ctx) ⇒ stateConsistent ∧ digestMatch ∧ headerObjectValid`；
   - 恢复：由 `restore iff …` 改为 `CandidateAcceptable(candidate) ⇔ digestMatch ∧ structuralValid`，正文两级表述（候选可接受判定与恢复执行判定）。
4. 版本迁移公式 (13)(14) 移至对应算法之前，遵循“版本语义定义 → 状态迁移公式 → 算法6 → 算法7”的顺序。

## 2. 算法系统（8 个，编号连续）

1. 算法1 Normalize：修复首轮把空 `cur` 加入 `I*` 的缺陷；删除冗余条件“`l ≤ cur.right 或 l = cur.right`”；明确空输入提前返回。
2. 算法2 Cover：输入保持单区间 `I=[l,r)`；删除未参与计算的 `L=2^⌈log2 U⌉`。
3. 算法3 PolicyCompile：`C ← Cover(I*,U)` 改为 `for I∈I*: C ← C ∪ Cover(I,U)`，与算法2及正文公式统一。
4. 算法6/7：顺序对调并重编号（算法6=仅密文头更新 HeaderOnlyUpdate，算法7=密文主体与密钥轮换 BodyRotation），标题补英文名；登记字段改为三个独立摘要。
5. 所有算法保留“输入/输出/分步/末尾横线”格式，DOCX 中不含“算法结束”文字。

## 3. 表格（8 张数据表）

- 表头行设置 `w:tblHeader`（跨页重复表头）、全部行 `w:cantSplit`、表内段落 `keepNext` 链。
- 原跨页的表5/表6/表8 现均整表置于单页完整展示（第 22/27/31 页），无需“续表”标题。
- 表号连续（表1–表8），表题位于表上方。

## 4. 参考文献（31 → 34）

- 新增 3 篇 2024/2025 文献并双源核验：[14] Zhang et al. Computer Networks 2024；[16] Ruan et al. IEEE TCE 2024；[22] Li et al. Mathematics 2025。
- 引用语义修正：QuickCheck [26] 仅支撑性质测试方法，不再支撑“15120 条正式记录”；JCS [33] 从研究内容一移至研究内容三（Header JCS 规范化序列化）。
- 全量按正文首次出现顺序重新编号；missing/orphan/duplicate/order 均为 0。
- 2021—2026 占比 21/34（61.8%）；2024—2026 共 12 篇。

## 5. 措辞与术语

- 区块链表述：删除“不可篡改账本”“天然的技术基础”，改为“多副本一致、可审计、可追溯的共享状态基础”。
- OAuth/JWT 局限：增加限定“在仅依赖无状态离线令牌校验、且未引入共享原子状态或在线状态查询机制的情况下”。
- 创新点一：不再绝对化“已有模型多面向连续时间”，改为“现有时态访问控制研究已能表达角色启停、周期授权及时间条件，但其研究重点通常不在于……”。
- 工程类名密度降低：授权状态合约（AuthorizationState）、密文头部注册合约（HeaderRegistry）、材料释放判定模块（AccessMaterialReleaseGuard）、本地不可变对象存储（LocalObjectStore）、恢复协调器（RecoveryCoordinator）、签发方（Issuer）、验证方（Verifier）、操作标识（operationId）、策略摘要（policyDigest）等首次中文+英文、后续仅中文。

## 6. 阶段性研究成果

- 改为“真实状态表述”：论文“初稿已完成，拟投稿《软件学报》”；两件专利“拟申请发明专利，专利文本撰写中”；删除 `[J]`/`中国, [P]` 等疑似已发表/已申请格式；无虚构投稿或申请状态。

## 7. “存在的主要问题和解决办法”

- 第 2 条措辞收敛：不硬性承诺大规模缓存/批量 Header/更多 Verifier/多节点共识实验，改为“根据学位论文整体论证需要，在不改变当前冻结实验结论的前提下开展必要的针对性补充验证；若某项扩展不构成核心主张所必需的证据，则将其作为研究局限或后续工作进行讨论”。

## 8. 封面与版式

- 攻读学位级别：删除重复的 Wingdings 2 F052 复选框符号，仅保留单一“☑硕士”。
- 培养方式：保持模板“全日制”选中标记（单符号），学校空白模板确认存在官方分页（第 2 页空白为模板固有）。
- 表单区段标签设置 `keepWithNext`，消除“阶段性研究成果”孤标题。
- 修正 M6 遗留的“冗余度实验 冗余度实验表明”“边界策略实验 边界实验覆盖”等重复标签与个别空格。

## 9. 时间一致性

- 发现封面填表日期（2026-07-27）早于研究内容三正式实验完成/冻结日期（2026-08-02）及仓库首个提交（2026-07-28）。未自行修改日期或删除结果，详见 `TEMPORAL_CONSISTENCY_AUDIT.json`，最终定稿需用户确认处理方式。

## 10. 产出物

- `王威-专业学位研究生学位论文中期考评表-M7最终候选稿.docx`
- `王威-专业学位研究生学位论文中期考评表-M7最终候选稿.pdf`（36 页）
- `M7-MIDTERM-SOURCE.md`
- `FORMULA_AUDIT.json` / `ALGORITHM_AUDIT.json` / `TABLE_LAYOUT_AUDIT.json` / `REFERENCE_AUDIT.json` / `TEMPORAL_CONSISTENCY_AUDIT.json`
- `FINAL_QA_REPORT.md` / `M7-state.json`

未修改：M6 全部资产、I9–I12 冻结实验数据、正式论文母本；未执行 push。
