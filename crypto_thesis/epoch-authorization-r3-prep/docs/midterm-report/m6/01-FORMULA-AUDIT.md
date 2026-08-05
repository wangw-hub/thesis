# 01 公式审计

## 1. 审计原则（严格核心公式原则）

只有满足以下至少一项的数学关系才保留为编号展示公式：
A. 定义全文核心研究对象；B. 后文明文以“式（x）”引用；C. 构成正确性/复杂度/安全属性分析基础；
D. 构成授权接受/拒绝核心关系；E. 构成密码封装/版本变化/材料释放核心关系；F. 构成正式实验指标定义。

## 2. M5 公式 26 条 → M6 状态

| M5编号 | 内容 | M6状态 | 理由 | M6编号 |
|---|---|---|---|---|
| 1 | `S(P)=\bigcup_{i=1}^{n}\{x\in T\mid l_i\le x<r_i\}` | KEEP_DISPLAY | 核心语义定义（允许槽集合），正文以式（1）引用 | 1 |
| 2 | `T=\{0,1,\ldots,U-1\}` | MOVE_INLINE | 普通符号定义，已写入正文行内 | — |
| 3 | `\phi(t)=\lfloor(t-t_0)/\Delta\rfloor` | MOVE_INLINE | 时间槽映射符号定义，后文未按编号引用，已写入正文行内 | — |
| 4 | `\mathcal{D}=[t_0,t_0+U\Delta)` | MOVE_INLINE | 普通符号定义，已写入正文行内 | — |
| 5 | `I^*=\operatorname{Normalize}(P)=\langle[a_1,b_1),\ldots,[a_k,b_k)\rang` | KEEP_DISPLAY | 唯一语义表示核心定义，正文以式（2）引用；按规范移至算法1之前的形式化模型 | 2 |
| 6 | `C(P)=\bigcup_{I\in I^*}C(I),\ c=|C(P)|` | KEEP_DISPLAY | 派生执行表示核心定义，正文以式（3）引用 | 3 |
| 7 | `D(j,s)=[j2^s,(j+1)2^s)` | MOVE_INLINE | 二进制对齐节点符号定义，已写入正文行内 | — |
| 8 | `L=2^{\lceil\log_2 U\rceil}` | MOVE_INLINE | 符号定义，已写入算法2输入说明 | — |
| 9 | `pd=\operatorname{SHA-256}(B(P))` | KEEP_DISPLAY | 策略摘要绑定核心关系，正文以式（4）引用；SHA-256 记法规范化 | 4 |
| 10 | `T(n,c)=O(n\log n+c)` | KEEP_DISPLAY | 输出敏感复杂度刻画，构成复杂度分析基础，正文以式（5）引用 | 5 |
| 11 | `B(P)=\operatorname{CanonicalSerialize}(t_0,\Delta,U,I^*)` | KEEP_DISPLAY | 规范编码核心定义，正文以式（6）引用 | 6 |
| 12 | `stateVersion'=stateVersion+1\ \wedge\ REVOKED\ 为终态` | MOVE_INLINE | 普通状态性质陈述，后文未按编号引用，已并入正文陈述 | — |
| 13 | `U=(account,userKeyId,status,userVersion,updatedAtBlock)` | MOVE_INLINE | 普通字段列表，已改写为正文行内元组表述 | — |
| 14 | `R=(owner,policyDigest,epoch,status,policyVersion,stateVersion,updatedA` | MOVE_INLINE | 普通字段列表，已改写为正文行内元组表述 | — |
| 15 | `\sigma=\operatorname{Ed25519.Sign}(sk_I,B)` | KEEP_DISPLAY | 能力凭证签名核心关系（密码封装），正文以式（7）引用 | 7 |
| 16 | `B=\operatorname{Encode}(F_1\Vert F_2\Vert\cdots\Vert F_n)` | KEEP_DISPLAY | 签名输入编码关系，正文以式（8）引用；去除实现代号下标 | 8 |
| 17 | `\text{INSERT}(k)=1\Leftrightarrow k\notin consumed,\ k=(chain,contract` | KEEP_DISPLAY | 原子一次性消费核心关系，构成授权接受/拒绝判定基础 | 9 |
| 18 | `release\Rightarrow status=ACTIVE\wedge dbAvailable` | KEEP_DISPLAY | 故障闭合核心关系（依赖故障时拒绝放行） | 10 |
| 19 | `hdrHash=\operatorname{SHA-256}(\operatorname{Canonical}(Header)),\ Hea` | KEEP_DISPLAY | 版本登记核心关系（链上注册表绑定） | 11 |
| 20 | `EK_R=\operatorname{HPKE.Seal}(pk_R,CK)` | KEEP_DISPLAY | 混合加密核心关系 | 12 |
| 21 | `C_{body}=\operatorname{AES-256-GCM}(K,N,M)` | KEEP_DISPLAY | 密码封装核心关系 | 13 |
| 22 | `keyVersion=bodyVersion` | MOVE_INLINE | 普通绑定关系，已并入正文陈述 | — |
| 23 | `(h,b,k)\mapsto(h+1,b+1,k+1)` | KEEP_DISPLAY | 密文主体与密钥轮换的版本核心关系 | 14 |
| 24 | `(h,b,k)\mapsto(h+1,b,k)` | KEEP_DISPLAY | 仅密文头更新的版本核心关系 | 15 |
| 25 | `release\Leftrightarrow status=ACTIVE\wedge t\in S(I^*)\wedge hdrValid` | KEEP_DISPLAY | 材料释放核心判定关系 | 16 |
| 26 | `restore\Leftrightarrow \operatorname{SHA-256}(candidate)=objHash\wedge` | KEEP_DISPLAY | 恢复判定核心关系（完整性权威唯一） | 17 |

## 3. 结论

- 保留展示公式：17 条（KEEP_DISPLAY）；移动为行内：9 条（MOVE_INLINE）；删除冗余：0 条。
- FORMULA_PLACEHOLDER_ERROR = 0（OMML 转换逐条测试通过，无占位符/乱码）。
- FORMULA_GARBAGE = 0；UNREFERENCED_TRIVIAL_DISPLAY_EQUATION = 0。
- 全部展示公式居中、编号右对齐，使用 Word 原生 OMML。
