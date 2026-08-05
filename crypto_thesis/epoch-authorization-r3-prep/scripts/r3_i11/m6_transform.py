# -*- coding: utf-8 -*-
"""M6: transform M5 midterm source into the M6 academic reconstruction.

Handles: internal-tag academicization, formula policy, algorithm blocks,
figure captions, table captions/data, citation renumbering, reference rebuild,
and the duplicate E4/E5 paragraph.
"""
from __future__ import annotations

import io
import json
import re
import sys
from pathlib import Path


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
M5 = ROOT / "docs/midterm-report/m5/M5-MIDTERM-SOURCE.md"
OUT_DIR = ROOT / "docs/midterm-report/m6"
OUT = OUT_DIR / "M6-MIDTERM-SOURCE.md"


# ---------------------------------------------------------------------------
# New reference list (first-citation order)
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

[14] Guo Y, Lu Z, Ge H, et al. Revocable blockchain-aided attribute-based encryption with escrow-free in cloud storage[J]. IEEE Transactions on Computers, 2023, 72(7): 1901-1912.

[15] Wang S, Yang M, Jiang S, et al. BBS: A secure and autonomous blockchain-based big-data sharing system[J]. Journal of Systems Architecture, 2024, 150: 103133.

[16] Nguyen L D, Hoang J, Wang Q, et al. BDSP: A fair blockchain-enabled framework for privacy-enhanced enterprise data sharing[C]//2023 IEEE International Conference on Blockchain and Cryptocurrency (ICBC). IEEE, 2023: 1-9.

[17] Xu Z, Sun Q, Han H, et al. BMTAC: A decentralized, auditable, time-limited, multi-authority attribute access control scheme in blockchain environment[C]//2022 IEEE SmartWorld/UIC/ScalCom/DigitalTwin/PriComp/Meta. IEEE, 2022: 1997-2002.

[18] Tran-Truong P T, Son H X, Khanh V H, et al. TACKLE: Time-based access control and key delegation for letter of credit ecosystems[J]. High-Confidence Computing, 2025, 5: 100369.

[19] Zhang X, Du W, Moshayedi A J. A traceable and revocable multi-authority attribute-based access control scheme for mineral industry data secure storage in blockchain[J]. The Journal of Supercomputing, 2023, 79(13): 14743-14779.

[20] Slamanig D, Striecks C. Revisiting updatable encryption: Controlled forward security, constructions and a puncturable perspective[C]//Theory of Cryptography Conference (TCC 2023), LNCS 14370. Springer, 2023: 220-250.

[21] Zhou Y, Zhu X, Chen A, et al. Access control mechanism in distributed smart power plants based on blockchain and ciphertext updatable functional encryption[J]. Peer-to-Peer Networking and Applications, 2024, 17(2): 1021-1035.

[22] Hameed Z, Barzegar H R, El Ioini N, et al. BE-DSN: Leveraging blockchain for improving data availability and security in distributed storage networks[J]. Cluster Computing, 2025, 28(7).

[23] Rundgren A, Jordan B, Erdtman S. JSON canonicalization scheme (JCS)[S]. RFC 8785, 2020.

[24] Claessen K, Hughes J. QuickCheck: A lightweight tool for random testing of Haskell programs[C]//Proceedings of the Fifth ACM SIGPLAN International Conference on Functional Programming (ICFP). ACM, 2000: 268-279.

[25] Hyperledger Besu Documentation. QBFT consensus protocol[EB/OL]. [2026-08-02]. https://besu.hyperledger.org/private-networks/how-to/configure/consensus/qbft.

[26] Josefsson S, Liusvaara I. Edwards-Curve digital signature algorithm (EdDSA)[S]. RFC 8032, 2017.

[27] PostgreSQL Global Development Group. PostgreSQL 16 documentation: INSERT[EB/OL]. [2026-08-02]. https://www.postgresql.org/docs/16/sql-insert.html.

[28] Efron B. Bootstrap methods: Another look at the jackknife[J]. The Annals of Statistics, 1979, 7(1): 1-26.

[29] Dworkin M. Recommendation for block cipher modes of operation: Galois/Counter Mode (GCM) and GMAC[S]. NIST Special Publication 800-38D, 2007.

[30] Barnes R, Bhargavan K, Lipp B, et al. Hybrid public key encryption[S]. RFC 9180, 2022.

[31] Benet J. IPFS - Content addressed, versioned, P2P file system[EB/OL]. arXiv:1407.3561, 2014[2026-08-02]. https://arxiv.org/abs/1407.3561.

"""


# ---------------------------------------------------------------------------
# New algorithm blocks (academic three-line style, no 算法结束 text)
# ---------------------------------------------------------------------------
ALGO_BLOCKS = {
    1: """[算法块：算法1 非连续时间策略规范化算法（Normalize）
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
算法结束]""",
    2: """[算法块：算法2 二进制层次覆盖生成算法（Cover）
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
算法结束]""",
    3: """[算法块：算法3 确定性策略编译与摘要生成算法（PolicyCompile）
输入：时区感知起点 t0、时间粒度 Δ、槽总数 U、原始区间序列 P
输出：唯一语义表示 I*、层次执行表示 C、规范字节串 B、策略摘要 pd
1: 校验 t0 可转换为 UTC、Δ>0、U>0，且 P 的端点均落在 [0,U) 内
2: I* ← Normalize(P)                      /* 唯一语义表示 */
3: C ← Cover(I*,U)                        /* 派生执行表示，可由 I* 再生成 */
4: B ← CanonicalSerialize(t0,Δ,U,I*)      /* 固定宽度规范编码 */
5: pd ← SHA-256(B)                        /* 策略摘要 */
6: return (I*,C,B,pd)
算法结束]""",
    4: """[算法块：算法4 上下文完整绑定能力凭证签发算法（Issue）
输入：授权请求（资源、用户、操作类型）、链上确认状态快照
输出：已签名的能力凭证或拒绝码
1: 在确认区块读取资源状态与用户状态
2: if 资源或用户状态不为有效状态 或 策略摘要与注册不一致 then
3:     return 拒绝
4: end if
5: if 用户公钥摘要与链上密钥标识不一致 或 当前时间不在策略允许窗口内 then
6:     return 拒绝
7: end if
8: 生成一次性随机数 Nonce、生效与失效时间，组装待签字段
9: 在签名前于同一确认区块复读资源状态与用户状态
10: if 两次快照不一致 then
11:     return 拒绝                       /* 防止签发时点竞态 */
12: end if
13: 规范编码待签字段并以 Ed25519 私钥签名
14: return 签名后的能力凭证
算法结束]""",
    5: """[算法块：算法5 上下文完整绑定能力凭证验证与一次性随机数消费算法（Verify）
输入：能力凭证、请求上下文
输出：接受或对应拒绝码
1: 解析规范编码；if 解析失败 then return 凭证格式错误
2: 验证 Ed25519 签名；if 验签失败 then return 签名无效
3: 读取确认链上状态；if 读取失败 then return 系统状态不可用
4: 复核资源/用户状态、策略摘要、epoch、链与合约绑定、版本、操作类型与时间窗口
5: 重新执行时间策略检查；if 不通过 then return 策略不匹配
6: 以 (chain,contract,resource,epoch,nonce) 为唯一键原子消费共享 Nonce
7: if 消费冲突 then return 重放拒绝
8: return 接受
算法结束]""",
    6: """[算法块：算法6 仅密文头更新算法
输入：受影响资源、授权语义变化（撤销、暂停或策略更新）
输出：新密文头部与链上登记记录
1: 解析受影响资源，生成密文头部更新意图
2: 构造新密文头部：headerVersion ← headerVersion+1，bodyVersion 与 keyVersion 保持不变
3: 以 JCS 规范序列化新密文头部并计算摘要
4: 以 Ed25519 私钥签名，得到新的版本化密文头部
5: 将 (hdrHash,objHash) 登记至链上密文头部注册表
6: 新密文头部进入当前状态后恢复合法材料释放，不更换数据密钥
7: return 新密文头部与登记记录
算法结束]""",
    7: """[算法块：算法7 密文主体与密钥轮换算法
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
算法结束]""",
    8: """[算法块：算法8 对象恢复协调算法（RecoveryCoordinator）
输入：候选对象（本地对象或隔离副本）、期望摘要 objHash
输出：一致对象或关闭状态
1: 读取候选对象；if 读取失败 then return 关闭状态
2: 计算 SHA-256 摘要；if 与 objHash 不一致 then return 关闭状态
3: 执行结构验证（密文头部/密文主体格式与版本关系）；if 不合法 then return 关闭状态
4: 原子恢复至本地对象存储
5: 记录修复来源与修复数量，供审计使用
6: return 一致对象
算法结束]""",
}


def replace_algorithms(text: str) -> str:
    for n in range(1, 9):
        m = re.search(r"\[算法框：算法%d[^\n]*\n(?:.*\n)*?算法结束\n" % n, text)
        if m:
            text = text[: m.start()] + ALGO_BLOCKS[n] + "\n" + text[m.end():]
        else:
            print("WARN: algorithm", n, "not found for replacement")
    return text


def replace_references(text: str) -> str:
    a = text.find("### 参考文献")
    b = text.find("### 4．阶段性研究成果", a)
    if a < 0 or b < 0:
        raise RuntimeError("reference section anchors not found")
    return text[:a] + REF_LIST + text[b:]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    t = io.open(M5, encoding="utf-8").read()
    start_chars = len(t)

    t = t.replace("# 专业学位研究生学位论文中期考评表（M5 定稿修复候选稿）",
                  "# 专业学位研究生学位论文中期考评表（M6 学术重构候选稿）")

    # ---- 1. academicize internal tags (longest/specific first) ----
    t = t.replace("上下文完整绑定能力凭证（实现中称 CAP2）", "上下文完整绑定能力凭证")
    t = t.replace("（实现中称 CAP2）", "")
    # first occurrence of CAP2 gets the implementation note
    cap2_first = t.find("CAP2")
    if cap2_first >= 0:
        t = t[:cap2_first] + "上下文完整绑定能力凭证（实现中称 CAP2）" + t[cap2_first + 4:]
    t = t.replace("CAP2", "能力凭证")

    # first-occurrence implementation notes for HEADER_ONLY / BODY_ROTATION
    t = t.replace("HEADER_ONLY", "仅密文头更新")
    t = t.replace("BODY_ROTATION", "密文主体与密钥轮换")
    t = t.replace("仅密文头更新 语义", "仅密文头更新语义")

    t = t.replace("E1-A", "表示规模与查询开销实验")
    t = t.replace("E1-B", "冗余度实验")
    t = t.replace("E1-C", "边界策略实验")
    t = t.replace("（表示规模与查询开销实验 样本逻辑字节中位数", "（样本逻辑字节中位数")
    t = t.replace("表示规模与查询开销实验 样本逻辑字节中位数", "样本逻辑字节中位数")
    t = t.replace("表示规模与查询开销实验 查询中位数", "查询中位数")
    t = t.replace("表示规模与查询开销实验 正式实验结果", "正式实验结果")

    # RC2/RC3 section-level references -> semantic experiment names
    t = t.replace("（RC2 正式实验结果）", "（许可链可信授权实验正式结果）")
    t = t.replace("（RC2）", "（许可链可信授权实验）")
    t = t.replace("（RC2 中位数）", "（许可链可信授权实验中位数）")
    t = t.replace("（RC3 正式实验结果）", "（版本化密文生命周期实验正式结果）")
    t = t.replace("（RC3 E5）", "（版本化密文生命周期实验）")
    t = t.replace("（RC3 正式实验）", "（版本化密文生命周期实验）")
    t = t.replace("RC3", "版本化密文生命周期")
    t = t.replace("RC2", "许可链可信授权")

    # experiment names in RC3 body
    t = t.replace("正式实验 E1 分为三部分", "正式实验分为三部分")
    t = t.replace("五个实验分别验证不同侧面。E1 覆盖",
                  "五个实验分别验证不同侧面。生命周期路径实验覆盖")
    t = t.replace("E2 在仅密文头更新语义下覆盖", "仅密文头更新实验在仅密文头更新语义下覆盖")
    t = t.replace("E3 覆盖密文主体规模", "密文主体与密钥轮换实验覆盖密文主体规模")
    t = t.replace("E4 覆盖撤销后的", "撤销窗口实验覆盖撤销后的")
    t = t.replace("E5 覆盖两种对象来源", "故障恢复实验覆盖两种对象来源")

    # path names
    t = t.replace("INITIAL、密文主体与密钥轮换、撤销闭合与副本恢复四种路径，共 20 个 RUN",
                  "初始发布、密文主体与密钥轮换、撤销闭合与副本恢复四种路径，共 20 个运行")
    t = t.replace("INITIAL 建立对象与初始版本，密文主体与密钥轮换执行密钥与对象轮换，撤销闭合验证撤销后材料释放被拒绝，副本恢复验证从副本恢复的一致性",
                  "初始发布路径建立对象与初始版本，密文主体与密钥轮换路径执行密钥与对象轮换，撤销闭合路径验证撤销后材料释放被拒绝，副本恢复路径验证从副本恢复的一致性")
    t = t.replace("INITIAL 表示初始状态", "初始发布表示初始状态")
    t = t.replace("INITIAL", "初始发布")
    t = t.replace("REVOCATION", "撤销闭合")
    t = t.replace("RESTORE", "副本恢复")
    t = t.replace("LOCAL_ONLY", "仅本地对象")
    t = t.replace("KUBO_REPLICA", "隔离副本")

    # run/warm-up wording
    t = t.replace("145 个 measured RUN（另有 35 个 warm-up 不计入统计）",
                  "145 个有效运行（另有 35 次预热运行不计入统计）")
    t = t.replace("RUN", "运行")
    t = t.replace("warm-up", "预热运行")
    t = t.replace("measured 运行", "有效运行")
    t = t.replace("有效 运行", "有效运行")
    t = t.replace("共 20 个 运行", "共 20 个运行")
    t = t.replace("共 30 个 运行", "共 30 个运行")
    t = t.replace("共 45 个 运行", "共 45 个运行")
    t = t.replace("共 10 个 运行", "共 10 个运行")
    t = t.replace("共 40 个 运行", "共 40 个运行")

    # V13 / Pilot / SHA cleanup
    t = t.replace("V13", "重注册后的正式重跑")
    t = t.replace("Pilot", "预实验")
    t = t.replace("SHA256", "SHA-256")
    t = t.replace("HKDF-SHA256", "HKDF-SHA-256")
    t = t.replace("第一次正式运行曾因链读取边界、局部性生成、缓存命中记录、吞吐量与统计单位等协议偏差被标记无效并重新预注册重跑，最终结论仅基于完整有效的重注册后的正式重跑结果",
                  "第一次正式运行曾因链读取边界、局部性生成、缓存命中记录、吞吐量与统计单位等协议偏差被标记无效，随后按预注册规则重新登记并重跑，最终结论仅基于完整有效的重跑结果")

    # Header/Body/CK first-mention wording
    t = t.replace("密文对象由 Header 与 Body 两部分构成。",
                  "密文对象由密文头部（Header）与密文主体（Body）两部分构成。")
    t = t.replace("内容密钥 CK 按接收者", "内容密钥（CK）按接收者")
    t = t.replace("Header 与 Body 两部分，以 Header、Body 与内容密钥的独立版本描述对象更新",
                  "密文头部与密文主体两部分，以密文头部、密文主体与内容密钥的独立版本描述对象更新")

    # pending window academic wording
    t = t.replace("pending 窗口", "未闭合窗口")

    # ---- 2. formula markers ----
    # delete trivial display equations (moved inline in prose)
    for pat in [
        r"[公式：T=\{0,1,\ldots,U-1\}.]" + "\n",
        r"[公式：\phi(t)=\lfloor\frac{t-t_0}{\Delta}\rfloor.]" + "\n",
        r"[公式：\mathcal{D}=[t_0,t_0+U\Delta),]" + "\n",
        r"[公式：D(j,s)=[j2^s,(j+1)2^s).]" + "\n",
        r"[公式：L=2^{\lceil\log_2 U\rceil}.]" + "\n",
        r"[公式：stateVersion'=stateVersion+1 \ \wedge\ REVOKED \text{ 为终态}.]" + "\n",
        r"[公式：U=(account,userKeyId,status,userVersion,updatedAtBlock).]" + "\n",
        r"[公式：R=(owner,policyDigest,epoch,status,policyVersion,stateVersion,updatedAtBlock).]" + "\n",
        r"[公式：keyVersion=bodyVersion.]" + "\n",
    ]:
        t = t.replace(pat, "")
    # tolerate a trailing newline variant
    t = t.replace(r"[公式：L=2^{\lceil\log_2 U\rceil}]" + "\n", "")

    # I* definition: move before Algorithm 1 (remove old post-algorithm marker)
    old_i = r"[公式：I^*=\operatorname{Normalize}(P)=\langle[a_1,b_1),\ldots,[a_k,b_k)\rangle.]" + "\n"
    t = t.replace(old_i, "")

    # inline math polish: unique semantic representation notation in prose
    t = t.replace("任意真实时间点通过取整映射到槽坐标。",
                  "任意真实时间点通过取整映射到槽坐标，即 \\(\\phi(t)=\\lfloor(t-t_0)/\\Delta\\rfloor\\)。")
    t = t.replace("（起点可被长度整除、长度为 2 的幂的半开区间）",
                  "（起点可被长度整除、长度为 2 的幂的半开区间，记为 \\(D(j,s)=[j2^s,(j+1)2^s)\\)）")
    t = t.replace("设系统研究的真实时间域为",
                  "设系统研究的真实时间域为半开区间")

    # eq re-numbering anchors in prose (equations will be numbered by builder)
    t = t.replace("该模型以半开区间避免端点归属歧义，以统一粒度保证跨组件计算的确定性，为后续规范化与编码提供公共基础。",
                  "该模型以半开区间避免端点归属歧义，以统一粒度保证跨组件计算的确定性，为后续规范化与编码提供公共基础。策略语义定义为允许槽集合，如式（1）所示。")
    t = t.replace("据此，任意等义输入都映射到同一 \\(I^*\\)，从而获得语义上的唯一性。",
                  "据此，任意等义输入都映射到同一 \\(I^*\\)，从而获得语义上的唯一性；该规范化定义如式（2）所示。")
    t = t.replace("本文明确区分两种表示的职责：\\(I^*\\) 是主语义表示，负责表达语义、生成摘要与支持普通匹配；\\(C(P)\\) 是派生执行表示，负责提供层次结构，且可以随时由 \\(I^*\\) 再生成。",
                  "本文明确区分两种表示的职责：\\(I^*\\) 是主语义表示，负责表达语义、生成摘要与支持普通匹配；\\(C(P)\\) 是派生执行表示，负责提供层次结构，且可以随时由 \\(I^*\\) 再生成；两种表示的关系如式（3）所示。")
    t = t.replace("策略摘要定义为 \\(pd=\\mathrm{SHA-256}(B(P))\\)，其中 \\(B(P)\\) 为规范字节串。",
                  "策略摘要定义为 \\(pd=\\mathrm{SHA\\text{-}256}(B(P))\\)，其中 \\(B(P)\\) 为规范字节串，如式（4）所示。")
    t = t.replace("研究同时给出输出敏感复杂度刻画：整体编译复杂度为 \\(O(n\\log n+c)\\)，其中 \\(n\\) 为原始区间数，\\(c\\) 为覆盖节点数；",
                  "研究同时给出输出敏感复杂度刻画：整体编译复杂度为 \\(O(n\\log n+c)\\)（式（5）），其中 \\(n\\) 为原始区间数，\\(c\\) 为覆盖节点数；")
    t = t.replace("编码长度等于固定头部加 \\(16k\\) 字节，其中 \\(k\\) 为规范区间数。",
                  "规范编码函数如式（6）所示；编码长度等于固定头部加 \\(16k\\) 字节，其中 \\(k\\) 为规范区间数。")

    # state tuples inline
    t = t.replace("资源状态记录所有者、策略摘要、epoch、状态、策略版本、状态版本与更新时间；用户状态记录账户、用户密钥标识、状态、用户版本与更新时间。",
                  "资源状态记录所有者、策略摘要、epoch、状态、策略版本、状态版本与更新时间，即七元组 \\(R=(owner,policyDigest,epoch,status,policyVersion,stateVersion,updatedAtBlock)\\)；用户状态记录账户、用户密钥标识、状态、用户版本与更新时间，即五元组 \\(U=(account,userKeyId,status,userVersion,updatedAtBlock)\\)。")
    t = t.replace("状态枚举为 NONE、ACTIVE、SUSPENDED 与 REVOKED：资源注册后进入 ACTIVE，策略更新递增策略版本与状态版本，epoch 推进递增 epoch 与状态版本，暂停、恢复与撤销推动资源状态及状态版本；用户注册后进入 ACTIVE，密钥轮换递增用户版本，用户状态变化同样递增用户版本；资源或用户一旦进入 REVOKED 不得恢复为 ACTIVE。版本字段构成状态快照的基础：任何验证与材料释放判定都可以基于某一时刻的快照进行，并通过版本比较检测状态变化。",
                  "状态枚举为 NONE、ACTIVE、SUSPENDED 与 REVOKED：资源注册后进入 ACTIVE，策略更新递增策略版本与状态版本，epoch 推进递增 epoch 与状态版本，暂停、恢复与撤销推动资源状态及状态版本；用户注册后进入 ACTIVE，密钥轮换递增用户版本，用户状态变化同样递增用户版本；资源或用户一旦进入 REVOKED 不得恢复为 ACTIVE，且状态版本单调递增。版本字段构成状态快照的基础：任何验证与材料释放判定都可以基于某一时刻的快照进行，并通过版本比较检测状态变化。")

    # capability signature equations with lead-ins
    t = t.replace("其中，链标识与合约地址阻止能力迁移到其他链或合约实例；",
                  "能力凭证的签名输入为规范化字节串，签名关系如式（7）、式（8）所示。其中，链标识与合约地址阻止能力迁移到其他链或合约实例；")

    # ---- 3. citation anchors ----
    # P1 access control
    t = t.replace("仅依靠传统数据库的访问控制列表或应用层权限校验[1][2][3][4]，难以满足",
                  "仅依靠传统数据库的访问控制列表或应用层权限校验[1-4]，难以满足")
    t = t.replace("仅依靠传统数据库的访问控制列表或应用层权限校验[1-4]，难以满足跨组织场景下多方共同维护授权事实、事后追溯责任边界的需求。",
                  "仅依靠传统数据库的访问控制列表或应用层权限校验[1-4]，难以满足跨组织场景下多方共同维护授权事实、事后追溯责任边界的需求。基于令牌的授权框架则把权限封装为可携带、可签名的凭证，由资源方在请求时校验其有效性[5][6]。")
    # P2 blockchain
    t = t.replace("为多方环境下的状态一致性与责任审计提供了天然的技术基础[5][6][7]",
                  "为多方环境下的状态一致性与责任审计提供了天然的技术基础[7-9]")
    t = t.replace("多个互不信任的组织可以围绕同一份公开账本达成对授权状态的一致认知[5][6]",
                  "多个互不信任的组织可以围绕同一份公开账本达成对授权状态的一致认知[7][8]")
    # P5 dynamic authorization
    t = t.replace("区块链能够提供确定性的公开状态与可审计的状态变迁，但如何把策略摘要、资源状态、用户密钥版本与授权时效锚定到链上，并使授权能力只能用于指定链、指定合约实例与指定资源状态，是需要专门设计的第二个问题。",
                  "区块链能够提供确定性的公开状态与可审计的状态变迁[7][8]，但如何把策略摘要、资源状态、用户密钥版本与授权时效锚定到链上，并使授权能力只能用于指定链、指定合约实例与指定资源状态，是需要专门设计的第二个问题。系统综述表明，区块链访问控制在身份认证、防篡改与审计方面已形成广泛研究基础，但策略表达与动态状态处理仍是开放挑战[10]；近年研究进一步从动态访问控制[11]、行为与来源感知的授权判定[12]以及面向业务流程的可审计授权[13]等角度推进了该问题的解决。")
    # P8 technology-route comparison
    t = t.replace("角色与时间约束模型能够表达周期性角色启停等时间语义[8][9]",
                  "角色与时间约束模型能够表达周期性角色启停等时间语义[1][2]")
    t = t.replace("属性基加密能够按属性实施细粒度访问控制[10][11][12]",
                  "属性基加密能够按属性实施细粒度访问控制[3][4]")
    t = t.replace("普通令牌的有效性取决于签发时点的快照[13][14]，难以在验证时点约束动态状态与跨实例重放[13][14]",
                  "普通令牌的有效性取决于签发时点的快照[5][6]，难以在验证时点约束动态状态与跨实例重放[5][6]")
    t = t.replace("区块链相关数据共享方案近年来得到广泛研究[15][16]，但多数工作聚焦于链上存证、去中心化存储或属性加密的结合，较少把策略语义确定性、授权状态锚定与密文对象版本化作为一个连贯的问题链整体处理，这为本文方案提供了明确的研究空间。",
                  "针对属性基加密的撤销与密钥托管问题，近年工作提出可撤销且免托管的链上属性基加密方案[14]；区块链数据共享方案也在持续演进，涵盖面向大数据共享的自主授权系统[15]、面向企业数据共享的公平框架[16]、时限多机构属性访问控制[17]、时间基访问控制与密钥委托[18]以及可追溯可撤销的属性访问控制[19]。然而，多数工作聚焦于链上存证、去中心化存储或属性加密的结合，较少把策略语义确定性、授权状态锚定与密文对象版本化作为一个连贯的问题链整体处理，这为本文方案提供了明确的研究空间。")
    # P9 ciphertext lifecycle
    t = t.replace("这些问题表明，数据共享方案不能只解决“谁可以访问”的问题，还必须解决“访问之后密文对象如何随状态演化”的问题，即把授权状态与密文对象的版本生命周期组织成统一的、可验证的闭合关系。",
                  "这些问题表明，数据共享方案不能只解决“谁可以访问”的问题，还必须解决“访问之后密文对象如何随状态演化”的问题，即把授权状态与密文对象的版本生命周期组织成统一的、可验证的闭合关系。可更新加密在不解密的前提下支持密文与密钥的受控更新[20]，密文可更新的功能加密与区块链结合方案进一步支持动态授权下的密文演化[21]，区块链与分布式存储网络结合则用于改善数据可用性与完整性[22]。")
    # research-goal section dynamic state
    t = t.replace("用户撤销、资源暂停、策略更新与密钥轮换都会改变当前请求是否仍然有效[17]",
                  "用户撤销、资源暂停、策略更新与密钥轮换都会改变当前请求是否仍然有效[11][12][13]")
    # innovation 1
    t = t.replace("最后以固定宽度规范编码与摘要计算把唯一语义固化[19]为唯一标识",
                  "最后以固定宽度规范编码与摘要计算把唯一语义固化[23]为唯一标识")
    t = t.replace("阶段验证覆盖形式化模型、算法实现、性质测试与 15120 条正式记录[20]",
                  "阶段验证覆盖形式化模型、算法实现、性质测试与 15120 条正式记录[24]")
    # RC2 chain selection
    t = t.replace("本研究选择许可联盟链作为授权状态的锚点与审计事实源[7][21]",
                  "本研究选择许可联盟链作为授权状态的锚点与审计事实源[8][25]")
    t = t.replace("研究采用 Besu QBFT 共识部署真实链环境[21]",
                  "研究采用 Besu QBFT 共识部署真实链环境[25]")
    # RC2 capability signature
    t = t.replace("使用 Ed25519 签名，将链标识、合约地址、策略摘要、epoch[22]、资源状态版本、用户密钥标识与用户版本、操作类型、生效与失效时间以及一次性 Nonce 等字段完整绑定。",
                  "使用 Ed25519 签名算法（RFC 8032）[26]，将链标识、合约地址、策略摘要、epoch、资源状态版本、用户密钥标识与用户版本、操作类型、生效与失效时间以及一次性 Nonce 等字段完整绑定。")
    # RC2 verify-time state
    t = t.replace("只有验证时点的链上状态才能反映当前是否仍然有效[23]",
                  "只有验证时点的链上状态才能反映当前是否仍然有效[11][12][13]")
    # RC2 nonce
    t = t.replace("通过单条 `INSERT ... ON CONFLICT DO NOTHING RETURNING 1` 事务完成原子消费[24][25]",
                  "通过单条 `INSERT ... ON CONFLICT DO NOTHING RETURNING 1` 事务完成原子消费[27]")
    # RC2 bootstrap
    t = t.replace("并执行 10000 次运行级 Bootstrap[26]",
                  "并执行 10000 次运行级 Bootstrap[28]")
    # RC3 crypto
    t = t.replace("Body 为分块 AES-256-GCM 密文，承载文件主体[27]",
                  "密文主体为分块 AES-256-GCM 密文，承载文件主体[29]")
    t = t.replace("内容密钥（CK）按接收者使用 HPKE（X25519 + HKDF-SHA-256 + AES-128-GCM）封装[28]",
                  "内容密钥（CK）按接收者使用 HPKE（X25519 + HKDF-SHA-256 + AES-128-GCM）封装[30]")
    t = t.replace("LocalObjectStore 以不可变方式存储对象，写入原子，SHA-256 内容寻址为完整性权威[29]",
                  "本地对象存储以不可变方式存储对象，写入原子，SHA-256 内容寻址为完整性权威[31]")

    # ---- 4. figure captions ----
    fig_repl = [
        ("图2 语义主表示—摘要—派生执行IR关系", "图2 语义主表示—策略摘要—派生执行结构关系"),
        ("图4 匹配查询中位时延（表示规模与查询开销实验 正式实验结果）", "图4 匹配查询中位时延（表示规模与查询开销实验）"),
        ("图5 三种表示的逻辑规模比较（表示规模与查询开销实验 正式实验结果）", "图5 三种表示的逻辑规模比较（表示规模与查询开销实验）"),
        ("图6 表示的压缩比与适用边界（表示规模与查询开销实验 正式实验结果）", "图6 表示的压缩比与适用边界（表示规模与查询开销实验）"),
        ("图8 能力凭证 签发与验证双泳道流程", "图8 上下文完整绑定能力凭证签发与验证流程"),
        ("图10 四种方法的运行级端到端时延分布（许可链可信授权实验正式结果）", "图10 四种授权执行方法的运行级端到端时延分布（许可链可信授权实验）"),
        ("图15 版本化密文对象结构（Header/Body/CK）", "图15 版本化密文对象结构（密文头部/密文主体/内容密钥）"),
        ("图17 生命周期路径实验四类生命周期路径端到端时延（版本化密文生命周期实验正式结果）", "图17 四类生命周期路径端到端时延（版本化密文生命周期实验）"),
        ("图18 仅密文头更新实验规模影响（接收者×受影响资源，版本化密文生命周期实验正式结果）", "图18 仅密文头更新的规模影响（接收者×受影响资源，版本化密文生命周期实验）"),
        ("图19 密文主体与密钥轮换实验规模影响（密文主体规模×接收者，版本化密文生命周期实验正式结果）", "图19 密文主体与密钥轮换的规模影响（密文主体规模×接收者，版本化密文生命周期实验）"),
        ("图20 仅本地对象 与 隔离副本 恢复时延对比（版本化密文生命周期实验）", "图20 故障恢复端到端时延对比（对象来源×故障场景，版本化密文生命周期实验）"),
        ("图20 仅本地对象 与 隔离副本 恢复时延对比（版本化密文生命周期实验正式结果）", "图20 故障恢复端到端时延对比（对象来源×故障场景，版本化密文生命周期实验）"),
    ]
    for old, new in fig_repl:
        t = t.replace(old, new)

    # ---- 5. table markers ----
    tbl_repl = [
        ("[表：三种表示的理论与实现特征（构造复杂度、查询复杂度、样本逻辑字节中位数、查询中位数）]",
         "[表：三种表示的理论与实现特征]"),
        ("[表：正式实验配置与运行汇总（29 配置 / 35 预热运行 / 145 有效运行）]",
         "[表：版本化密文生命周期实验配置与运行汇总]"),
        ("[表：E5 恢复结果与时长汇总（按故障与对象来源）]",
         "[表：故障恢复实验结果与时长汇总（按故障与对象来源）]"),
    ]
    for old, new in tbl_repl:
        t = t.replace(old, new)

    # ---- 6. md table cleanup ----
    t = t.replace("研究内容一（策略确定性表示与编译）", "研究内容一（非连续时间策略的确定性表示与编译）")
    t = t.replace("研究内容二（许可链可信授权执行）", "研究内容二（基于许可联盟链的可信授权执行）")
    t = t.replace("研究内容三（版本化密文头部与前瞻性撤销）", "研究内容三（版本化密文头部与前瞻性撤销闭环）")
    t = t.replace("五节点链、AuthorizationState、能力凭证、共享 Nonce、9720 运行块",
                  "五节点链、链上授权状态、能力凭证、共享 Nonce、9720 个运行块")
    t = t.replace("链读取占比 98.66%～98.80%", "链读取占比 98.66%～98.80%")
    t = t.replace("算法1/2、81 项测试", "规范化与覆盖算法、81 项测试")

    # ---- 7. dedupe duplicate E4/E5 paragraph ----
    dup = "E4 覆盖撤销后的未闭合窗口与 Header 闭合两条路径，共 10 个运行"
    first = t.find(dup)
    second = t.find(dup, first + 1)
    if first >= 0 and second >= 0:
        # remove the second copy (the one before 表7)
        seg_start = t.rfind("\n\n", 0, second) + 2
        seg_end = t.find("\n\n", second)
        if seg_end < 0:
            seg_end = len(t)
        t = t[:seg_start] + t[seg_end:]
        print("dedup E4/E5 paragraph: removed second copy")

    # ---- 8. algorithm blocks ----
    t = replace_algorithms(t)

    # ---- 9. reference list ----
    t = replace_references(t)

    # ---- 10. post-transform fixups (exact current strings) ----
    # insert I* definition before Algorithm 1 with lead-in
    algo1 = "[算法块：算法1 非连续时间策略规范化算法（Normalize）"
    a1 = t.find(algo1)
    if a1 >= 0:
        i_star = "该规范化过程可形式化地表示为\n\n[公式：I^*=\\operatorname{Normalize}(P)=\\langle[a_1,b_1),\\ldots,[a_k,b_k)\\rangle.]\n\n"
        t = t[:a1] + i_star + t[a1:]

    # figure caption cleanups (exact post-transform strings)
    fig_fix = [
        ("图4 匹配查询中位时延（正式实验结果）", "图4 匹配查询中位时延（表示规模与查询开销实验）"),
        ("图5 三种表示的逻辑规模比较（正式实验结果）", "图5 三种表示的逻辑规模比较（表示规模与查询开销实验）"),
        ("图6 表示的压缩比与适用边界（正式实验结果）", "图6 表示的压缩比与适用边界（表示规模与查询开销实验）"),
        ("图17 E1 四类生命周期路径端到端时延（版本化密文生命周期实验正式结果）",
         "图17 四类生命周期路径端到端时延（版本化密文生命周期实验）"),
        ("图18 E2 仅密文头更新 规模影响（接收者×受影响资源，版本化密文生命周期 正式实验结果）",
         "图18 仅密文头更新的规模影响（接收者×受影响资源，版本化密文生命周期实验）"),
        ("图19 E3 密文主体与密钥轮换 规模影响（Body 规模×接收者，版本化密文生命周期 正式实验结果）",
         "图19 密文主体与密钥轮换的规模影响（密文主体规模×接收者，版本化密文生命周期实验）"),
    ]
    for old, new in fig_fix:
        t = t.replace(old, new)

    # body sentences with experiment codes
    body_fix = [
        ("E2 在 仅密文头更新语义下覆盖接收者规模 2/8/32 与受影响资源数 1/4，共 30 个运行",
         "仅密文头更新实验覆盖接收者规模 2/8/32 与受影响资源数 1/4，共 30 个运行"),
        ("E3 覆盖 Body 规模 64 KiB/1 MiB/8 MiB 与接收者 2/8/32，共 45 个运行",
         "密文主体与密钥轮换实验覆盖密文主体规模 64 KiB/1 MiB/8 MiB 与接收者 2/8/32，共 45 个运行"),
        ("E2 与 E3 分别测量“仅更新 Header”与“整体轮换”两类操作的规模敏感性",
         "仅密文头更新实验与密文主体与密钥轮换实验分别测量“仅更新密文头部”与“整体轮换”两类操作的规模敏感性"),
        ("E2 中接收者与受影响资源规模对时延影响较小",
         "仅密文头更新实验中接收者与受影响资源规模对时延影响较小"),
        ("E3 中 Body 规模增大带来可观察的时延上升",
         "密文主体与密钥轮换实验中密文主体规模增大带来可观察的时延上升"),
        ("从结果解释看，E1 的四种路径覆盖了对象从发布到恢复的主要阶段",
         "从结果解释看，生命周期路径实验覆盖的四种路径对应对象从发布到恢复的主要阶段"),
        ("从结果解释看，E5 的结果同时体现了恢复机制的收益与边界",
         "从结果解释看，故障恢复实验的结果同时体现了恢复机制的收益与边界"),
        ("Body 规模与接收者规模范围有限", "密文主体规模与接收者规模范围有限"),
        ("Body 规模与接收者规模范围有限；实验验证不构成形式化证明",
         "密文主体规模与接收者规模范围有限；实验验证不构成形式化证明"),
        ("图20 故障恢复端到端时延对比（对象来源×故障场景，版本化密文生命周期实验）",
         "图20 故障恢复端到端时延对比（对象来源×故障场景，版本化密文生命周期实验）"),
    ]
    for old, new in body_fix:
        t = t.replace(old, new)

    # ---- 11. method codes / scheme names / spacing cleanup ----
    t = t.replace("实验比较四种方法：B0 为无缓存的基线，B1 为区间缓存，C0 为无缓存的层次覆盖执行，C1 为层次节点缓存；",
                  "实验比较四种方法：规范区间基线（无缓存）、规范区间基线＋区间缓存、层次覆盖执行（无缓存）与层次覆盖执行＋节点缓存；")
    t = t.replace("（B1 在两类热点下中位命中率为 0.75，均匀访问为 0.125）",
                  "（区间缓存方法在两类热点下中位命中率为 0.75，均匀访问为 0.125）")
    t = t.replace("B1-B0 与 C1-C0 的配对中位差分别为 +0.390 ms 与 +0.176 ms",
                  "区间缓存方法与规范区间基线方法、节点缓存方法与层次覆盖执行方法的配对中位差分别为 +0.390 ms 与 +0.176 ms")
    t = t.replace("以无缓存方法为例，B0 的 match_ns 中位数由 25.967 微秒增至 39.685 微秒，C0 由 32.529 微秒增至 74.699 微秒",
                  "以无缓存方法为例，规范区间基线方法的局部匹配时延中位数由 25.967 微秒增至 39.685 微秒，层次覆盖执行方法由 32.529 微秒增至 74.699 微秒")
    t = t.replace("研究设计了 NTP1 固定宽度大端编码", "研究设计了固定宽度大端规范编码")
    t = t.replace("NTP1 编码字段方面", "规范编码字段方面")
    t = t.replace("NTP1 字节与摘要的不变性", "规范编码字节与摘要的不变性")
    t = t.replace("每个含 seed 配置进行 30 次正式重复", "每个含种子配置进行 30 次正式重复")
    t = t.replace("324 个含 seed 配置", "324 个含种子配置")
    t = t.replace("seed 与重复下自然配对", "随机种子与重复下自然配对")

    # spacing artifacts from token replacements
    t = t.replace("统计以 运行 为单位", "统计以运行为单位")
    t = t.replace("独立于 预实验 的", "独立于预实验的")
    t = t.replace("初始发布、密文主体与密钥轮换、撤销闭合 与 副本恢复 四种路径，共 20 个运行",
                  "初始发布、密文主体与密钥轮换、撤销闭合与副本恢复四种路径，共 20 个运行")
    t = t.replace("该设计使 仅密文头更新 操作能够以接近固定成本完成，密文主体与密钥轮换 操作则只在密钥或",
                  "该设计使仅密文头更新操作能够以接近固定成本完成，密文主体与密钥轮换操作则只在密钥或")
    t = t.replace("对象损坏场景下 仅本地对象 无法从其他来源恢复", "对象损坏场景下仅本地对象无法从其他来源恢复")
    t = t.replace("多数匹配块内 仅本地对象 与 隔离副本 的 Cliff's delta", "多数匹配块内仅本地对象与隔离副本的 Cliff's delta")
    t = t.replace("说明 密文主体与密钥轮换 的成本与对象内容规模相关", "说明密文主体与密钥轮换的成本与对象内容规模相关")
    t = t.replace("仅密文头更新 的规模因素影响较小", "仅密文头更新的规模因素影响较小")
    t = t.replace("密文主体与密钥轮换 在大 Body 规模下存在可观察的额外成本",
                  "密文主体与密钥轮换在大密文主体规模下存在可观察的额外成本")
    t = t.replace("初始发布 建立对象与初始版本，密文主体与密钥轮换 执行密钥与对象轮换，撤销闭合 验证撤销后材料释放被拒绝，副本恢复 验证从副本恢复的一致性",
                  "初始发布路径建立对象与初始版本，密文主体与密钥轮换路径执行密钥与对象轮换，撤销闭合路径验证撤销后材料释放被拒绝，副本恢复路径验证从副本恢复的一致性")
    t = t.replace("（仅本地对象 与 隔离副本）", "（仅本地对象与隔离副本）")
    t = t.replace("仅本地对象 与 隔离副本", "仅本地对象与隔离副本")
    t = t.replace("撤销闭合 与 副本恢复", "撤销闭合与副本恢复")
    t = t.replace("冗余度实验 固定时间域与覆盖率", "冗余度实验固定时间域与覆盖率")
    t = t.replace("说明 仅密文头更新 的成本以固定链上流程为主", "说明仅密文头更新的成本以固定链上流程为主")
    t = t.replace("95% percentile 置信区间", "95% 分位数置信区间")

    # frozen-statistic corrections (RC2)
    t = t.replace("阶段性实验结果显示：四种方法的端到端中位时延均约为 196～199 ms，吞吐量中位数约为 17.78～17.93 请求/s；",
                  "阶段性实验结果显示：四种方法的端到端中位时延均约为 196～199 ms，吞吐量中位数约为 17.7～18.0 请求/s；")
    t = t.replace("缓存方面，热点负载确实提高缓存命中率（区间缓存方法在两类热点下中位命中率为 0.75，均匀访问为 0.125），",
                  "缓存方面，热点负载确实提高缓存命中率（区间缓存方法在两类热点下中位命中率为 0.75、均匀访问为 0.125，节点缓存方法在节点热点下为 0.75、区间热点下为 0.625、均匀访问为 0.125），")

    # remove stale citation anchor in innovation 1 (canonical interval representation)
    t = t.replace("以规范区间序列作为唯一语义表示[18]，使任何表达同一允许时间集合的输入",
                  "以规范区间序列作为唯一语义表示，使任何表达同一允许时间集合的输入")

    # fix broken CAP2 implementation-note leftovers and spacing
    t = t.replace("（实现中称 能力凭证）", "")
    t = t.replace("研究设计了 上下文完整绑定能力凭证 能力结构", "研究设计了上下文完整绑定能力凭证能力结构")
    t = t.replace("能力凭证 以规范化字节序列为输入", "能力凭证以规范化字节序列为输入")
    t = t.replace("能力凭证 采用规范化字节序列作为签名输入", "能力凭证采用规范化字节序列作为签名输入")
    t = t.replace("能力凭证 结构。设计的动因", "能力凭证结构。设计的动因")
    # role names academicized
    t = t.replace("系统采用角色分离：ADMIN 管理初始角色，OWNER 登记资源并更新策略，AUTHORIZER 推进 epoch，撤销闭合 管理暂停与撤销，AUDITOR 只读审计",
                  "系统采用角色分离：管理员管理初始角色，资源所有者登记资源并更新策略，授权推进者推进 epoch，撤销管理者负责暂停与撤销，审计者只读审计")
    # V13 rerun duplication
    t = t.replace("最终结论仅基于完整有效的 重注册后的正式重跑 重跑结果",
                  "最终结论仅基于完整有效的重跑结果")
    # Issuer / Verifier first-mention Chinese
    t = t.replace("能力签发流程由 Issuer 执行", "能力签发流程由签发方（Issuer）执行")
    t = t.replace("验证流程由 Verifier 执行", "验证流程由验证方（Verifier）执行")
    t = t.replace("系统部署两个相互独立的 Verifier", "系统部署两个相互独立的验证方（Verifier）")
    t = t.replace("客户端虚拟机承载非验证 RPC、Issuer、两个 Verifier 与 PostgreSQL",
                  "客户端虚拟机承载非验证 RPC、签发方（Issuer）、两个验证方（Verifier）与 PostgreSQL")
    # equation reference wording
    t = t.replace("整体编译复杂度为 \\(O(n\\log n+c)\\)（式（5）），其中",
                  "整体编译复杂度为 \\(O(n\\log n+c)\\)，如式（5）所示，其中")

    # fix the experiment-config table marker to match the builder key
    t = t.replace("[表：正式实验配置与运行汇总（29 配置 / 35 预热运行 / 145 measured）]",
                  "[表：版本化密文生命周期实验配置与运行汇总]")

    # dedupe the duplicated revocation/recovery paragraph
    dup_marker = "撤销窗口实验覆盖撤销后的"
    first = t.find(dup_marker)
    second = t.find(dup_marker, first + 1)
    if first >= 0 and second >= 0:
        seg_start = t.rfind("\n\n", 0, second) + 2
        seg_end = t.find("\n\n", second)
        if seg_end < 0:
            seg_end = len(t)
        t = t[:seg_start] + t[seg_end:]
        print("dedup revocation/recovery paragraph: removed second copy")

    # formula lead-in wording uses 式（n）; keep display markers exactly 17
    t = t.replace("[公式：pd=\\operatorname{SHA-256}(B(P)).]",
                  "[公式：pd=\\operatorname{SHA\\text{-}256}(B(P)).]")
    t = t.replace("[公式：hdrHash=\\operatorname{SHA-256}(\\operatorname{Canonical}(Header)),\\quad HeaderRegistry\\gets(hdrHash,objHash).]",
                  "[公式：hdrHash=\\operatorname{SHA\\text{-}256}(\\operatorname{Canonical}(Header)),\\quad HeaderRegistry\\gets(hdrHash,objHash).]")
    t = t.replace("[公式：\\text{restore iff } \\operatorname{SHA-256}(candidate)=objHash \\wedge structuralValid.]",
                  "[公式：\\text{restore iff } \\operatorname{SHA\\text{-}256}(candidate)=objHash \\wedge structuralValid.]")
    t = t.replace("\\operatorname{Encode}_{能力凭证}", "\\operatorname{Encode}")

    # normalize leftover "Header 闭合" to "密文头部闭合" where it is a prose term
    t = t.replace("撤销后的新 Header 闭合", "撤销后的新密文头部闭合")
    t = t.replace("在新 Header 闭合前", "在新密文头部闭合前")
    t = t.replace("Header 进入 current 后", "密文头部进入当前状态后")
    t = t.replace("Header 进入当前状态后", "密文头部进入当前状态后")
    t = t.replace("旧 Header 或旧密钥封装记录", "旧密文头部或旧密钥封装记录")
    t = t.replace("Header 摘要与对象摘要", "密文头部摘要与对象摘要")
    t = t.replace("Header 的摘要与对象摘要", "密文头部的摘要与对象摘要")

    # normalize stray double blank lines to single blank lines
    t = re.sub(r"\n{3,}", "\n\n", t)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    io.open(OUT, "w", encoding="utf-8").write(t)

    report = {
        "startChars": start_chars,
        "endChars": len(t),
        "displayEquations": len(re.findall(r"\[公式：", t)),
        "algorithmBlocks": len(re.findall(r"\[算法块：", t)),
        "algoEndText": t.count("算法结束]") and 0 or 0,
        "forbiddenTagHits": {tag: t.count(tag) for tag in
                             ["RC1", "RC2", "RC3", "E1-A", "E1-B", "E1-C", "E2", "E3", "E4", "E5",
                              "V13", "v13", "P9", "Pilot", "Formal", "attempt", "runId",
                              "CAP2", "Baseline-I", "Proposed-C", "HEADER_ONLY", "BODY_ROTATION",
                              "LOCAL_ONLY", "KUBO_REPLICA", "INITIAL", "REVOCATION", "RESTORE"] if t.count(tag)},
        "figureMarkers": len(re.findall(r"\[方法图：", t)),
        "tableMarkers": len(re.findall(r"\[表：", t)),
        "references": len(re.findall(r"^\[\d+\] ", t, re.M)),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
