"""Build THESIS-INTEGRATED-MASTER-DRAFT-V1 by assembling real chapter sources."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "docs/thesis-integration"
OUT = OUT_DIR / "THESIS-INTEGRATED-MASTER-DRAFT-V1.md"

RC1 = Path("D:/Research/crypto_thesis/time-policy/第四章正式修订稿V1.2.md")
RC2 = Path("D:/Research/crypto_thesis/epoch-authorization/docs/thesis-drafts/"
           "第5章_链上状态驱动的可信授权执行机制_最终定稿.md")
RC3 = ROOT / "docs/research-content-3-implementation/i13/THESIS-RC3-WRITEBACK-FINAL.md"


def read_utf8(path: Path) -> str:
    return path.read_text("utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ch4 = read_utf8(RC1)
    if "## 参考文献" in ch4:
        ch4 = ch4[: ch4.rindex("## 参考文献")].rstrip() + "\n"
    ch5 = read_utf8(RC2)
    ch6 = read_utf8(RC3)

    abstract_cn = """随着数据共享场景对时间约束和事后追溯要求的提高，授权策略往往由多个不连续、非对齐的时间窗口组成，
并需要在授权状态变化后仍保证链下密文对象的安全释放。针对这些问题，本文面向非连续时间约束的区块链数据共享场景，
研究了策略表示、可信授权执行与密文对象生命周期管理的三项递进关键技术并完成系统实现。

研究内容一提出非连续时间策略的确定性规范化编译方法：以半开区间序列表征唯一语义表示，并据此确定性计算策略摘要，
层次覆盖结构仅作为可再生成的派生执行表示。实验表明，规范化区间列表在本文覆盖的配置范围内是更稳健的默认表示，
层次覆盖未表现出普遍存储优势，其价值限于提供稳定的层次节点接口。

研究内容二在真实五节点许可联盟链上实现了由链上授权状态锚定的可信授权执行机制，设计了与链标识、合约实例、
策略摘要、资源状态与用户密钥版本完整绑定的能力结构，并以共享原子 Nonce 协调多验证实例。
正式实验表明，逐请求链读取主导端到端时延，缓存与层次覆盖未产生稳定工程收益，系统的核心价值在于状态锚定、
重放控制与依赖故障下的 Fail-Closed 行为。

研究内容三实现了版本化密文头部与前瞻性撤销闭环机制，将链上授权状态、数据库任务状态与链下不可变对象组织为
可验证的闭合关系。受控正式实验完成 145 个有效运行：状态一致性与幂等性检查全部通过，未观察到错误材料释放，
撤销窗口内材料释放保持 Fail-Closed；恢复机制在对象损坏场景下提供可验证的恢复来源，并如实报告未观察到清晰
性能效应的副本结果。

本文的贡献集中在面向非连续时间约束的确定性策略表示、基于许可联盟链的可信授权执行，以及版本化密文对象的前瞻性
撤销与恢复闭环，并以预注册的正式实验给出可复现的证据边界。"""

    abstract_en = """Data sharing scenarios often impose non-continuous, misaligned time constraints on authorization
policies, and the shared material must remain securely governed after authorization state changes. This thesis
studies three progressive key technologies for blockchain-based data sharing under non-continuous time
constraints, and implements the corresponding system.

The first research content proposes a deterministic normalization and compilation method for non-continuous
time policies: a canonical half-open interval sequence represents the unique semantics, from which a policy
digest is deterministically derived, while a hierarchical cover is kept only as a regenerable derived execution
representation. Experiments show that the canonical interval list is the more robust default representation
within the tested scope, and the hierarchical cover exhibits no general storage advantage.

The second research content implements trusted authorization execution anchored by on-chain authorization
state on a real five-node permissioned consortium chain. A capability structure fully bound to chain identity,
contract instance, policy digest, resource state and user key version is designed, and a shared atomic nonce
coordinates multiple verifiers. Formal experiments show that per-request chain reads dominate end-to-end
latency; caching and the hierarchical cover yield no stable engineering benefit. The contribution lies in state
anchoring, replay control and fail-closed behavior under dependency failures.

The third research content implements versioned ciphertext headers with a forward-looking revocation and
recovery closure, binding on-chain authorization state, database task state and immutable off-chain objects into
a verifiable whole. A controlled formal experiment completes 145 valid runs: state-consistency and idempotency
checks all pass, no erroneous material release is observed, material release remains fail-closed during the
revocation window, and the recovery mechanism provides a verifiable recovery source under object corruption,
with no clear performance effect of the replica mechanism honestly reported.

The contributions of this thesis are the deterministic policy representation for non-continuous time
constraints, trusted authorization execution on a permissioned consortium chain, and the versioned-ciphertext
forward-looking revocation and recovery closure, together with reproducible pre-registered experimental
evidence and its boundaries."""

    intro = """## 第一章 绪论

### 1.1 研究背景与意义

区块链数据共享中的授权问题同时包含时间维度与状态维度：策略允许访问的时间往往不是单一连续区间，而是由多个
窗口、例外与周期片段组合而成；授权状态还会因暂停、撤销与密钥轮换而变化。系统既需要确定、唯一、可复现的策略
语义，也需要在授权状态变化后仍能控制链下密文对象的释放。本文围绕“非连续时间约束—可信授权执行—密文对象生命周期
管理”这一主线，按三个递进研究内容组织并实现。

### 1.2 研究内容与递进关系

研究内容一解决策略表示问题：将非连续时间约束规范化为唯一语义表示，并确定性计算策略摘要，为后续授权执行提供
稳定输入。研究内容二解决可信执行问题：将策略摘要与授权状态锚定到许可联盟链，通过能力结构与共享 Nonce 保证
授权判定的可审计性与重放控制。研究内容三解决状态变化后的对象治理问题：以版本化密文头部与前瞻性撤销闭环，
在授权状态变化后保持链下密文对象、密钥材料与撤销恢复状态的一致。

三者的关系是：策略表示提供语义与摘要输入，可信授权执行消费该输入并产出可验证的授权状态，密文对象生命周期
管理以该授权状态为材料释放与 Header 更新的可信依据。接口逻辑详见第三章。

### 1.3 主要贡献

1. 提出非连续时间策略的确定性规范化编译方法：唯一语义表示与确定性策略摘要，层次覆盖定位为可选派生执行结构，
   并通过边界实验明确其适用边界（研究内容一）。
2. 在真实五节点许可联盟链上实现并验证链上状态锚定的可信授权执行机制：完整绑定的能力结构、共享原子 Nonce
   与多验证实例一致性、依赖故障下的 Fail-Closed 行为（研究内容二）。
3. 实现版本化密文头部与前瞻性撤销闭环：链上状态、数据库任务与链下不可变对象的可验证闭合，以及受控正式实验
   验证的正确性、安全行为与工程开销边界（研究内容三）。

### 1.4 章节安排

第二章介绍相关工作与技术基础；第三章给出总体技术路线与三项研究内容的接口；第四章至第六章分别对应研究内容一、
二、三；第七章总结全文并讨论未来工作。
"""

    related = """## 第二章 相关工作与技术基础

本章概述与三项研究内容相关的已有工作与基础技术。已有研究使用角色与时间约束描述授权策略[1]，使用区间与层次
结构组织时间语义[2]，以规范序列化保证跨组件一致性[3]，并以性质测试验证实现[4]。本文方法延续这些基础，但将
层次结构定位为派生执行表示而非主语义表示（第四章）。

能力与最小权限原则[5]、许可链共识[6]与数据库原子语义[7]为研究内容二提供基础；Ed25519[8]与 Bootstrap 方法[9]
分别用于签名与统计推断。研究内容三使用标准密码原语 AES-256-GCM、HPKE（RFC 9180）与 Ed25519，其贡献属于
系统组合与状态协议，而非新的密码原语。

[LITERATURE_VERIFICATION_REQUIRED: 近五年许可链授权状态管理、跨链/跨合约能力绑定、多验证器共享一次性状态
相关研究需按学校数据库检索核验后补充]
"""

    transitions = """## 第三章 总体技术路线与三项研究内容接口

### 3.1 策略表示到授权执行的接口

研究内容一输出的唯一语义表示与确定性策略摘要（policyDigest）构成研究内容二的策略输入。能力签发与验证以
policyDigest 为绑定字段，链上资源状态记录 policyDigest，验证流程重新执行时间策略检查，从而将策略语义、
策略摘要与链上状态绑定。

### 3.2 授权状态到密文对象治理的接口

研究内容二输出的可验证授权状态（资源状态、epoch、stateVersion、userVersion）成为研究内容三判断材料释放、
Header 更新与撤销闭环的可信输入。材料释放由 AccessMaterialReleaseGuard 依据链上复合状态判定；撤销事件驱动
Header 更新意图，链下对象版本与恢复动作与链上状态保持一致。

### 3.3 统一状态模型

三个研究内容共享半开区间时间语义（第四章定义）、策略摘要绑定（第四章到第五章）与版本化状态闭合适配（第五章到
第六章），形成“策略表示—可信授权执行—密文对象更新与撤销恢复”的统一主线。"""

    conclusion = """## 第七章 总结与展望

本文围绕非连续时间约束下的区块链数据共享，完成策略表示、可信授权执行与密文对象生命周期管理三项递进研究。
研究内容一建立唯一语义表示与确定性策略摘要，并如实报告层次覆盖不具普遍存储优势的负结果；研究内容二在真实
五节点许可联盟链上验证链上状态锚定、能力绑定、共享 Nonce 与 Fail-Closed；研究内容三实现版本化密文头部与
前瞻性撤销闭环，并以 145 个有效正式运行验证正确性、安全行为与工程开销边界。

未来工作包括：减少可验证链读取成本的安全状态缓存；在独立物理集群与更多节点规模下的性能验证；故障类别与
对象规模的扩展；以及将层次节点接口纳入实际授权协议后的系统性收益验证。
"""

    appendix = """## 附录A 复现说明

三项研究内容的实验均遵循冻结的预注册或验收设计。研究内容三正式实验使用独立于 Pilot 的 Formal 环境
（PostgreSQL 127.0.0.1:55433、隔离 Kubo、单节点 QBFT 链 chainId 2026080201），29 个配置、5 次重复、
145 个 measured RUN 与 35 个 warm-up（不计入统计），统计以 RUN 为单位并使用 10000 次 Bootstrap 的 95%
percentile CI；预注册 digest 与不可变运行索引见复现材料。所有失败运行保留，最终统计仅使用单一冻结实现产生的
accepted runs。"""

    references = """## 参考文献

[1] Bertino E, Bonatti P A, Ferrari E. TRBAC: A Temporal Role-Based Access Control Model[J]. ACM Transactions on
Information and System Security, 2001, 4(3): 191-223. DOI: 10.1145/344287.344298.

[2] Abiteboul S, Manolescu I, Polyzotis N, Preda N, Sun C. XML Processing in DHT Networks[C]//Proceedings of
ICDE 2008. IEEE, 2008: 606-615. DOI: 10.1109/ICDE.2008.4497469.

[3] Rundgren A, Jordan B, Erdtman S. JSON Canonicalization Scheme (JCS): RFC 8785[S]. RFC Editor, 2020.

[4] Claessen K, Hughes J. QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs[C]//Proceedings
of ICFP 2000. New York: ACM, 2000: 268-279. DOI: 10.1145/351240.351266.

[5] Saltzer J H, Schroeder M D. The Protection of Information in Computer Systems[J]. Proceedings of the IEEE,
1975, 63(9): 1278-1308. DOI: 10.1109/PROC.1975.9939.

[6] Hyperledger Besu Documentation. QBFT consensus protocol[EB/OL]. 访问日期待补充。

[7] PostgreSQL Global Development Group. PostgreSQL 16 INSERT Documentation[EB/OL]. 访问日期待补充。

[8] Josefsson S, Liusvaara I. Edwards-Curve Digital Signature Algorithm (EdDSA): RFC 8032[S]. RFC Editor, 2017.

[9] Efron B. Bootstrap Methods: Another Look at the Jackknife[J]. The Annals of Statistics, 1979, 7(1): 1-26.
DOI: 10.1214/aos/1176344552.

[10] Barnes R, Bhargavan K, Lipp B, Wood C. Hybrid Public Key Encryption: RFC 9180[S]. RFC Editor, 2022.

[LITERATURE_VERIFICATION_REQUIRED: 待核验条目见 docs/full-thesis-final-review/literature-verification-queue.json]
"""

    master = []
    master.append("# 《面向非连续时间约束的区块链数据共享关键技术研究及实现》\n")
    master.append("## 集成母本候选稿 V1（I14）\n")
    master.append("> 本稿由真实冻结章节材料集成，来源映射见 `INTEGRATED-THESIS-SOURCE-MAP.json`。\n")
    master.append("## 中文摘要\n\n" + abstract_cn + "\n")
    master.append("## 关键词\n\n非连续时间约束；区块链数据共享；可信授权执行；版本化密文；前瞻性撤销；故障恢复\n")
    master.append("## Abstract\n\n" + abstract_en + "\n")
    master.append("## Keywords\n\nnon-continuous time constraint; blockchain data sharing; trusted authorization; "
                  "versioned ciphertext; forward-looking revocation; recovery\n")
    master.append("## 目录\n\n"
                  "第一章 绪论；第二章 相关工作与技术基础；第三章 总体技术路线；第四章 非连续时间策略规范化编译方法；"
                  "第五章 链上状态驱动的可信授权执行机制；第六章 版本化密文头部与前瞻性撤销闭环机制；"
                  "第七章 总结与展望；参考文献；附录A 复现说明\n")
    master.append(intro)
    master.append(related)
    master.append(transitions)
    master.append(ch4.rstrip() + "\n")
    master.append(ch5.rstrip() + "\n")
    master.append(ch6.rstrip() + "\n")
    master.append(conclusion)
    master.append(references)
    master.append(appendix)
    text = "\n".join(master)
    OUT.write_text(text, encoding="utf-8")

    source_map = {
        "schemaVersion": "IntegratedThesisSourceMapV1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sections": [
            {"section": "中文摘要/Abstract/关键词", "source": "I14 新建候选（基于三章真实结果）", "type": "NEW"},
            {"section": "第一章 绪论", "source": "I14 新建候选（基于开题与三章真实结果）", "type": "NEW"},
            {"section": "第二章 相关工作与技术基础", "source": "I14 新建候选（引用第四章[1-4]与第五章已核验文献）", "type": "NEW_WITH_LITERATURE_QUEUE"},
            {"section": "第三章 总体技术路线", "source": "I14 新建过渡段（接口逻辑来自四/五/六章冻结文本）", "type": "NEW"},
            {"section": "第四章", "source": "time-policy/第四章正式修订稿V1.2.md", "type": "EMBED_VERBATIM"},
            {"section": "第五章", "source": "epoch-authorization/docs/thesis-drafts/第5章_…_最终定稿.md", "type": "EMBED_VERBATIM"},
            {"section": "第六章", "source": "docs/research-content-3-implementation/i13/THESIS-RC3-WRITEBACK-FINAL.md", "type": "EMBED_VERBATIM"},
            {"section": "第七章 总结与展望", "source": "I14 新建候选", "type": "NEW"},
            {"section": "参考文献", "source": "第四章[1-4] + 第五章已核验[5-9] + RFC 9180", "type": "COMPILED"},
            {"section": "附录A 复现说明", "source": "I14 新建候选（基于 I11-I13 复现材料）", "type": "NEW"},
        ],
        "appliedFixes": [
            {"issue": "第四章 4.10 “5120 条记录”与 E1 验收 15120/15120 不一致", "fix": "集成稿沿用 15120/15120（权威验收）；冻结章节文件不改", "chapter": "第四章/附录"},
            {"issue": "第四章稿内嵌“参考文献”与母本汇总参考文献重复", "fix": "剥离第四章内嵌参考文献，统一由母本汇总表承载", "chapter": "集成母本"},
        ],
    }
    (OUT_DIR / "INTEGRATED-THESIS-SOURCE-MAP.json").write_text(
        json.dumps(source_map, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"master": str(OUT), "bytes": OUT.stat().st_size,
                      "sections": len(source_map["sections"])}, sort_keys=True))


if __name__ == "__main__":
    main()
