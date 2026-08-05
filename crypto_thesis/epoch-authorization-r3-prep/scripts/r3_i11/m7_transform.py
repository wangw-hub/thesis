# -*- coding: utf-8 -*-
"""M7: transform the frozen M6 midterm source into the M7 final-candidate source.

Scope (M6 -> M7, no content inflation):
  * formulas: fix empty nary placeholder (eq 1/3), delete low-information eq 10,
    and re-derive RC3 formulas (header digests, HPKE context binding, chunked
    body AEAD, release necessary-condition predicate, candidate-acceptable
    predicate) from the frozen implementation.
  * algorithms: fix Normalize empty-cur bug, unify Cover/PolicyCompile
    interface, swap/rename algorithms 6/7, move version-transition formulas
    before the corresponding algorithms.
  * references: move JCS citation to RC3, fix QuickCheck citation semantics,
    add three verified 2024/2025 references, then renumber by first citation
    order.
  * wording: temper blockchain/OAuth/JWT claims, reduce code-class-name
    density, restate stage results in "real status" form, converge problem 2
    wording.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
M6 = ROOT / "docs/midterm-report/m6/M6-MIDTERM-SOURCE.md"
OUT_DIR = ROOT / "docs/midterm-report/m7"
OUT = OUT_DIR / "M7-MIDTERM-SOURCE.md"


# ---------------------------------------------------------------------------
# New reference list (final numbering, assigned by the renumbering pass)
# ---------------------------------------------------------------------------
REF_LIST = """### 参考文献
[1] Sandhu R S, Coyne E J, Feinstein H L, et al. Role-based access control models[J]. IEEE Computer, 1996, 29(2): 38-47.

[2] Bertino E, Bonatti P A, Ferrari E. TRBAC: A temporal role-based access control model[J]. ACM Transactions on Information and System Security, 2001, 4(3): 191-233.

[3] Panda S, Sahoo S, Halder R, et al. Contextual attribute-based access control scheme for cloud storage using blockchain technology[J]. Software: Practice and Experience, 2024, 54(10): 2042-2062.

[4] Bethencourt J, Sahai A, Waters B. Ciphertext-policy attribute-based encryption[C]//Proceedings of the 2007 IEEE Symposium on Security and Privacy. IEEE, 2007: 321-334.

[5] Hardt D. The OAuth 2.0 authorization framework[S]. RFC 6749, 2012.

[6] Jones M, Bradley J, Sakimura N. JSON Web Token (JWT)[S]. RFC 7519, 2015.

[7] Nakamoto S. Bitcoin: A peer-to-peer electronic cash system[EB/OL]. 2008. https://bitcoin.org/bitcoin.pdf.

[8] Androulaki E, Barger A, Bortnikov V, et al. Hyperledger Fabric: A distributed operating system for permissioned blockchains[C]//Proceedings of the 13th European Conference on Computer Systems (EuroSys). ACM, 2018: 30.

[9] Rouhani S, Belchior R, Cruz R S, et al. Distributed attribute-based access control system using permissioned blockchain[J]. World Wide Web, 2021, 24(5): 1617-1644.

[10] Singh R, Kukreja D, Sharma D K. Blockchain-enabled access control to prevent cyber attacks in IoT: Systematic literature review[J]. Frontiers in Big Data, 2022, 5: 1081770.

[11] Wang P, Xu N, Zhang H, et al. Dynamic access control and trust management for blockchain-empowered IoT[J]. IEEE Internet of Things Journal, 2022, 9(15): 12997-13009.

[12] Sun L, Zhou D, Liu D, et al. BPDAC: A blockchain based and provenance enabled dynamic access control scheme[J]. IEEE Access, 2023, 11: 142552-142568.

[13] Akhtar M, Barati M, Shafiq B, et al. Blockchain based auditable access control for business processes with event driven policies[J]. IEEE Transactions on Dependable and Secure Computing, 2024, 21(5): 4699-4716.

[14] Zhang Q, Yuan L, Xie T, et al. Auditable and dynamic access control scheme with behavior and identity tracing[J]. Computer Networks, 2024, 251: 110623.

[15] Guo Y, Lu Z, Ge H, et al. Revocable blockchain-aided attribute-based encryption with escrow-free in cloud storage[J]. IEEE Transactions on Computers, 2023, 72(7): 1901-1912.

[16] Ruan C, Hu C, Li X, et al. A revocable and fair outsourcing attribute-based access control scheme in metaverse[J]. IEEE Transactions on Consumer Electronics, 2024, 70(1): 3781-3791.

[17] Wang S, Yang M, Jiang S, et al. BBS: A secure and autonomous blockchain-based big-data sharing system[J]. Journal of Systems Architecture, 2024, 150: 103133.

[18] Nguyen L D, Hoang J, Wang Q, et al. BDSP: A fair blockchain-enabled framework for privacy-enhanced enterprise data sharing[C]//2023 IEEE International Conference on Blockchain and Cryptocurrency (ICBC). IEEE, 2023: 1-9.

[19] Xu Z, Sun Q, Han H, et al. BMTAC: A decentralized, auditable, time-limited, multi-authority attribute access control scheme in blockchain environment[C]//2022 IEEE SmartWorld/UIC/ScalCom/DigitalTwin/PriComp/Meta. IEEE, 2022: 1997-2002.

[20] Tran-Truong P T, Son H X, Khanh V H, et al. TACKLE: Time-based access control and key delegation for letter of credit ecosystems[J]. High-Confidence Computing, 2025, 5: 100369.

[21] Zhang X, Du W, Moshayedi A J. A traceable and revocable multi-authority attribute-based access control scheme for mineral industry data secure storage in blockchain[J]. The Journal of Supercomputing, 2023, 79(13): 14743-14779.

[22] Li K, Pan H, Zhang Y, et al. A blockchain-enabled decentralized autonomous access control scheme for data sharing[J]. Mathematics, 2025, 13(17): 2712.

[23] Slamanig D, Striecks C. Revisiting updatable encryption: Controlled forward security, constructions and a puncturable perspective[C]//Theory of Cryptography Conference (TCC 2023), LNCS 14370. Springer, 2023: 220-250.

[24] Zhou Y, Zhu X, Chen A, et al. Access control mechanism in distributed smart power plants based on blockchain and ciphertext updatable functional encryption[J]. Peer-to-Peer Networking and Applications, 2024, 17(2): 1021-1035.

[25] Hameed Z, Barzegar H R, El Ioini N, et al. BE-DSN: Leveraging blockchain for improving data availability and security in distributed storage networks[J]. Cluster Computing, 2025, 28(7).

[26] Claessen K, Hughes J. QuickCheck: A lightweight tool for random testing of Haskell programs[C]//Proceedings of the Fifth ACM SIGPLAN International Conference on Functional Programming (ICFP). ACM, 2000: 268-279.

[27] Hyperledger Besu Documentation. QBFT consensus protocol[EB/OL]. [2026-08-02]. https://besu.hyperledger.org/private-networks/how-to/configure/consensus/qbft.

[28] Josefsson S, Liusvaara I. Edwards-Curve digital signature algorithm (EdDSA)[S]. RFC 8032, 2017.

[29] PostgreSQL Global Development Group. PostgreSQL 16 documentation: INSERT[EB/OL]. [2026-08-02]. https://www.postgresql.org/docs/16/sql-insert.html.

[30] Efron B. Bootstrap methods: Another look at the jackknife[J]. The Annals of Statistics, 1979, 7(1): 1-26.

[31] Dworkin M. Recommendation for block cipher modes of operation: Galois/Counter Mode (GCM) and GMAC[S]. NIST Special Publication 800-38D, 2007.

[32] Barnes R, Bhargavan K, Lipp B, et al. Hybrid public key encryption[S]. RFC 9180, 2022.

[33] Rundgren A, Jordan B, Erdtman S. JSON canonicalization scheme (JCS)[S]. RFC 8785, 2020.

[34] Benet J. IPFS - Content addressed, versioned, P2P file system[EB/OL]. arXiv:1407.3561, 2014[2026-08-02]. https://arxiv.org/abs/1407.3561.

"""


# ---------------------------------------------------------------------------
# Algorithm blocks
# ---------------------------------------------------------------------------
ALGO1 = """[算法块：算法1 非连续时间策略规范化算法（Normalize）
输入：已离散化区间序列 P=[l1,r1),…,[ln,rn)，时间域槽数 U
输出：规范区间序列 I*
1: 将 P 中各区间按左端点升序排序，左端点相同时按右端点升序排序
2: if P 为空 then
3:     return 空序列 I*
4: end if
5: cur ← 排序后序列中的首个区间 [l,r)
6: for 排序后序列中的每个剩余区间 [l,r) do
7:     if l ≤ cur.right then
8:         cur.right ← max(cur.right, r)   /* 合并相交或相邻区间 */
9:     else
10:         将 cur 加入 I*；cur ← [l,r)     /* 开始新分量 */
11:     end if
12: end for
13: 将最后一个 cur 加入 I*
14: return I*                              /* 有序、互斥、互不相邻 */
算法结束]"""

ALGO2 = """[算法块：算法2 二进制层次覆盖生成算法（Cover）
输入：规范区间 I=[l,r)，槽总数 U
输出：最大对齐覆盖节点集合 C
1: C ← ∅；pos ← l
2: while pos < r do
3:     size ← 当前位置可用的最大 2 的幂对齐块
4:     while size > r−pos do size ← size ≫ 1   /* 不超过剩余长度 */
5:     将节点 (pos,size) 加入 C
6:     pos ← pos + size
7: end while
8: return C                                /* 节点互斥、首尾相接、并集等于 I */
算法结束]"""

ALGO3 = """[算法块：算法3 确定性策略编译与摘要生成算法（PolicyCompile）
输入：时区感知起点 t0、时间粒度 Δ、槽总数 U、原始区间序列 P
输出：唯一语义表示 I*、层次执行表示 C、规范字节串 B、策略摘要 pd
1: 校验 t0 可转换为 UTC、Δ>0、U>0，且 P 的端点均落在 [0,U) 内
2: I* ← Normalize(P)                      /* 唯一语义表示 */
3: C ← ∅
4: for 每个规范区间 I ∈ I* do
5:     C ← C ∪ Cover(I,U)                 /* 派生执行表示，可由 I* 再生成 */
6: end for
7: B ← CanonicalSerialize(t0,Δ,U,I*)      /* 固定宽度规范编码 */
8: pd ← SHA-256(B)                        /* 策略摘要 */
9: return (I*,C,B,pd)
算法结束]"""

RC3_VERSION_BLOCK = """版本语义被冻结为三类操作：初始发布表示初始状态（headerVersion=1，bodyVersion=1，keyVersion=1）；仅密文头更新表示仅更新密文头部（headerVersion 加 1，bodyVersion 与 keyVersion 不变，密文主体与内容密钥不变）；密文主体与密钥轮换表示整体轮换（headerVersion、bodyVersion、keyVersion 均加 1，生成新内容密钥与新密文主体）。两类状态迁移的语义先于算法给出定义：仅密文头更新执行 (h,b,k)↦(h+1,b,k)，密文主体与密钥轮换执行 (h,b,k)↦(h+1,b+1,k+1)，如式（13）、式（14）所示。仅密文头更新用于授权语义变化（如撤销后的密文头部闭合）而不更换数据密钥，密文主体与密钥轮换用于更换密文对象与密钥。二者是不同语义的操作：仅密文头更新面向授权状态变化，密文主体与密钥轮换面向密钥与对象更新，实验中分别分析，不作等价比较。

[公式：(h,b,k)\\mapsto(h+1,b,k).]

[公式：(h,b,k)\\mapsto(h+1,b+1,k+1).]

[算法块：算法6 仅密文头更新算法（HeaderOnlyUpdate）
输入：受影响资源、授权语义变化（撤销、暂停或策略更新）
输出：新密文头部与链上登记记录
1: 解析受影响资源，生成密文头部更新意图
2: 构造新密文头部：headerVersion ← headerVersion+1，bodyVersion 与 keyVersion 保持不变
3: 以 JCS 规范序列化新密文头部并计算摘要
4: 以 Ed25519 私钥签名，得到新的版本化密文头部
5: 将 (headerCoreDigest,headerObjectDigest,bodyObjectDigest) 登记至链上密文头部注册合约
6: 新密文头部进入当前状态后恢复合法材料释放，不更换数据密钥
7: return 新密文头部与登记记录
算法结束]

[算法块：算法7 密文主体与密钥轮换算法（BodyRotation）
输入：需要轮换的密文对象（密钥或内容变化）
输出：新密文主体、新内容密钥 CK′、新密文头部
1: 生成新内容密钥 CK′
2: 以 CK′ 对密文主体执行 AES-256-GCM 分块加密，生成新密文主体
3: for 每个接收者 do
4:     以 HPKE 为新内容密钥生成加密封装记录
5: end for
6: 构造新密文头部：(headerVersion,bodyVersion,keyVersion) ← (h+1,b+1,k+1)
7: JCS 序列化、Ed25519 签名并登记至密文头部注册合约
8: return 新密文主体、新内容密钥与新密文头部
算法结束]"""


def _old_algo1() -> str:
    return """[算法块：算法1 非连续时间策略规范化算法（Normalize）
输入：已离散化区间序列 P=[l1,r1),…,[ln,rn)，时间域槽数 U
输出：规范区间序列 I*
1: 将 P 中各区间按左端点升序排序，左端点相同时按右端点升序排序
2: cur ← []
3: for 排序后序列中的每个区间 [l,r) do
4:     if cur 非空 且 l ≤ cur.right 或 l = cur.right then
5:         cur.right ← max(cur.right, r)   /* 合并相交或相邻区间 */
6:     else
7:         将 cur 加入 I*；cur ← [l,r)     /* 开始新分量 */
8:     end if
9: end for
10: 将最后一个 cur 加入 I*
11: return I*                              /* 有序、互斥、互不相邻 */
算法结束]"""


def _old_algo2() -> str:
    return """[算法块：算法2 二进制层次覆盖生成算法（Cover）
输入：规范区间 I=[l,r)，槽总数 U，对齐上界 L=2^⌈log2 U⌉
输出：最大对齐覆盖节点集合 C
1: C ← ∅；pos ← l
2: while pos < r do
3:     size ← 当前位置可用的最大 2 的幂对齐块
4:     while size > r−pos do size ← size ≫ 1   /* 不超过剩余长度 */
5:     将节点 (pos,size) 加入 C
6:     pos ← pos + size
7: end while
8: return C                                /* 节点互斥、首尾相接、并集等于 I */
算法结束]"""


def _old_algo3() -> str:
    return """[算法块：算法3 确定性策略编译与摘要生成算法（PolicyCompile）
输入：时区感知起点 t0、时间粒度 Δ、槽总数 U、原始区间序列 P
输出：唯一语义表示 I*、层次执行表示 C、规范字节串 B、策略摘要 pd
1: 校验 t0 可转换为 UTC、Δ>0、U>0，且 P 的端点均落在 [0,U) 内
2: I* ← Normalize(P)                      /* 唯一语义表示 */
3: C ← Cover(I*,U)                        /* 派生执行表示，可由 I* 再生成 */
4: B ← CanonicalSerialize(t0,Δ,U,I*)      /* 固定宽度规范编码 */
5: pd ← SHA-256(B)                        /* 策略摘要 */
6: return (I*,C,B,pd)
算法结束]"""


def _old_rc3_version() -> str:
    return """版本语义被冻结为三类操作：初始发布表示初始状态（headerVersion=1，bodyVersion=1，keyVersion=1）；仅密文头更新 表示仅更新 Header（headerVersion 加 1，bodyVersion 与 keyVersion 不变，Body 与 CK 不变）；密文主体与密钥轮换 表示整体轮换（headerVersion、bodyVersion、keyVersion 均加 1，生成新 CK 与新 Body）。仅密文头更新 用于授权语义变化（如撤销后的 Header 闭合）而不更换数据密钥，密文主体与密钥轮换 用于更换密文对象与密钥。二者是不同语义的操作：仅密文头更新 面向授权状态变化，密文主体与密钥轮换 面向密钥与对象更新，实验中分别分析，不作等价比较。

[算法块：算法7 密文主体与密钥轮换算法
输入：需要轮换的密文对象（密钥或内容变化）
输出：新密文主体、新内容密钥 CK′、新密文头部
1: 生成新内容密钥 CK′
2: 以 CK′ 对密文主体执行 AES-256-GCM 分块加密，生成新密文主体
3: for 每个接收者 do
4:     以 HPKE 为新内容密钥生成加密封装记录
5: end for
6: 构造新密文头部：(headerVersion,bodyVersion,keyVersion) ← (h+1,b+1,k+1)
7: JCS 序列化、Ed25519 签名并登记至密文头部注册表
8: return 新密文主体、新内容密钥与新密文头部
算法结束]

[算法块：算法6 仅密文头更新算法
输入：受影响资源、授权语义变化（撤销、暂停或策略更新）
输出：新密文头部与链上登记记录
1: 解析受影响资源，生成密文头部更新意图
2: 构造新密文头部：headerVersion ← headerVersion+1，bodyVersion 与 keyVersion 保持不变
3: 以 JCS 规范序列化新密文头部并计算摘要
4: 以 Ed25519 私钥签名，得到新的版本化密文头部
5: 将 (hdrHash,objHash) 登记至链上密文头部注册表
6: 新密文头部进入当前状态后恢复合法材料释放，不更换数据密钥
7: return 新密文头部与登记记录
算法结束]

[公式：(h,b,k)\\mapsto(h+1,b+1,k+1).]

[公式：(h,b,k)\\mapsto(h+1,b,k).]"""


# ---------------------------------------------------------------------------
# Ordered text replacements (old -> new)
# ---------------------------------------------------------------------------
REPLACEMENTS: list[tuple[str, str, str]] = []


def rep(key: str, old: str, new: str, count: int = 1) -> None:
    REPLACEMENTS.append((key, old, new, count))


# --- background wording / citations ----------------------------------------
rep(
    "blockchain-claim",
    "区块链凭借不可篡改账本、智能合约和可追溯事件记录，为多方环境下的状态一致性与责任审计提供了天然的技术基础[7-9]",
    "区块链通过多副本一致、可审计、可追溯的共享状态基础与智能合约机制，为多方环境下的状态一致性与责任审计提供了支撑[7-9]",
)
rep(
    "zhang-citation",
    "近年研究进一步从动态访问控制[11]、行为与来源感知的授权判定[12]以及面向业务流程的可审计授权[13]等角度推进了该问题的解决。",
    "近年研究进一步从动态访问控制[11]、行为与来源感知的授权判定[12]、面向业务流程的可审计授权[13]以及兼具行为与身份追溯的动态访问控制[«NEWZHANG»]等角度推进了该问题的解决。",
)
rep(
    "oauth-qualifier-bg",
    "普通令牌的有效性取决于签发时点的快照[5][6]，难以在验证时点约束动态状态与跨实例重放[5][6]",
    "在仅依赖无状态离线令牌校验、且未引入共享原子状态或在线状态查询机制的情况下，普通令牌的有效性取决于签发时点的快照[5][6]，难以在验证时点约束动态状态与跨实例重放[5][6]",
)
rep(
    "ruan-citation",
    "针对属性基加密的撤销与密钥托管问题，近年工作提出可撤销且免托管的链上属性基加密方案[14]",
    "针对属性基加密的撤销与密钥托管问题，近年工作提出可撤销且免托管的链上属性基加密方案[14]，面向元数据场景的可撤销公平外包属性访问控制方案[«NEWRUAN»]亦进一步压缩了撤销开销",
)
rep(
    "zhan-citation",
    "以及可追溯可撤销的属性访问控制[19]。然而",
    "以及可追溯可撤销的属性访问控制[19]、面向数据共享的去中心化自治访问控制[«NEWZHAN»]。然而",
)

# --- innovation point 1 wording --------------------------------------------
rep(
    "innovation1-absolute",
    "已有访问控制模型多面向连续时间或单一时间点，难以表达由多个非对齐窗口、例外日期与周期片段构成的授权规则；",
    "现有时态访问控制研究已经能够表达角色启停、周期授权及时间条件，但其研究重点通常不在于将任意等义的非连续时间区间输入规范化为唯一语义表示，并进一步形成可跨组件复核的确定性策略摘要；",
)
rep(
    "jcs-out-of-rc1",
    "最后以固定宽度规范编码与摘要计算把唯一语义固化[23]为唯一标识",
    "最后以固定宽度规范编码与摘要计算把唯一语义固化为唯一标识",
)
rep(
    "quickcheck-semantics",
    "阶段验证覆盖形式化模型、算法实现、性质测试与 15120 条正式记录[24]，明确了规范区间在实验范围内的稳健性以及层次覆盖的适用边界。",
    "阶段验证采用性质测试方法[24]对规范化幂等性、输入置换不变性等性质进行验证，正式实验共获得 15120 条有效记录，明确了规范区间在实验范围内的稳健性以及层次覆盖的适用边界。",
)

# --- innovation point 2 wording --------------------------------------------
rep(
    "innovation2-oauth",
    "或使用无状态令牌，无法在验证时点约束动态状态、无法统一跨实例重放语义、也无法防止能力在链与合约之间迁移。",
    "或使用无状态令牌；在仅依赖无状态离线令牌校验、且未引入共享原子状态或在线状态查询机制的情况下，无法在验证时点约束动态状态、无法统一跨实例重放语义、也无法防止能力在链与合约之间迁移。",
)

# --- formulas ---------------------------------------------------------------
rep(
    "eq1-nary",
    "[公式：S(P)=\\bigcup_{i=1}^{n}\\{x\\in T\\mid l_i\\le x<r_i\\}.]",
    "[公式：S(P)=\\bigcup_{i=1}^{n}\\left\\{x\\in T\\mid l_i\\le x<r_i\\right\\}.]",
)
rep(
    "eq1-inline-nary",
    "其语义定义为允许槽集合 \\(S(P)=\\bigcup_{i=1}^{n}\\{x\\in T\\mid l_i\\le x<r_i\\}\\)。",
    "其语义定义为允许槽集合 \\(S(P)=\\bigcup_{i=1}^{n}\\left\\{x\\in T\\mid l_i\\le x<r_i\\right\\}\\)。",
)
rep(
    "eq3-nary",
    "[公式：C(P)=\\bigcup_{I\\in I^*}C(I),\\qquad c=|C(P)|.]",
    "[公式：C(P)=\\bigcup_{I\\in I^*}\\left(C(I)\\right),\\qquad c=\\left|C(P)\\right|.]",
)
rep(
    "eq10-delete",
    "\n[公式：\\text{release}\\Rightarrow status=ACTIVE \\wedge \\text{dbAvailable}.]\n",
    "\n",
)
rep(
    "eq11-header-digest",
    "[公式：hdrHash=\\operatorname{SHA\\text{-}256}(\\operatorname{Canonical}(Header)),\\quad HeaderRegistry\\gets(hdrHash,objHash).]",
    "[公式：\\operatorname{headerCoreDigest}=\\operatorname{SHA\\text{-}256}(D_H\\,\\Vert\\,\\operatorname{JCS}(HeaderCore)),\\quad \\operatorname{headerObjectDigest}=\\operatorname{SHA\\text{-}256}(signedHeader).]",
)
rep(
    "eq12-hpke",
    "[公式：EK_{R}=\\operatorname{HPKE.Seal}(pk_R, CK).]",
    "[公式：(enc,ct)=\\operatorname{HPKE.Seal}(pk_R,CK,\\operatorname{Info}(ctx),\\operatorname{AAD}(ctx)).]",
)
rep(
    "eq13-body",
    "[公式：C_{body}=\\operatorname{AES-256-GCM}(K,N,M).]",
    "[公式：C_j=\\operatorname{AES\\text{-}256\\text{-}GCM}(CK,N_j,M_j,\\operatorname{AAD}(ctx,j)),\\quad N_j=N_0\\,\\Vert\\,\\mathrm{BE32}(j).]",
)
rep(
    "eq16-release",
    "[公式：\\text{release iff } status=ACTIVE \\wedge t\\in S(I^*) \\wedge hdrValid.]",
    "[公式：\\text{ReleaseAllowed}(ctx)\\Rightarrow \\text{stateConsistent}\\wedge\\text{digestMatch}\\wedge\\text{headerObjectValid}.]",
)
rep(
    "eq17-restore",
    "[公式：\\text{restore iff } \\operatorname{SHA\\text{-}256}(candidate)=objHash \\wedge structuralValid.]",
    "[公式：\\text{CandidateAcceptable}(candidate)\\Leftrightarrow \\operatorname{SHA\\text{-}256}(candidate)=objHash\\wedge structuralValid.]",
)

# --- algorithms ---------------------------------------------------------------
rep("algo1-normalize", _old_algo1(), ALGO1)
rep("algo2-cover", _old_algo2(), ALGO2)
rep("algo3-compile", _old_algo3(), ALGO3)
rep("algo67-reorder", _old_rc3_version(), RC3_VERSION_BLOCK)

# --- RC3 text refinement ------------------------------------------------------
rep(
    "rc3-object-desc",
    "密文对象由密文头部（Header）与密文主体（Body）两部分构成。密文主体为分块 AES-256-GCM 密文，承载文件主体[29]；Header 的核心字段由 HeaderCore 承载，包括资源标识、Header/Body/Key 版本、Body 摘要与接收者信封等，签名后形成 SignedVersionedHeader。内容密钥（CK）按接收者使用 HPKE（X25519 + HKDF-SHA-256 + AES-128-GCM）封装[30]为 EncryptedCKRecord，每个 Body 版本使用独立 CK，V1 冻结语义为 keyVersion 等于 bodyVersion。Header 使用 JCS 规范序列化并以 Ed25519 签名，其摘要与对象摘要均进入链上 HeaderRegistry 的提交记录，从而把链下对象与链上状态绑定：任何对 Header 或 Body 的篡改都会反映到摘要不一致上，任何版本变化都可以在链上核验。",
    "密文对象由密文头部（Header）与密文主体（Body）两部分构成。密文主体为分块 AES-256-GCM 密文，承载文件主体[29]；密文头部由核心结构与签名构成：核心结构（HeaderCore）承载资源标识、密文头部/密文主体/内容密钥版本、密文主体摘要与接收者信封等字段，签名后形成带版本签名的密文头部（SignedVersionedHeader）。内容密钥（CK）按接收者使用 HPKE（X25519 + HKDF-SHA-256 + AES-128-GCM）封装[30]为内容密钥封装记录（EncryptedCKRecord），每个密文主体版本使用独立内容密钥，V1 冻结语义为 keyVersion 等于 bodyVersion。密文头部使用 JCS 规范序列化[«JCS»]并以 Ed25519 签名。冻结实现区分三个独立摘要：密文头部核心摘要（headerCoreDigest）对带域分隔符的 HeaderCore 规范序列化计算 SHA-256，密文头部对象摘要（headerObjectDigest）对完整签名对象计算 SHA-256，密文主体对象摘要（bodyObjectDigest）对密文主体计算 SHA-256；三者均登记至链上密文头部注册合约（HeaderRegistry）的提交记录，从而把链下对象与链上状态绑定：任何对密文头部或密文主体的篡改都会反映到摘要不一致上，任何版本变化都可以在链上核验。",
)
rep(
    "rc3-envelope-expl",
    "接收者信封支持多接收者场景：每个接收者对应一个 HPKE 封装记录，接收者通过自己的密钥解封装获得内容密钥，未列入信封的实体无法获得 CK，从而实现“授权列表之外的接收者不可解密”。",
    "接收者信封支持多接收者场景：每个接收者对应一个 HPKE 封装记录，接收者通过自己的密钥解封装获得内容密钥，未列入信封的实体无法获得内容密钥，从而实现“授权列表之外的接收者不可解密”。HPKE 封装将应用上下文绑定到 Info 与 AAD：Info 由链标识、授权状态合约、密文头部注册合约、资源标识、版本三元组、策略摘要、epoch、状态版本、接收者密钥标识与用户版本等字段的规范序列化构成，AAD 绑定封装域标识、上述上下文与密文主体摘要；冻结测试确认错误的 Info 或 AAD 均导致解封装失败。",
)
rep(
    "rc3-body-chunk",
    "Body 采用分块加密便于流式处理与部分校验，分块数与摘要计算在发布时确定，后续轮换生成新 Body 与新 CK，旧版本仍可按摘要追溯。",
    "密文主体采用分块加密：每块以 8 字节随机 Nonce 基与 4 字节大端块序号组合为独立 Nonce，AAD 绑定链标识、资源标识、密文主体版本、分块总数与块序号、清单摘要等字段，便于流式处理与部分校验；分块数与摘要计算在发布时确定，后续轮换生成新密文主体与新内容密钥，旧版本仍可按摘要追溯。",
)
rep(
    "rc3-headerupd",
    "需要说明的是，密文头部与密文主体的分离是降低动态更新成本的关键：文件主体通常体积较大，重新加密会产生与文件规模成正比的数据搬移开销；而密文头部体积小、只承载版本与摘要信息，更新头部即可表达授权语义变化。",
    "需要说明的是，密文头部与密文主体的分离是降低动态更新成本的关键：文件主体通常体积较大，重新加密会产生与文件规模成正比的数据搬移开销；而密文头部体积小、只承载版本与摘要信息，更新密文头部即可表达授权语义变化。",
)
rep(
    "rc3-state-machine",
    "版本状态机由 AuthorizationState 与 HeaderRegistry 共同维护：AuthorizationState 保存 policyDigest、epoch、stateVersion 与资源状态，HeaderRegistry 保存 headerVersion、bodyVersion、keyVersion、摘要与操作身份；二者通过资源标识关联，形成“资源状态—对象版本”的双通道记录。",
    "版本状态机由授权状态合约与密文头部注册合约共同维护：授权状态合约保存策略摘要、epoch、状态版本与资源状态，密文头部注册合约保存 headerVersion、bodyVersion、keyVersion、三个摘要与操作身份；二者通过资源标识关联，形成“资源状态—对象版本”的双通道记录。",
)
rep(
    "rc3-release-para",
    "材料释放判定由 AccessMaterialReleaseGuard 依据链上复合状态与 Header 对象完整性执行：只有资源与用户均为有效状态、Header 存在且摘要一致、当前时间落在策略允许窗口内时才允许释放。链上 HeaderRegistry 保存 headerVersion、bodyVersion、keyVersion、摘要与操作身份，与 AuthorizationState 共同构成状态事实源；数据库控制面以任务状态机管理链上写入：任务显式提交后可被独立连接读取，经准入后广播交易，以回执与固定区块状态验证后固化为已提交；数据库事务不跨链回执等待，operationId 保证重复执行幂等，提交结果不确定等异常按预注册规则处理。",
    "材料释放判定由材料释放判定模块（AccessMaterialReleaseGuard）依据链上复合状态与密文头部对象完整性执行，其判定语义为必要条件式：当授权状态超前于密文头部（AUTHORIZATION_AHEAD_OF_HEADER）时判定为 HEADER_UPDATE_PENDING，复合状态非一致时判定为 UNKNOWN（Fail-Closed），仅当复合状态一致、策略摘要/epoch/状态版本匹配且密文头部对象有效时才允许释放；资源与用户有效状态、当前时间落在策略允许窗口内等条件由释放流程在判定之前另行检查，因而材料释放的充分条件由综合谓词与上述外部检查共同构成，论文对该综合判定仅作必要条件式表达，不作不完整的双向等价表述。链上密文头部注册合约保存 headerVersion、bodyVersion、keyVersion、三个摘要与操作身份，与授权状态合约共同构成状态事实源；数据库控制面以任务状态机管理链上写入：任务显式提交后可被独立连接读取，经准入后广播交易，以回执与固定区块状态验证后固化为已提交；数据库事务不跨链回执等待，操作标识保证重复执行幂等，提交结果不确定等异常按预注册规则处理。",
)
rep(
    "rc3-recovery-para",
    "恢复协调的核心原则是“完整性权威唯一、恢复路径可验证”：无论候选对象来自本地存储还是隔离副本，都必须通过相同的 SHA-256 摘要验证与结构验证，验证通过后才能执行原子恢复；验证失败的对象不进入可用状态，系统保持 Fail-Closed 而不是降级使用不可信对象。",
    "恢复协调的核心原则是“完整性权威唯一、恢复路径可验证”：无论候选对象来自本地存储还是隔离副本，都必须通过相同的 SHA-256 摘要验证与结构验证，验证通过后候选对象才被判定为可接受；是否实际执行恢复由恢复协调器依据完整证据（任务状态、可信备份、链上锚点与一致性判定等）综合决定，论文以候选可接受判定与恢复执行判定两级表述，避免把候选完整性误写为恢复动作的充分条件。验证失败的对象不进入可用状态，系统保持 Fail-Closed 而不是降级使用不可信对象。",
)
rep(
    "rc3-kubo",
    "链下对象层由 LocalObjectStore 与隔离的 Kubo 副本组成：本地对象存储以不可变方式存储对象，写入原子，SHA-256 内容寻址为完整性权威[31]；Kubo 仅作为隔离副本定位，CID 不替代 SHA-256 的完整性权威。恢复由 RecoveryCoordinator 协调：读取候选对象、SHA 验证、结构验证、原子恢复，最终形成一致状态或 Fail-Closed 结果。",
    "链下对象层由本地不可变对象存储（LocalObjectStore）与隔离的 Kubo 副本组成：本地不可变对象存储以不可变方式存储对象，写入原子，SHA-256 内容寻址为完整性权威[31]；Kubo 仅作为隔离副本定位，CID 不替代 SHA-256 的完整性权威。恢复由恢复协调器（RecoveryCoordinator）协调：读取候选对象、SHA 验证、结构验证、原子恢复，最终形成一致状态或 Fail-Closed 结果。",
)

# --- class-name density reduction (later occurrences -> Chinese only) --------
rep("term-authstate-049", "链上授权状态合约、能力签发与验证组件", "链上授权状态合约（AuthorizationState）、能力签发与验证组件")
rep("term-authstate-163", "由 `AuthorizationState` 合约分别维护", "由授权状态合约分别维护")
rep("term-registry-049", "共享数据库、密文头部注册表、链下对象存储", "共享数据库、密文头部注册合约（HeaderRegistry）、链下对象存储")
rep("term-guard-365", "材料释放由 AccessMaterialReleaseGuard 依据链上复合状态判定", "材料释放由材料释放判定模块依据链上复合状态判定")
rep("term-issuer-171", "签名密钥由 Issuer 持有并保护", "签名密钥由能力签发方（Issuer）持有并保护")
rep("term-issuer-227", "一台承载非验证 RPC、Issuer、两个 Verifier 与 PostgreSQL 的客户端虚拟机", "一台承载非验证 RPC、签发方、两个验证方与 PostgreSQL 的客户端虚拟机")
rep("term-verifier-213", "系统部署两个相互独立的验证方（Verifier），二者不共享进程内内存", "系统部署两个相互独立的验证方，二者不共享进程内内存")
rep("term-verifier-219b", "数据库中断期间 Verifier 保持 Fail-Closed", "数据库中断期间验证方保持 Fail-Closed")
rep("term-opid-304", "operationId 保证重复执行幂等", "操作标识（operationId）保证重复执行幂等")
rep(
    "term-policydigest-163",
    "即七元组 \\(R=(owner,policyDigest,epoch,status,policyVersion,stateVersion,updatedAtBlock)\\)；",
    "即七元组 \\(R=(owner,pd,epoch,status,policyVersion,stateVersion,updatedAtBlock)\\)，其中 \\(pd\\) 为策略摘要（policyDigest）；",
)
rep("term-policydigest-365", "资源状态记录 policyDigest，能力签发与验证都绑定该摘要", "资源状态记录策略摘要，能力签发与验证都绑定该摘要")
rep(
    "term-rc1-update-header",
    "授权语义变化通过仅更新 Header 完成，密钥与对象内容变化通过整体轮换完成",
    "授权语义变化通过仅更新密文头部完成，密钥与对象内容变化通过整体轮换完成",
)
rep("term-rc1-new-header-close", "在新 Header 闭合后恢复合法用户访问", "在新密文头部闭合后恢复合法用户访问")
rep(
    "term-headercore-267",
    "HeaderCore 的字段设计遵循“对象自描述、摘要可核验”的原则：资源标识指向链上资源，版本三元组描述 Header/Body/CK 的当前版本，Body 摘要与接收者信封分别保证对象完整性与按接收者封装；签名覆盖规范化序列化的全部字段，任何字段被修改都会导致验签失败。",
    "核心结构的字段设计遵循“对象自描述、摘要可核验”的原则：资源标识指向链上资源，版本三元组描述密文头部/密文主体/内容密钥的当前版本，密文主体摘要与接收者信封分别保证对象完整性与按接收者封装；签名覆盖规范化序列化的全部字段，任何字段被修改都会导致验签失败。",
)
rep("term-header-update-flow-306", "为撤销流程、Header 更新流程与恢复流程提供统一的状态基础", "为撤销流程、密文头部更新流程与恢复流程提供统一的状态基础")
rep(
    "term-rc3-revoke-312",
    "事件扫描与受影响资源解析生成 Header 更新意图；在 Header 闭合前，材料释放判定保持拒绝",
    "事件扫描与受影响资源解析生成密文头部更新意图；在密文头部闭合前，材料释放判定保持拒绝",
)
rep("term-rc3-old-ck-312", "不能收回此前已合法获得的明文、旧 CK 或旧密文", "不能收回此前已合法获得的明文、旧内容密钥或旧密文")
rep("term-rc3-body-345", "Body 由 64 KiB 增至 8 MiB", "密文主体由 64 KiB 增至 8 MiB")
rep("term-rc3-old-ck-345", "旧 CK 无法解密新 Body、摘要变化与版本关系全部正确", "旧内容密钥无法解密新密文主体、摘要变化与版本关系全部正确")
rep("term-rc3-351-sp", "隔离副本 从隔离副本恢复", "隔离副本从隔离副本恢复")
rep("term-rc3-header-close-351a", "撤销后的 未闭合窗口与 Header 闭合两条路径", "撤销后的未闭合窗口与密文头部闭合两条路径")
rep("term-rc3-header-close-351b", "Header 闭合后 5 次均为允许", "密文头部闭合后 5 次均为允许")
rep("term-rc3-365a", "成为研究内容三判断材料释放、Header 更新与撤销闭环的可信输入", "成为研究内容三判断材料释放、密文头部更新与撤销闭环的可信输入")
rep("term-rc3-365b", "撤销事件驱动 Header 更新意图", "撤销事件驱动密文头部更新意图")
rep("term-rc3-365c", "（撤销、Header 闭合、密钥轮换）", "（撤销、密文头部闭合、密钥轮换）")
rep("term-rc3-367", "授权状态变化触发 Header 更新与材料释放判定切换", "授权状态变化触发密文头部更新与材料释放判定切换")
rep("term-rc3-369", "Header 版本与对象摘要由链上注册表登记", "密文头部版本与对象摘要由链上注册合约登记")

# --- M6 leftover duplicated labels / stray spaces -----------------------------
rep("dup-rc1-redundancy", "冗余度实验 冗余度实验表明", "冗余度实验表明")
rep("dup-rc1-boundary", "边界策略实验 边界实验覆盖", "边界策略实验覆盖")

# --- stage results (real status) -----------------------------------------------
rep(
    "stage-results",
    """[1] 王威, 夏琦, 高建彬, 夏虎. 基于许可联盟链状态锚定与共享 Nonce 的授权执行方法[J]. 软件学报（论文初稿已完成，拟投稿）.
[2] 王威, 高建彬, 王鹏. 一种非连续时间访问策略的确定性编译方法及系统: 中国, [P].（专利撰写中，拟申请）.
[3] 王威, 高建彬, 王鹏. 一种链上可信授权与版本化密文对象管理方法及系统: 中国, [P].（专利撰写中，拟申请）.
另：三套可复现原型与冻结实验数据集（时间策略编译、许可链授权执行、版本化密文头部与撤销恢复）。""",
    """[1] 阶段性学术论文：《基于许可联盟链状态锚定与共享 Nonce 的授权执行方法》。论文初稿已完成，拟投稿《软件学报》。
[2] 拟申请发明专利：《一种非连续时间访问策略的确定性编译方法及系统》。专利文本撰写中。
[3] 拟申请发明专利：《一种链上可信授权与版本化密文对象管理方法及系统》。专利文本撰写中。
另：三套可复现原型与冻结实验数据集（时间策略编译、许可链授权执行、版本化密文头部与撤销恢复）。""",
)

# --- problem 2 wording ---------------------------------------------------------
rep(
    "problem2-458",
    "实验方面，缓存与层次覆盖的协议级收益、批量密文头更新与更多验证实例的一致性表现尚未在更大规模下验证，现有结论的适用范围需要随证据边界如实表述。",
    "实验方面，将根据学位论文整体论证需要，在不改变当前冻结实验结论的前提下开展必要的针对性补充验证；若某项扩展不构成核心主张所必需的证据，则将其作为研究局限或后续工作进行讨论，现有结论的适用范围随证据边界如实表述。",
)
rep(
    "problem2-470",
    "实验方面按预注册设计补充协议级收益与规模扩展实验，每项扩展先明确假设与指标再执行，无法完成的扩展如实列入论文局限与未来工作。",
    "实验方面根据学位论文整体论证需要，在不改变当前冻结实验结论的前提下开展必要的针对性补充验证；每项扩展先明确假设与指标再执行，无法完成的扩展如实列入论文局限与未来工作。",
)
rep(
    "problem2-476",
    "按需补充针对性扩展实验（缓存协议收益、批量 Header 更新、更多 Verifier 一致性等）；完成全文图表、公式与参考文献规范化",
    "按需开展不改变冻结实验结论的针对性补充验证；完成全文图表、公式与参考文献规范化",
)


# ---------------------------------------------------------------------------
# Citation renumbering
# ---------------------------------------------------------------------------
TOKEN_RE = re.compile(r"\[\d+(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*\]")
PLACEHOLDER_RE = re.compile(r"\[«([A-Z]+)»\]")


def _expand(tok: str) -> list[int]:
    nums: list[int] = []
    for part in tok[1:-1].replace(" ", "").split(","):
        if "-" in part:
            a, b = part.split("-")
            nums.extend(range(int(a), int(b) + 1))
        else:
            nums.append(int(part))
    return nums


def _compress(nums: list[int]) -> str:
    nums = sorted(set(nums))
    parts: list[str] = []
    start = prev = nums[0]
    for n in nums[1:]:
        if n == prev + 1:
            prev = n
            continue
        parts.append(str(start) if start == prev else f"{start}-{prev}")
        start = prev = n
    parts.append(str(start) if start == prev else f"{start}-{prev}")
    return "[" + ",".join(parts) + "]"


def renumber(text: str) -> tuple[str, dict[str, int]]:
    """Assign final numbers by first-citation order and rewrite all tokens."""
    order: list[str] = []  # first-occurrence sequence of keys
    seen: set[str] = set()
    events: list[tuple[int, int, re.Match]] = []
    for m in TOKEN_RE.finditer(text):
        events.append((m.start(), 0, m))
    for m in PLACEHOLDER_RE.finditer(text):
        events.append((m.start(), 1, m))
    events.sort(key=lambda e: (e[0], e[1]))
    for _, kind, m in events:
        if kind == 0:
            for n in _expand(m.group(0)):
                key = f"old:{n}"
                if key not in seen:
                    seen.add(key)
                    order.append(key)
        else:
            key = f"new:{m.group(1)}"
            if key not in seen:
                seen.add(key)
                order.append(key)
    mapping = {key: i + 1 for i, key in enumerate(order)}

    def _repl(m: re.Match) -> str:
        old_nums = _expand(m.group(0))
        new_nums = [mapping[f"old:{n}"] for n in old_nums]
        return _compress(new_nums)

    out = TOKEN_RE.sub(_repl, text)
    out = PLACEHOLDER_RE.sub(lambda m: f"[{mapping[f'new:{m.group(1)}']}]", out)
    return out, mapping


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    text = M6.read_text(encoding="utf-8")
    applied: list[str] = []
    for key, old, new, count in REPLACEMENTS:
        if count == -1:
            if old in text:
                text = text.replace(old, new)
                applied.append(f"{key} (all)")
            else:
                applied.append(f"{key} (already absent)")
        else:
            found = text.count(old)
            if found < count:
                raise SystemExit(
                    f"REPLACEMENT FAILED: {key}: expected >= {count}, found {found}\n"
                    f"old={old[:100]!r}"
                )
            text = text.replace(old, new, count)
            applied.append(f"{key} (x{count})")

    # split: renumber only the body (before the reference list); keep the
    # reference list fixed and the stage-results/problem sections untouched.
    start = text.find("### 参考文献")
    end = text.find("### 4．阶段性研究成果")
    if start < 0 or end < 0:
        raise SystemExit("reference list anchors not found")
    body = text[:start]
    tail = text[end:]
    body, mapping = renumber(body)
    text = body + REF_LIST + tail

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print("applied replacements:")
    for a in applied:
        print("  ", a)
    print("citation mapping:", json_dumps(mapping))
    print("wrote:", OUT)


def json_dumps(d: dict) -> str:
    import json

    return json.dumps(d, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
