# -*- coding: utf-8 -*-
"""M3: transform the M2 draft into the M3 source (3+3 problems, citations, equations, algorithms, references)."""
from __future__ import annotations

import io
import json
import re
from pathlib import Path


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
M2 = ROOT / "docs/midterm-report/m2/MIDTERM-REPORT-M2-FULL-DRAFT.md"
OUT = ROOT / "docs/midterm-report/m3"
SRC = OUT / "M3-MIDTERM-SOURCE.md"


REFS = [
    "Bertino E, Bonatti P A, Ferrari E. TRBAC: A temporal role-based access control model[J]. ACM Transactions on Information and System Security, 2001, 4(3): 191-233.",
    "Abiteboul S, Manolescu I, Polyzotis N, et al. XML processing in DHT networks[C]//Proceedings of the 24th International Conference on Data Engineering (ICDE). IEEE, 2008: 606-615.",
    "Rundgren A, Jordan B, Erdtman S. JSON canonicalization scheme (JCS)[S]. RFC 8785, 2020.",
    "Claessen K, Hughes J. QuickCheck: A lightweight tool for random testing of Haskell programs[C]//Proceedings of ICFP 2000. ACM, 2000: 268-279.",
    "Saltzer J H, Schroeder M D. The protection of information in computer systems[J]. Proceedings of the IEEE, 1975, 63(9): 1278-1308.",
    "Hyperledger Besu Documentation. QBFT consensus protocol[EB/OL]. [2026-08-02]. https://besu.hyperledger.org/private-networks/how-to/configure/consensus/qbft.",
    "PostgreSQL Global Development Group. PostgreSQL 16 documentation: INSERT[EB/OL]. [2026-08-02]. https://www.postgresql.org/docs/16/sql-insert.html.",
    "Josefsson S, Liusvaara I. Edwards-Curve digital signature algorithm (EdDSA)[S]. RFC 8032, 2017.",
    "Efron B. Bootstrap methods: Another look at the jackknife[J]. The Annals of Statistics, 1979, 7(1): 1-26.",
    "Barnes R, Bhargavan K, Lipp B, et al. Hybrid public key encryption[S]. RFC 9180, 2022.",
    "Hardt D. The OAuth 2.0 authorization framework[S]. RFC 6749, 2012.",
    "Jones M, Bradley J, Sakimura N. JSON Web Token (JWT)[S]. RFC 7519, 2015.",
    "Dennis J B, Van Horn E C. Programming semantics for multiprogrammed computations[J]. Communications of the ACM, 1966, 9(3): 143-155.",
    "Benet J. IPFS - Content addressed, versioned, P2P file system[EB/OL]. arXiv:1407.3561, 2014[2026-08-02]. https://arxiv.org/abs/1407.3561.",
    "Bethencourt J, Sahai A, Waters B. Ciphertext-policy attribute-based encryption[C]//Proceedings of the 2007 IEEE Symposium on Security and Privacy. IEEE, 2007: 321-334.",
    "Rouhani S, Belchior R, Cruz R S, et al. Distributed attribute-based access control system using permissioned blockchain[J]. World Wide Web, 2021, 24(5): 1617-1644.",
    "Sandhu R S, Coyne E J, Feinstein H L, et al. Role-based access control models[J]. IEEE Computer, 1996, 29(2): 38-47.",
    "Sahai A, Waters B. Fuzzy identity-based encryption[C]//EUROCRYPT 2005. Springer, 2005: 457-473.",
    "Goyal V, Pandey O, Sahai A, et al. Attribute-based encryption for fine-grained access control of encrypted data[C]//Proceedings of the 13th ACM Conference on Computer and Communications Security. ACM, 2006: 89-98.",
    "Boldyreva A, Goyal V, Kumar V. Identity-based encryption with efficient revocation[C]//Proceedings of the 15th ACM Conference on Computer and Communications Security. ACM, 2008: 417-426.",
    "Nakamoto S. Bitcoin: A peer-to-peer electronic cash system[EB/OL]. 2008. https://bitcoin.org/bitcoin.pdf.",
    "Wood G. Ethereum: A secure decentralised generalised transaction ledger[EB/OL]. Ethereum Project Yellow Paper, 2014. https://ethereum.github.io/yellowpaper/paper.pdf.",
    "Androulaki E, Barger A, Bortnikov V, et al. Hyperledger Fabric: A distributed operating system for permissioned blockchains[C]//Proceedings of the 13th EuroSys Conference. ACM, 2018: 30.",
    "Maesa D D F, Mori P, Ricci L. Blockchain based access control[C]//IFIP International Conference on Distributed Applications and Interoperable Systems. Springer, 2017: 206-220.",
    "Dworkin M. Recommendation for block cipher modes of operation: Galois/Counter Mode (GCM) and GMAC[S]. NIST Special Publication 800-38D, 2007.",
    "Miller M S, Yee K, Shapiro J. Capability myths demolished[R]. Technical Report SRL2003-02, Johns Hopkins University, 2003.",
    "Lamport L. Time, clocks, and the ordering of events in a distributed system[J]. Communications of the ACM, 1978, 21(7): 558-565.",
    "Lampson B W. Protection[J]. ACM SIGOPS Operating Systems Review, 1974, 8(1): 18-24.",
    "Gray J. The transaction concept: Virtues and limitations[C]//Proceedings of the 7th International Conference on Very Large Data Bases. 1981: 144-154.",
]


# citation insertions: (anchor, refs list) — insert "[n]" after the anchor phrase.
# Anchors below use the EXACT text present in the M2 source.
CITATIONS = [
    ("为多方环境下的状态一致性与责任审计提供了天然的技术基础", [21, 22, 23]),
    ("围绕同一份公开账本达成对授权状态的一致认知", [21, 22]),
    ("区块链相关数据共享方案近年来得到广泛研究", [16, 24]),
    ("角色与时间约束模型能够表达周期性角色启停等时间语义", [1, 17]),
    ("属性基加密能够按属性实施细粒度访问控制", [15, 18, 19]),
    ("用户撤销、资源暂停、策略更新与密钥轮换都会改变当前请求是否仍然有效", [20]),
    ("普通令牌的有效性取决于签发时点的快照", [11, 12]),
    ("难以在验证时点约束动态状态与跨实例重放", [11, 12]),
    ("只有验证时点的链上状态才能反映当前是否仍然有效", [27]),
    ("仅依靠传统数据库的访问控制列表或应用层权限校验", [5, 13, 26, 28]),
    ("以规范区间序列作为唯一语义表示", [2]),
    ("以固定宽度规范编码与摘要计算把唯一语义固化", [3]),
    ("阶段验证覆盖形式化模型、算法实现、性质测试与 15120 条正式记录", [4]),
    ("每组比较含 2430 对运行块，并执行 10000 次运行级 Bootstrap", [9]),
    ("使用 Ed25519 签名，将链标识、合约地址、策略摘要、epoch", [8]),
    ("研究采用 Besu QBFT 共识部署真实链环境", [6]),
    ("通过单条 `INSERT ... ON CONFLICT DO NOTHING RETURNING 1` 事务完成原子消费", [7, 29]),
    ("内容密钥 CK 按接收者使用 HPKE（X25519 + HKDF-SHA256 + AES-128-GCM）封装", [10]),
    ("Body 为分块 AES-256-GCM 密文，承载文件主体", [25]),
    ("SHA-256 内容寻址为完整性权威", [14]),
    ("本研究选择许可联盟链作为授权状态的锚点与审计事实源", [23, 6]),
]


EQUATIONS = [
    ("真实时间域", r"\mathcal{D}=[t_0,t_0+U\Delta),"),
    ("基本 Epoch 映射", r"\phi(t)=\lfloor\frac{t-t_0}{\Delta}\rfloor."),
    ("离散时间域", r"T=\{0,1,\ldots,U-1\}."),
    ("允许槽集合", r"S(P)=\bigcup_{i=1}^{n}\{x\in T\mid l_i\le x<r_i\}."),
    ("唯一语义表示", r"I^*=\operatorname{Normalize}(P)=\langle[a_1,b_1),\ldots,[a_k,b_k)\rangle."),
    ("层次覆盖根区间", r"L=2^{\lceil\log_2 U\rceil}."),
    ("二进制对齐节点", r"D(j,s)=[j2^s,(j+1)2^s)."),
    ("全策略覆盖", r"C(P)=\bigcup_{I\in I^*}C(I),\qquad c=|C(P)|."),
    ("规范字节串", r"B(P)=\operatorname{CanonicalSerialize}(t_0,\Delta,U,I^*)."),
    ("策略摘要", r"pd=\operatorname{SHA256}(B(P))."),
    ("编译复杂度", r"T(n,c)=O(n\log n+c)."),
    ("资源状态", r"R=(owner,policyDigest,epoch,status,policyVersion,stateVersion,updatedAtBlock)."),
    ("用户状态", r"U=(account,userKeyId,status,userVersion,updatedAtBlock)."),
    ("能力编码", r"B=\operatorname{Encode}_{CAP2}(F_1\Vert F_2\Vert\cdots\Vert F_n)."),
    ("能力签名", r"\sigma=\operatorname{Ed25519.Sign}(sk_I,B)."),
    ("一次性消费条件", r"\text{INSERT }(k)\text{ returns 1 }\Leftrightarrow k\notin consumed, \quad k=(chain,contract,resource,epoch,nonce)."),
    ("版本单调约束", r"stateVersion'=stateVersion+1 \ \wedge\ REVOKED \text{ 为终态}."),
    ("Fail-Closed 判定", r"\text{release}\Rightarrow status=ACTIVE \wedge \text{dbAvailable}."),
    ("V1 密钥版本关系", r"keyVersion=bodyVersion."),
    ("HEADER_ONLY 状态变换", r"(h,b,k)\mapsto(h+1,b,k)."),
    ("BODY_ROTATION 状态变换", r"(h,b,k)\mapsto(h+1,b+1,k+1)."),
    ("Body 加密关系", r"C_{body}=\operatorname{AES-256-GCM}(K,N,M)."),
    ("HPKE 封装关系", r"EK_{R}=\operatorname{HPKE.Seal}(pk_R, CK)."),
    ("Header 摘要绑定", r"hdrHash=\operatorname{SHA256}(\operatorname{Canonical}(Header)),\quad HeaderRegistry\gets(hdrHash,objHash)."),
    ("材料释放条件", r"\text{release iff } status=ACTIVE \wedge t\in S(I^*) \wedge hdrValid."),
    ("恢复一致性条件", r"\text{restore iff } \operatorname{SHA256}(candidate)=objHash \wedge structuralValid."),
]


ALGORITHMS = [
    ("算法1 非连续时间策略规范化", "算法1 非连续时间策略规范化（Normalize）\n输入：已离散化区间序列 P\n输出：规范区间序列 I*\n1: 按 (left,right) 对区间排序\n2: 线性扫描：与当前分量相交或相邻则合并，否则开始新分量\n3: 返回有序、互斥、互不相邻的 I*"),
    ("算法2 Dyadic 层次覆盖生成", "算法2 Dyadic 层次覆盖生成（Cover）\n输入：规范区间 I=[l,r)，槽总数 U\n输出：最大对齐覆盖节点集合\n1: WHILE l<r DO\n2:   size ← 当前位置最大可用 2 的幂对齐块\n3:   WHILE size>r-l DO size ← size>>1\n4:   输出 (l,size)；l ← l+size\n5: END WHILE"),
    ("算法3 确定性策略编译与摘要", "算法3 确定性策略编译与摘要生成（PolicyCompile）\n输入：时区起点 t0、粒度 Δ、槽总数 U、区间序列 P\n输出：I*、C、B、pd\n1: 校验输入约束；2: I*←Normalize(P)；3: C←Cover(I*)；4: B←NTP1Serialize；5: pd←SHA256(B)"),
    ("算法4 CAP2 能力签发", "算法4 CAP2 能力签发（Issue）\n输入：授权请求、链上状态\n输出：签名能力 CAP2\n1: 读取资源/用户确认状态，校验 ACTIVE 与策略摘要\n2: 校验 SHA256(pubkey)=userKeyId 且时间落入策略窗口\n3: 生成 nonce 与有效期；签名前再次读取状态\n4: 两次快照一致则规范化编码并 Ed25519 签名"),
    ("算法5 CAP2 验证与共享 Nonce 消费", "算法5 CAP2 验证与共享 Nonce 消费（Verify）\n输入：CAP2、请求上下文\n输出：ACCEPT 或拒绝码\n1: 解析与验签；2: 读取确认链状态；3: 逐项绑定复核；4: 重执行时间策略；5: 原子消费 Nonce；6: 全部通过返回 ACCEPT"),
    ("算法6 HEADER_ONLY 更新流程", "算法6 HEADER_ONLY 更新流程\n输入：受影响资源、撤销/授权语义变化\n输出：新 Header 与链上登记\n1: 解析受影响资源并生成 Header 更新意图\n2: 新 Header 的 headerVersion←h+1，body/key 版本不变\n3: JCS 序列化、Ed25519 签名、登记 HeaderRegistry\n4: Header 进入 current 后恢复材料释放"),
    ("算法7 BODY_ROTATION 流程", "算法7 BODY_ROTATION 流程\n输入：需要轮换的密文对象\n输出：新 Body、新 CK、新 Header\n1: 生成新内容密钥 CK'；2: 使用 CK' 分块加密新 Body；\n3: 为接收者生成新 EncryptedCKRecord（HPKE）；\n4: 构造新 Header，(h,b,k)←(h+1,b+1,k+1)；签名并登记"),
    ("算法8 RecoveryCoordinator 故障恢复", "算法8 RecoveryCoordinator 故障恢复\n输入：候选对象（本地或副本）、期望摘要 objHash\n输出：一致对象或 FAIL_CLOSED\n1: 读取候选对象；2: SHA256 摘要验证；3: 结构验证；4: 原子恢复；5: 记录修复来源与数量；6: 返回一致或 FAIL_CLOSED"),
]


FIGURE_ANCHORS = [
    ("以三个问题的完整闭环作为总体目标", None,
     "[方法图：图1 论文总体技术路线与三项研究内容递进关系]"),
    ("算法层面，确定性编译流程由算法1给出整体组织", None,
     "[方法图：图2 非连续时间策略确定性编译流程]"),
    ("本文明确区分两种表示的职责", None,
     "[方法图：图3 语义主表示—摘要—派生执行IR关系]"),
    ("研究采用 Besu QBFT 共识部署真实链环境", None,
     "[方法图：图7 许可联盟链可信授权系统总体架构]"),
    ("验证顺序在实现中被冻结并完整执行", None,
     "[方法图：图8 CAP2 签发与验证双泳道流程]"),
    ("密文对象由 Header 与 Body 两部分构成", None,
     "[方法图：图15 版本化密文对象结构（Header/Body/CK）]"),
    ("链下对象层由 LocalObjectStore 与隔离的 Kubo 副本组成", None,
     "[方法图：图16 链上可信状态—控制协调—链下密文对象三层闭环架构]"),
]


NEW_PROBLEMS = (
    "总体来看，当前研究已经形成“策略表示—可信授权执行—密文生命周期治理”的基本技术闭环，三项研究内容的核心算法与原型实验均已达到阶段性完成状态，但与开题阶段设定的完整研究目标相比，仍存在以下三个需要进一步解决的问题。\n\n"
    "（1）论文的理论抽象与学术表达仍需深化。三项研究内容分别形成了较为完整的方法与实验结果，但作为学位论文整体，需要把接口关系、安全假设与结论边界整理为连续、自洽的学术论证，从工程原型中抽象出清晰的研究问题、形式化模型与证据链；同时，研究内容二的安全属性与故障模型、研究内容三的版本一致性论证仍以实验验证为主，尚未形成完整的端到端形式化归约，论文中需要明确区分实验验证与形式化证明，避免对安全性质作过强概括。\n\n"
    "（2）相关工作与创新边界的覆盖仍需补强。本阶段已完成 29 篇参考文献的真实性核验，但近五年许可链授权状态管理、跨链令牌绑定、版本化密文与前瞻性撤销、事务恢复等主题的更广泛综述仍需补充；与属性基加密、门限解密、普通令牌授权等数据共享路线的系统对比尚未在论文中完整展开，需要进一步说明本文方案与既有路线的边界，使每一处创新性表述都建立在证据与文献对照之上，避免超出支持范围。\n\n"
    "（3）实验规模与外部有效性受限。研究内容二的正式实验运行于共享物理主机的虚拟机之上，单台虚拟机的精确 vCPU 与内存配额未形成独立清单；研究内容三的正式实验在受控单节点环境中完成，单节点 QBFT 无法反映多 Validator 共识影响，故障类别与 Body 规模范围有限；缓存与层次覆盖的协议级收益、批量密文头更新与更多 Verifier 实例的一致性表现尚未在更大规模下验证。论文写作需要把机制结论与数值结论分开表述，如实保留适用范围限定。\n\n"
    "需要说明的是，上述问题均属于“完成度已高、边界待明确”的范畴：三项研究内容的核心机制均已实现并经过正式实验验证，剩余工作以论文整合、边界表述与针对性扩展为主，符合中期考评对“技术路线基本闭合、后续转向整合与深化”的定位。\n\n"
)


NEW_SOLUTIONS = (
    "针对上述问题，后续将围绕理论抽象与学术表达、相关工作与创新边界、实验规模与外部有效性三条主线继续推进，每个问题均有对应的解决办法与可验证的完成标准。\n\n"
    "（1）针对理论抽象与学术表达问题，将按照“统一语义—授权执行—密文生命周期”的主线重构论文论证结构，统一符号与术语，把接口关系、安全假设与结论边界整理为可引用的命题形式；理论层面补充研究内容二的安全属性说明与研究内容三的版本一致性论证，严格区分实验验证与形式化证明。验证方式为逐章对照审稿检查表；完成标准是论文各章接口一致、术语统一、边界表述与冻结证据一致。\n\n"
    "（2）针对相关工作与创新边界问题，将基于已核验的 29 篇文献补充近五年相关主题综述，以对比表整理各路线在时间语义表达、状态锚定、重放控制、撤销传导与恢复能力上的差异，对每一处创新性表述建立证据对照；新增文献按学校要求经真实来源核验后引入。验证方式为文献来源抽查与创新表述逐句对照；完成标准是相关工作覆盖充分、创新边界与证据一致。\n\n"
    "（3）针对实验规模与外部有效性问题，将如实保留现有结论的适用范围表述，把机制结论与数值结论分开；在条件允许时补充独立物理集群或多节点规模验证实验、批量密文头更新压力实验与更多 Verifier 一致性实验，每项实验先明确假设与指标再执行；无法完成的扩展明确列为论文局限与未来工作。验证方式为实验设计预注册与结果复现检查；完成标准是每项扩展有明确假设、设计、结果与边界。\n\n"
    "上述解决办法与三个问题一一对应。在时间安排上，论文整合与理论深化优先于扩展实验，扩展实验仅在条件允许且对结论有实质补充时执行；所有结论均以冻结环境与预注册设计为边界。\n\n"
)


def main() -> None:
    text = io.open(M2, encoding="utf-8").read()
    text = text.replace("# 专业学位研究生学位论文中期考评表（M2 完整候选稿）",
                        "# 专业学位研究生学位论文中期考评表（M3 精细重构候选稿）")
    # 0. strip old M2 figure / algorithm markers first
    text = re.sub(r"\[图：[^\]]*\]", "", text)
    text = re.sub(r"\[算法：[^\]]*\]", "", text)

    # 1. citation insertions (by anchor)
    inserted = 0
    for anchor, refs in CITATIONS:
        if anchor in text:
            marker = "".join(f"[{r}]" for r in refs)
            text = text.replace(anchor, anchor + marker, 1)
            inserted += 1

    # 2. equation insertions: insert the display marker at the END of the
    #    paragraph that contains the anchor, so inline-LaTeX anchors are not
    #    corrupted. Insert from the end of the document backwards.
    eq_anchors = [
        ("设系统研究的真实时间域为", 0),
        ("其中 \(t_0\) 为可转换为 UTC 的时区感知起点", 1),
        ("任意真实时间点通过取整映射到槽坐标", 2),
        ("策略以半开区间", 3),
        ("它是允许槽集合的极大连续分量分解", 4),
        ("以二进制对齐节点（起点可被长度整除、长度为 2 的幂的半开区间）", 5),
        ("算法从左至右为每个未覆盖左端点选择当前位置可用的最大对齐块", 6),
        ("覆盖的节点总数记为", 7),
        ("规范字节串由固定头部与区间列表组成", 8),
        ("策略摘要定义为", 9),
        ("整体编译复杂度为", 10),
        ("资源状态记录所有者", 11),
        ("用户状态记录账户", 12),
        ("CAP2 以规范化字节序列为输入", 13),
        ("使用 Ed25519 签名，将链标识、合约地址、策略摘要、epoch", 14),
        ("以 (chain_id, contract_address, resource_id, epoch, nonce) 为消费唯一键", 15),
        ("版本字段构成状态快照的基础", 16),
        ("当 RPC 或数据库不可用时", 17),
        ("V1 冻结语义为 keyVersion 等于 bodyVersion", 18),
        ("HEADER_ONLY 表示仅更新 Header（heade", 19),
        ("BODY_ROTATION 表示整体轮换（headerVersion、bodyVersion、keyVersion 均加 1", 20),
        ("Body 为分块 AES-256-GCM 密文", 21),
        ("内容密钥 CK 按接收者使用 HPKE", 22),
        ("Header 使用 JCS 规范序列化", 23),
        ("材料释放判定由 AccessMaterialReleaseGuard", 24),
        ("恢复由 RecoveryCoordinator 协调", 25),
    ]

    def para_end(text: str, pos: int) -> int:
        """End of the paragraph (double newline) containing pos."""
        nl = text.find("\n\n", pos)
        return nl if nl >= 0 else len(text)

    inserts = []
    eq_count = 0
    for anchor, eq_pos in eq_anchors:
        if anchor in text and eq_pos < len(EQUATIONS):
            idx = text.find(anchor)
            end = para_end(text, idx)
            latex = EQUATIONS[eq_pos][1]
            inserts.append((end, f"\n\n[公式：{latex}]\n"))
            eq_count += 1
        else:
            import sys as _sys
            print("EQ SKIPPED:", anchor[:24], "eq_pos:", eq_pos,
                  "in_text:", anchor in text, "has_eq:", eq_pos < len(EQUATIONS),
                  file=_sys.stderr)
    for pos, marker in sorted(inserts, key=lambda x: x[0], reverse=True):
        text = text[:pos] + marker + text[pos:]
    import sys as _sys
    print("EQ_INSERTS:", [m[:24] for _, m in sorted(inserts, key=lambda x: x[0])], file=_sys.stderr)

    # 3. method figure markers (insert at paragraph end, backwards)
    fig_inserts = []
    fig_count = 0
    for anchor, _, marker in FIGURE_ANCHORS:
        if anchor in text:
            idx = text.find(anchor)
            end = para_end(text, idx)
            fig_inserts.append((end, f"\n\n{marker}\n"))
            fig_count += 1
    for pos, marker in sorted(fig_inserts, key=lambda x: x[0], reverse=True):
        text = text[:pos] + marker + text[pos:]

    # 4. algorithm insertions (insert at paragraph end, backwards)
    algo_anchors = [
        ("规范化过程（Normalize）首先按区间左端点排序", "算法1 非连续时间策略规范化"),
        ("算法从左至右为每个未覆盖左端点选择当前位置可用的最大对齐块", "算法2 Dyadic 层次覆盖生成"),
        ("确定性编译流程由算法1给出整体组织", "算法3 确定性策略编译与摘要"),
        ("能力签发流程由 Issuer 执行", "算法4 CAP2 能力签发"),
        ("验证流程由 Verifier 执行", "算法5 CAP2 验证与共享 Nonce 消费"),
        ("HEADER_ONLY 用于授权语义变化", "算法6 HEADER_ONLY 更新流程"),
        ("BODY_ROTATION 用于更换密文对象与密钥", "算法7 BODY_ROTATION 流程"),
        ("恢复由 RecoveryCoordinator 协调", "算法8 RecoveryCoordinator 故障恢复"),
    ]
    algo_inserts = []
    algo_count = 0
    for anchor, name in algo_anchors:
        if anchor in text:
            entry = next((x for x in ALGORITHMS if x[0].startswith(name.split(" ")[0])), None)
            if entry is None:
                continue
            idx = text.find(anchor)
            end = para_end(text, idx)
            algo_inserts.append((end, f"\n\n[算法框：{entry[1]}]\n"))
            algo_count += 1
    for pos, marker in sorted(algo_inserts, key=lambda x: x[0], reverse=True):
        text = text[:pos] + marker + text[pos:]

    # 4b. experiment design table (replaces the removed factor-pairing figure)
    d_anchor = "实验共覆盖 108 个因素配置、324 个含 seed 配置、9720 个运行块、77760 条请求记录与 233280 条链读取记录"
    if d_anchor in text:
        idx = text.find(d_anchor)
        end = para_end(text, idx)
        text = text[:end] + "\n\n[表：正式实验因素设计汇总（因素/水平/配置/重复/请求与链读取规模）]\n" + text[end:]

    # 4c. experiment figure markers (re-inserted at frozen-result anchors)
    exp_fig_anchors = [
        ("查询性能方面，E1-A 中槽枚举、规范区间列表与层次覆盖的查询中位数的中位数", "图4 匹配查询中位时延（E1-A 正式实验结果）"),
        ("从规模数据看，E1-A 样本逻辑字节中位数分别为", "图5 三种表示的逻辑规模比较（E1-A 正式实验结果）"),
        ("E1-C 边界实验覆盖偶数槽、奇数槽、随机孤立点、最大碎片、全域与近全域等八类边界策略", "图6 表示的压缩比与适用边界（E1-A 正式实验结果）"),
        ("并发 50、100 与 500 个相同能力请求", "图9 并发度对端到端时延的影响（RC2）"),
        ("四种方法复用相同语义策略与查询集合", "图10 四种方法的运行级端到端时延分布（RC2 正式实验结果）"),
        ("缓存命中按单请求直接记录", "图11 请求局部性与缓存的影响（RC2）"),
        ("逐请求链读取占端到端时延的", "图12 端到端时延的阶段占比（RC2 中位数）"),
        ("置信区间跨越 0", "图13 自然配对比较与运行级 Bootstrap 置信区间（RC2）"),
        ("碎片率对局部匹配的影响", "图14 碎片率对匹配时延的影响（RC2）"),
        ("端到端时延中位数分别为", "图17/图18 注释"),
        ("恢复端到端时延中位数约 3.1～3.2 s", "图19 LOCAL_ONLY 与 KUBO_REPLICA 恢复时延对比（RC3 E5）"),
    ]
    exp_inserts = []
    for anchor, marker in exp_fig_anchors:
        if anchor in text:
            idx = text.find(anchor)
            end = para_end(text, idx)
            if marker == "图17/图18 注释":
                exp_inserts.append((end, "\n\n[方法图：图17 HEADER_ONLY 操作端到端时延（RC3 正式实验结果）]\n\n[方法图：图18 BODY_ROTATION 操作端到端时延（RC3 正式实验结果）]\n"))
            else:
                exp_inserts.append((end, f"\n\n[方法图：{marker}]\n"))
    # merge inserts sharing the same end position, preserving source order
    merged = {}
    for pos, marker in exp_inserts:
        merged[pos] = merged.get(pos, "") + marker
    for pos, marker in sorted(merged.items(), key=lambda x: x[0], reverse=True):
        text = text[:pos] + marker + text[pos:]

    # 4d. compact the progress-overview markdown table (5 wide cols -> 3 cols)
    old_table = (
        "| 研究内容 | 主要任务 | 当前状态 | 已有证据 | 后续工作 |\n"
        "|---|---|---|---|---|\n"
        "| 研究内容一 | 非连续时间策略确定性表示与编译 | 核心方法与正式实验已完成 | 形式化模型、算法1/2、81 项测试、98.61% 覆盖率、168 样本、15120 条有效记录 | 论文级凝练与适用边界表述 |\n"
        "| 研究内容二 | 许可联盟链可信授权执行 | 原型与正式实验已完成 | 五节点链、AuthorizationState、CAP2、共享 Nonce、9720 运行块、链读取占比 98.66%～98.80% | 缓存与层次接口的协议级讨论 |\n"
        "| 研究内容三 | 版本化密文头部与前瞻性撤销 | 原型与正式实验已完成 | 版本协议、任务状态机、恢复协调、145 个有效运行、错误材料释放 0 | 多节点扩展与批量更新压力 |\n"
        "| 论文整体 | 全文整合与定稿 | 章节草稿已形成 | 三项内容证据链与审计材料 | 相关工作完善、理论深化、定稿 |"
    )
    new_table = (
        "| 研究内容 | 当前状态 | 主要证据 |\n"
        "|---|---|---|\n"
        "| 研究内容一（策略确定性表示与编译） | 核心方法与正式实验已完成 | 形式化模型、算法1/2、81 项测试、98.61% 覆盖率、168 样本、15120 条有效记录；后续为论文级凝练与适用边界表述 |\n"
        "| 研究内容二（许可链可信授权执行） | 原型与正式实验已完成 | 五节点链、AuthorizationState、CAP2、共享 Nonce、9720 运行块、链读取占比 98.66%～98.80%；后续为缓存与层次接口的协议级讨论 |\n"
        "| 研究内容三（版本化密文头部与前瞻性撤销） | 原型与正式实验已完成 | 版本协议、任务状态机、恢复协调、145 个有效运行、错误材料释放 0；后续为多节点扩展与批量更新压力 |\n"
        "| 论文整体（全文整合与定稿） | 章节草稿已形成 | 三项内容证据链与审计材料；后续为相关工作完善、理论深化、定稿 |"
    )
    if old_table in text:
        text = text.replace(old_table, new_table, 1)

    # 5. problems/solutions 3+3: replace the section content
    p_start = text.find("总体来看，当前研究已经形成")
    p_end = text.find("从计划管理角度看")
    new_problems = NEW_PROBLEMS
    text = text[:p_start] + new_problems + text[p_end:]
    # replace solutions (4->3)
    s_start = text.find("针对上述问题，后续将围绕")
    s_end = text.find("下一步具体研究计划（时间以实际中期考评与毕业安排为准）")
    new_solutions = NEW_SOLUTIONS
    text = text[:s_start] + new_solutions + text[s_end:]
    # 6. append reference list before "### 4．阶段性研究成果"
    ref_sec = "### 参考文献\n\n"
    ref_sec += "\n\n".join(f"[{i+1}] {r}" for i, r in enumerate(REFS)) + "\n\n"
    idx4 = text.find("### 4．阶段性研究成果")
    text = text[:idx4] + ref_sec + text[idx4:]
    OUT.mkdir(parents=True, exist_ok=True)
    io.open(SRC, "w", encoding="utf-8").write(text)
    print(json.dumps({"citationsInserted": inserted, "citationsTotal": len(CITATIONS),
                      "equations": eq_count, "equationsTotal": len(EQUATIONS),
                      "methodFigs": fig_count, "methodFigsTotal": len(FIGURE_ANCHORS),
                      "algorithms": algo_count, "algorithmsTotal": len(ALGORITHMS),
                      "refs": len(REFS), "srcChars": len(text)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
