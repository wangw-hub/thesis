# -*- coding: utf-8 -*-
"""M7 -> FINAL-CLEAN transform.

Eliminates remaining technical/semantic issues on the frozen M7 baseline:
  * references: access dates removed, [25] article number, [1-4] citation
    semantics, IPFS [34] anchor moved to Kubo content-addressed replica;
  * formulas: eq(10) becomes an aligned OMML eqArr (single number), HPKE
    argument-order clarification, no overclaim in release/restore prose;
  * algorithms: Cover fully formalized, Issue double-read semantics fixed,
    HeaderOnlyUpdate rebuilds the legal recipient set, RecoveryCoordinator
    outputs RecoveryDisposition;
  * symbols: U_u (user tuple), R_d (redundancy), B_cap (capability bytes);
  * claims/wording: OAuth/JWT qualification, permissioned-ledger terminology,
    absolute-claim removal, problem ordering, thesis-vs-stage-paper split;
  * content dedup: RC3 database control plane merged, closure section trimmed.
"""
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
M7 = ROOT / "docs/midterm-report/m7/M7-MIDTERM-SOURCE.md"
OUT_DIR = ROOT / "docs/midterm-report/final"
OUT = OUT_DIR / "FINAL-MIDTERM-SOURCE.md"


REPLACEMENTS: list[tuple[str, str, str]] = []


def rep(key: str, old: str, new: str, count: int = 1) -> None:
    REPLACEMENTS.append((key, old, new, count))


# ---------------------------------------------------------------------------
# 1) references: access dates + [25] metadata + citation semantics
# ---------------------------------------------------------------------------
rep(
    "ref27-besu-access-date",
    "Hyperledger Besu Documentation. QBFT consensus protocol[EB/OL]. [2026-08-02]. https://besu.hyperledger.org/private-networks/how-to/configure/consensus/qbft.",
    "Hyperledger Besu Documentation. QBFT consensus protocol[EB/OL]. https://besu.hyperledger.org/private-networks/how-to/configure/consensus/qbft.",
)
rep(
    "ref29-postgres-access-date",
    "PostgreSQL Global Development Group. PostgreSQL 16 documentation: INSERT[EB/OL]. [2026-08-02]. https://www.postgresql.org/docs/16/sql-insert.html.",
    "PostgreSQL Global Development Group. PostgreSQL 16 documentation: INSERT[EB/OL]. https://www.postgresql.org/docs/16/sql-insert.html.",
)
rep(
    "ref34-ipfs-access-date",
    "Benet J. IPFS - Content addressed, versioned, P2P file system[EB/OL]. arXiv:1407.3561, 2014[2026-08-02]. https://arxiv.org/abs/1407.3561.",
    "Benet J. IPFS - Content addressed, versioned, P2P file system[EB/OL]. arXiv:1407.3561, 2014. https://arxiv.org/abs/1407.3561.",
)
rep(
    "ref25-bedsn-article",
    "BE-DSN: Leveraging blockchain for improving data availability and security in distributed storage networks[J]. Cluster Computing, 2025, 28(7).",
    "BE-DSN: Leveraging blockchain for improving data availability and security in distributed storage networks[J]. Cluster Computing, 2025, 28(7): 437.",
)
rep(
    "ref14-semantics",
    "仅依靠传统数据库的访问控制列表或应用层权限校验[1-4]，难以满足跨组织场景下多方共同维护授权事实、事后追溯责任边界的需求。",
    "传统角色/属性访问控制及密码学访问控制机制[1-4]能够在单一管理域内表达权限与策略，但难以满足跨组织场景下多方共同维护授权事实、事后追溯责任边界的需求。",
)
rep(
    "ref34-ipfs-anchor",
    "本地不可变对象存储以不可变方式存储对象，写入原子，SHA-256 内容寻址为完整性权威[34]；Kubo 仅作为隔离副本定位，CID 不替代 SHA-256 的完整性权威。",
    "本地不可变对象存储以不可变方式存储对象，写入原子，SHA-256 内容寻址被规定为对象完整性权威；Kubo 仅作为隔离副本定位，以内容寻址标识关联副本对象[34]，但 CID 不替代 SHA-256 的完整性权威。",
)


# ---------------------------------------------------------------------------
# 2) formulas
# ---------------------------------------------------------------------------
rep(
    "eq10-aligned",
    "[公式：\\operatorname{headerCoreDigest}=\\operatorname{SHA\\text{-}256}(D_H\\,\\Vert\\,\\operatorname{JCS}(HeaderCore)),\\quad \\operatorname{headerObjectDigest}=\\operatorname{SHA\\text{-}256}(signedHeader).]",
    "[公式：\\begin{array}{l}\\operatorname{headerCoreDigest}=\\operatorname{SHA\\text{-}256}(D_H\\,\\Vert\\,\\operatorname{JCS}(HeaderCore))\\\\ \\operatorname{headerObjectDigest}=\\operatorname{SHA\\text{-}256}(signedHeader)\\end{array}]",
)
rep(
    "hpke-arg-order",
    "HPKE 封装将应用上下文绑定到 Info 与 AAD：Info 由链标识、授权状态合约、密文头部注册合约、资源标识、版本三元组、策略摘要、epoch、状态版本、接收者密钥标识与用户版本等字段的规范序列化构成，AAD 绑定封装域标识、上述上下文与密文主体摘要；冻结测试确认错误的 Info 或 AAD 均导致解封装失败。",
    "HPKE 封装将应用上下文绑定到 Info 与 AAD：Info 由链标识、授权状态合约、密文头部注册合约、资源标识、版本三元组、策略摘要、epoch、状态版本、接收者密钥标识与用户版本等字段的规范序列化构成，AAD 绑定封装域标识、上述上下文与密文主体摘要。式（11）中 enc 为一次性封装公钥，ct 为内容密钥封装密文；实参顺序（接收者公钥、明文 CK、info、aad）与冻结实现 seal_base(pk_R, CK, info, aad) 一致。冻结测试确认错误的 Info 或 AAD 均导致解封装失败。",
)


# ---------------------------------------------------------------------------
# 3) algorithms
# ---------------------------------------------------------------------------
ALGO2 = """[算法块：算法2 二进制层次覆盖生成算法（Cover）
输入：规范区间 I=[l,r)，槽总数 U（仅用于端点合法性校验）
输出：最大对齐覆盖节点集合 C
1: C ← ∅；pos ← l
2: while pos < r do
3:     remaining ← r − pos
4:     if pos = 0 then
5:         size ← 不大于 remaining 的最大 2 的幂        /* size = 2^⌊log2 remaining⌋ */
6:     else
7:         size ← 可整除 pos 的最大 2 的幂              /* size = lowbit(pos) = pos & −pos */
8:         while size > remaining do size ← size ≫ 1    /* 不超过剩余长度 */
9:     end if
10:     将节点 (pos,size) 加入 C；pos ← pos + size
11: end while
12: return C                              /* 节点互斥、首尾相接、并集等于 I */
算法结束]"""

OLD_ALGO2 = """[算法块：算法2 二进制层次覆盖生成算法（Cover）
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

rep("algo2-formalize", OLD_ALGO2, ALGO2)
rep(
    "algo2-prose",
    "算法从左至右为每个未覆盖左端点选择当前位置可用的最大对齐块；若该块超过剩余长度，则持续右移缩小，直至完全位于源区间内。",
    "算法从左至右为每个未覆盖左端点选择当前位置可用的最大对齐块：起点为 0 时，取不超过剩余长度的最大 2 的幂；起点非 0 时，取可整除当前位置的最大 2 的幂（即 pos & −pos），若超过剩余长度则持续右移缩小，直至完全位于源区间内；槽总数 U 仅用于端点合法性校验，不参与块大小选择。",
)

ALGO4 = """[算法块：算法4 上下文完整绑定能力凭证签发算法（Issue）
输入：授权请求（资源、用户、操作类型）、链上确认状态
输出：已签名的能力凭证或拒绝码
1: 读取最新确认区块上的资源状态与用户状态
2: if 资源或用户状态不为有效状态 或 策略摘要与注册不一致 then
3:     return 拒绝
4: end if
5: if 用户公钥摘要与链上密钥标识不一致 或 当前时间不在策略允许窗口内 then
6:     return 拒绝
7: end if
8: 生成一次性随机数 Nonce、生效与失效时间，组装待签字段
9: 在签名前再次读取最新确认区块上的资源状态与用户状态
10: if 两次读取返回的状态不一致 then
11:     return 拒绝                       /* 两次读取之间存在已确认状态变迁 */
12: end if
13: 规范编码待签字段并以 Ed25519 私钥签名
14: return 签名后的能力凭证
算法结束]"""

OLD_ALGO4 = """[算法块：算法4 上下文完整绑定能力凭证签发算法（Issue）
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
算法结束]"""

rep("algo4-double-read", OLD_ALGO4, ALGO4)
rep(
    "issue-prose",
    "能力签发流程由签发方（Issuer）执行：首先在同一确认区块读取资源状态与用户状态，检查资源与用户均为 ACTIVE；随后校验用户公钥哈希与链上密钥标识一致，检查策略摘要一致且当前时间落入策略允许窗口；生成 Nonce、有效期与待签字段后，在签名前再次读取同一资源与用户状态，若两次快照不一致则拒绝签发。签名前复读的目的在于防止“签发时点与读取时点之间状态已经变化”的竞态：签发操作依据的是签名前的最终确认快照，避免把基于过期状态的判断固化到能力中。",
    "能力签发流程由签发方（Issuer）执行：首先读取最新确认区块上的资源状态与用户状态，检查资源与用户均为 ACTIVE；随后校验用户公钥哈希与链上密钥标识一致，检查策略摘要一致且当前时间落入策略允许窗口；生成 Nonce、有效期与待签字段后，在签名前再次读取最新确认区块上的资源状态与用户状态，若两次读取返回的状态不一致则拒绝签发。两次读取均取各自时刻的最新确认快照，签名前复读的目的在于防止“读取时点与签名时点之间状态已经变化”的竞态：若两次读取之间存在任何已确认的状态变迁（资源或用户状态、epoch、版本发生变化），则拒绝签发，避免把基于过期状态的判断固化到能力中。",
)

ALGO6 = """[算法块：算法6 仅密文头更新算法（HeaderOnlyUpdate）
输入：受影响资源、授权语义变化（撤销、暂停或策略更新）
输出：新密文头部与链上登记记录
1: 解析受影响资源，生成密文头部更新意图
2: 根据当前授权状态确定合法接收者集合（被撤销/暂停用户不再进入新密文头部）
3: 复用当前内容密钥与密文主体（Body 与 CK 不变，bodyVersion 与 keyVersion 保持不变）
4: for 每个合法接收者 do
5:     以 HPKE 复用当前内容密钥重新生成加密封装记录
6: end for
7: 构造新密文头部：headerVersion ← headerVersion+1
8: 以 JCS 规范序列化新密文头部并计算 headerCoreDigest
9: 以 Ed25519 私钥签名，得到新的版本化密文头部
10: 计算 headerObjectDigest 与 bodyObjectDigest，登记至链上密文头部注册合约
11: 新密文头部进入当前状态后恢复合法材料释放，不更换数据密钥
12: return 新密文头部与登记记录
算法结束]"""

OLD_ALGO6 = """[算法块：算法6 仅密文头更新算法（HeaderOnlyUpdate）
输入：受影响资源、授权语义变化（撤销、暂停或策略更新）
输出：新密文头部与链上登记记录
1: 解析受影响资源，生成密文头部更新意图
2: 构造新密文头部：headerVersion ← headerVersion+1，bodyVersion 与 keyVersion 保持不变
3: 以 JCS 规范序列化新密文头部并计算摘要
4: 以 Ed25519 私钥签名，得到新的版本化密文头部
5: 将 (headerCoreDigest,headerObjectDigest,bodyObjectDigest) 登记至链上密文头部注册合约
6: 新密文头部进入当前状态后恢复合法材料释放，不更换数据密钥
7: return 新密文头部与登记记录
算法结束]"""

rep("algo6-recipient-rebuild", OLD_ALGO6, ALGO6)
rep(
    "algo6-version-prose",
    "两类状态迁移的语义先于算法给出定义：仅密文头更新执行 (h,b,k)↦(h+1,b,k)，密文主体与密钥轮换执行 (h,b,k)↦(h+1,b+1,k+1)，如式（13）、式（14）所示。仅密文头更新用于授权语义变化（如撤销后的密文头部闭合）而不更换数据密钥，密文主体与密钥轮换用于更换密文对象与密钥。",
    "两类状态迁移的语义先于算法给出定义：仅密文头更新执行 (h,b,k)↦(h+1,b,k)，密文主体与密钥轮换执行 (h,b,k)↦(h+1,b+1,k+1)，如式（13）、式（14）所示。仅密文头更新用于授权语义变化（如撤销后的密文头部闭合）而不更换数据密钥，其关键动作是按当前授权状态重建合法接收者集合的封装记录：被撤销用户不再出现在新密文头部中，合法用户继续获得同一内容密钥对应的新封装记录（冻结实验证据：revokedRecipientAbsent、legalRecipientRetained、bodyDigestUnchanged 均为真）；密文主体与密钥轮换用于更换密文对象与密钥。",
)

ALGO8 = """[算法块：算法8 对象恢复协调算法（RecoveryCoordinator）
输入：候选对象（本地对象或隔离副本）、期望摘要 objHash、可信备份可用性
输出：一致对象或恢复判定（RecoveryDisposition）
1: 读取候选对象；if 候选不存在 then return 缺失对象故障闭合（FAIL_CLOSED_MISSING_OBJECT）
2: 计算 SHA-256 摘要；if 与 objHash 不一致 then return 对象损坏故障闭合（FAIL_CLOSED_CORRUPT_OBJECT）
3: 执行结构验证（密文头部/密文主体格式与版本关系）；if 不合法 then return 对象损坏故障闭合（FAIL_CLOSED_CORRUPT_OBJECT）
4: if 存在已验证的可信备份 then
5:     原子恢复至本地对象存储并记录修复来源与修复数量
6:     return 一致对象（CONSISTENT，自动恢复）
7: else
8:     return 不可恢复内容损失（IRRECOVERABLE_CONTENT_LOSS）或需人工核对（MANUAL_RECONCILIATION_REQUIRED）
9: end if
算法结束]"""

OLD_ALGO8 = """[算法块：算法8 对象恢复协调算法（RecoveryCoordinator）
输入：候选对象（本地对象或隔离副本）、期望摘要 objHash
输出：一致对象或关闭状态
1: 读取候选对象；if 读取失败 then return 关闭状态
2: 计算 SHA-256 摘要；if 与 objHash 不一致 then return 关闭状态
3: 执行结构验证（密文头部/密文主体格式与版本关系）；if 不合法 then return 关闭状态
4: 原子恢复至本地对象存储
5: 记录修复来源与修复数量，供审计使用
6: return 一致对象
算法结束]"""

rep("algo8-disposition", OLD_ALGO8, ALGO8)
rep(
    "algo8-prose",
    "恢复由恢复协调器（RecoveryCoordinator）协调：读取候选对象、SHA 验证、结构验证、原子恢复，最终形成一致状态或 Fail-Closed 结果。",
    "恢复由恢复协调器（RecoveryCoordinator）协调：读取候选对象、SHA 验证、结构验证、原子恢复，最终形成一致对象或对应的恢复判定（RecoveryDisposition，如 AUTO_RECOVERABLE、FAIL_CLOSED_CORRUPT_OBJECT、IRRECOVERABLE_CONTENT_LOSS、MANUAL_RECONCILIATION_REQUIRED 等）。",
)


# ---------------------------------------------------------------------------
# 4) symbols
# ---------------------------------------------------------------------------
rep("sym-user-tuple", "即五元组 \\(U=(account,userKeyId,status,userVersion,updatedAtBlock)\\)", "即五元组 \\(U_u=(account,userKeyId,status,userVersion,updatedAtBlock)\\)")
rep("sym-redundancy-1", "冗余度 \\(R=2\\) 与 3 个随机种子", "冗余度 \\(R_d=2\\) 与 3 个随机种子")
rep("sym-redundancy-2", "考察冗余度 \\(R\\in\\{1,2,4,8\\}\\)", "考察冗余度 \\(R_d\\in\\{1,2,4,8\\}\\)")
rep("sym-cap-bytes-1", "[公式：\\sigma=\\operatorname{Ed25519.Sign}(sk_I,B).]", "[公式：\\sigma=\\operatorname{Ed25519.Sign}(sk_I,B_{cap}).]")
rep("sym-cap-bytes-2", "[公式：B=\\operatorname{Encode}(F_1\\Vert F_2\\Vert\\cdots\\Vert F_n).]", "[公式：B_{cap}=\\operatorname{Encode}(F_1\\Vert F_2\\Vert\\cdots\\Vert F_n).]")


# ---------------------------------------------------------------------------
# 5) claims / wording
# ---------------------------------------------------------------------------
rep(
    "claim-oauth-jwt",
    "设计的动因是：普通令牌通常只包含签发者、主体与有效期，无法约束令牌在哪个链、哪个合约实例、哪个资源状态版本下有效；持有令牌的用户可以把令牌用于其他环境或其他资源，也可以在状态变化后继续使用旧令牌。",
    "设计的动因是：若令牌未显式绑定链标识、合约实例、策略摘要及动态状态版本，且验证时不读取共享在线状态，则令牌本身无法提供本文定义的跨部署域约束、状态版本约束与跨实例一次性消费语义；持有令牌的用户可能把令牌用于其他环境或其他资源，也可能在状态变化后继续使用旧令牌。",
)
rep(
    "claim-public-ledger",
    "多个互不信任的组织可以围绕同一份公开账本达成对授权状态的一致认知[7][8]",
    "多个互不信任的组织可以围绕同一份多方共享账本达成对授权状态的一致认知[7][8]",
)
rep(
    "claim-public-state-1",
    "区块链能够提供确定性的公开状态与可审计的状态变迁[7][8]",
    "区块链能够提供确定性的共享状态与可审计的状态变迁[7][8]",
)
rep(
    "claim-public-state-2",
    "链上只保存必要的公开状态、摘要与审计信息",
    "链上只保存必要的共享状态、摘要与审计信息",
)
rep(
    "claim-public-source",
    "该部署不是“演示性搭链”，而是为授权状态提供确定性的公开事实源",
    "该部署不是“演示性搭链”，而是为授权状态提供多方共享、可验证、可审计的事实源",
)
rep(
    "claim-absolute",
    "三个接口分别对应“语义一致”“状态一致”“对象一致”，共同保证系统在正常路径与故障路径下都不会出现链上状态与链下执行脱节的情况。",
    "三个接口分别对应“语义一致”“状态一致”“对象一致”，在当前冻结实现、故障模型与实验覆盖范围内，未观察到导致链上状态与链下执行不一致的违规路径。",
)
rep(
    "claim-problem-order",
    "从计划管理角度看，上述问题的解决顺序为：先完成论文结构整合与理论表述（问题一），再完善相关工作与创新边界（问题三），随后在条件允许时补充扩展实验与对比实验（问题二），最后完成全文定稿。",
    "从计划管理角度看，上述问题的解决顺序为：首先完成理论贯通与全文结构整合，其次完善相关工作与创新边界，再根据学位论文核心论证需要开展必要的针对性补充验证，最终完成全文定稿。",
)
rep(
    "claim-thesis-vs-stage",
    "论文初稿围绕研究内容二或三组织核心章节，专利文本按当前方案方向撰写",
    "学位论文初稿按照三项递进研究内容组织核心章节；阶段性学术论文根据成熟度从研究内容二或研究内容三中凝练独立问题。专利文本按当前方案方向撰写",
)


# ---------------------------------------------------------------------------
# 6) content dedup
# ---------------------------------------------------------------------------
rep(
    "dedup-db-plane-1",
    "数据库控制面是链上写入与链下任务之间的同步层：任务在显式提交后即可被独立连接读取，经写入准入后广播交易，以回执与固定区块状态验证后固化为已提交；数据库事务不跨链回执等待，避免把链上确认时延引入数据库事务边界。操作标识（operationId）保证重复执行幂等：同一任务即使因网络重试被执行多次，也只产生一次链上效果；提交结果不确定等异常按预注册规则处理，不擅自回滚链上已确认的状态。任务状态机的状态迁移覆盖创建、准入、广播、已提交与失败等路径，为审计与恢复提供完整的操作记录。",
    "数据库控制面是链上写入与链下任务之间的同步层：任务在显式提交后即可被独立连接读取，经写入准入后广播交易，以回执与固定区块状态验证后固化为已提交；数据库事务不跨链回执等待，避免把链上确认时延引入数据库事务边界。操作标识（operationId）保证重复执行幂等：同一任务即使因网络重试被执行多次，也只产生一次链上效果；提交结果不确定（COMMIT_UNKNOWN）等异常按预注册规则处理，不擅自回滚链上已确认的状态。任务状态机的状态迁移覆盖创建、准入、广播、已提交与失败等路径，为审计与恢复提供完整的操作记录。",
)
rep(
    "dedup-db-plane-2",
    "数据库控制面解决的是“链上写入与链下应用之间的一致性”问题：应用先写入任务记录再提交链上交易，链上回执与固定区块状态验证通过后才把任务固化为已提交，任何中间失败都保留可审计的记录；操作标识保证幂等，使重试不会产生重复效果。这一设计使链下任务状态与链上交易结果在最终一致的前提下可追踪，为撤销流程、密文头部更新流程与恢复流程提供统一的状态基础。",
    "这一设计解决的是链上写入与链下应用之间的一致性问题：应用先写入任务记录再提交链上交易，任何中间失败都保留可审计的记录，使链下任务状态与链上交易结果在最终一致的前提下可追踪，为撤销流程、密文头部更新流程与恢复流程提供统一的状态基础。",
)
rep(
    "dedup-db-plane-3",
    "；数据库控制面以任务状态机管理链上写入：任务显式提交后可被独立连接读取，经准入后广播交易，以回执与固定区块状态验证后固化为已提交；数据库事务不跨链回执等待，操作标识保证重复执行幂等，提交结果不确定等异常按预注册规则处理。",
    "。",
)
rep(
    "dedup-closure",
    "整个生命周期中，策略摘要、授权状态、任务状态与对象摘要相互绑定，任何一环的状态变化都会沿接口传导，形成“策略生成—状态锚定—材料释放—版本更新—撤销恢复”的反馈闭环。",
    "整个生命周期中，策略摘要、授权状态、任务状态与对象摘要相互绑定，任何一环的状态变化都会沿接口传导形成反馈闭环。",
)


# ---------------------------------------------------------------------------
# 7) figure-20 note + stage result truth
# ---------------------------------------------------------------------------
rep(
    "fig20-note",
    "多数匹配块内仅本地对象与隔离副本的 Cliff's delta 约 0.04",
    "恢复时延比较仅覆盖无故障与对象损坏两类可比较场景：内容标识不一致和双端缺失场景按 Fail-Closed 终止，不纳入恢复时延比较。多数匹配块内仅本地对象与隔离副本的 Cliff's delta 约 0.04",
)
rep(
    "stage-paper-status",
    "[1] 阶段性学术论文：《基于许可联盟链状态锚定与共享 Nonce 的授权执行方法》。论文初稿已完成，拟投稿《软件学报》。",
    "[1] 阶段性学术论文：《基于许可联盟链状态锚定与共享 Nonce 的授权执行方法》。正在形成论文稿，拟投稿《软件学报》。",
)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    text = M7.read_text(encoding="utf-8")
    applied: list[str] = []
    for key, old, new, count in REPLACEMENTS:
        found = text.count(old)
        if found < count:
            raise SystemExit(
                f"REPLACEMENT FAILED: {key}: expected >= {count}, found {found}\n"
                f"old={old[:120]!r}"
            )
        text = text.replace(old, new, count)
        applied.append(f"{key} (x{found})")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print("applied:")
    for a in applied:
        print("  ", a)
    print("wrote:", OUT)


if __name__ == "__main__":
    main()
