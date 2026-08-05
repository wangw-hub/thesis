# 02 公式审计（FORMULA AUDIT）

- 总数：16（M7 亦为 16，未新增）
- FORMULA_RENDER_ERROR = 0；FORMULA_SEMANTIC_ERROR = 0；FORMULA_OVERFLOW = 0；FORMULA_PLACEHOLDER = 0

| 式号 | 位置 | 内容 | 本轮动作 | 依据 |
|---|---|---|---|---|
| (1) | RC1 | S(P)=⋃{x∈T∣l_i≤x<r_i} | 保持 | 冻结形式化模型；`\left...\right` 防占位符 |
| (2) | RC1 | I*=Normalize(P) | 保持 | 规范化算法与 81 项测试 |
| (3) | RC1 | C(P)=⋃C(I), c=|C(P)| | 保持 | Cover/PolicyCompile 接口统一 |
| (4) | RC1 | pd=SHA-256(B(P)) | 保持 | 固定宽度规范编码 |
| (5) | RC1 | T(n,c)=O(n log n+c) | 保持 | 输出敏感复杂度分析 |
| (6) | RC1 | B(P)=CanonicalSerialize(t0,Δ,U,I*) | 保持 | 序列化器 |
| (7) | RC2 | σ=Ed25519.Sign(sk_I,B_cap) | 符号修正 | B→B_cap（与 RC1 B(P) 区分） |
| (8) | RC2 | B_cap=Encode(F1‖…‖Fn) | 符号修正 | 同上 |
| (9) | RC2 | INSERT(k)⇔k∉consumed | 保持 | PostgreSQL ON CONFLICT 原子消费 |
| (10) | RC3 | headerCoreDigest / headerObjectDigest 对齐数组 | 排版重做 | 由单行双定义改为 OMML eqArr，单编号，不折行 |
| (11) | RC3 | (enc,ct)=HPKE.Seal(pk_R,CK,Info(ctx),AAD(ctx)) | 语义核验 | 与冻结实现 seal_base(pk, plaintext, info, aad) 一致；正文补充 enc/ct 含义与错误 Info/AAD 证据 |
| (12) | RC3 | C_j=AES-256-GCM(CK,N_j,M_j,AAD(ctx,j)); N_j=N0‖BE32(j) | 保持 | chunk_crypto.py |
| (13) | RC3 | (h,b,k)↦(h+1,b,k) | 保持 | HEADER_ONLY |
| (14) | RC3 | (h,b,k)↦(h+1,b+1,k+1) | 保持 | BODY_ROTATION |
| (15) | RC3 | ReleaseAllowed(ctx)⇒stateConsistent∧digestMatch∧headerObjectValid | 保持必要条件 | guard.py；正文无“充分保证”表述 |
| (16) | RC3 | CandidateAcceptable(candidate)⇔digestMatch∧structuralValid | 保持边界 | reconciler.py；正文区分候选可接受与恢复执行 |

## 关键核验

1. 式(10) 在 Word 原生 OMML 中为 `<m:eqArr>` 对齐组，PDF 第 23 页渲染为两行对齐、单编号，无横向压缩。
2. 式(11) 实参顺序（接收者公钥、明文 CK、info、aad）与 `src/epoch_auth_r3/crypto/hpke_provider.py` 的 `seal_base` 一致；`tests/r3/i1/test_hpke_context_binding.py` 覆盖错误 Info/AAD 拒绝。
3. 式(15) 方向为必要条件（⇒），不写 iff；式(16) 为候选可接受判定（⇔ 仅对候选），恢复动作由协调器依据完整证据决定。
4. 全部编号 (1)–(16) 连续，按正文出现顺序升序。
