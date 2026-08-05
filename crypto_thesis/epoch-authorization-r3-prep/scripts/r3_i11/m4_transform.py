# -*- coding: utf-8 -*-
"""M4: refine the M3 midterm source into the M4 candidate source.

Changes applied on top of M3-MIDTERM-SOURCE.md:
1. Renumber references to first-occurrence order (single GB/T 7714 list).
2. Remove section (8) "阶段性实验结果与研究认识总结"; absorb its completion
   overview table into section (7).
3. Rewrite algorithm blocks (normalized multi-line pseudo-code; Algorithm 3
   fully rewritten).
4. Rewrite stage results as 1 paper + 2 patents with stable wording.
5. Rewrite problems/solutions into the 3 research-advancement themes.
6. Polish section (7) closing text.
"""
from __future__ import annotations

import io
import json
import re
import sys
from pathlib import Path


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
M3 = ROOT / "docs/midterm-report/m3/M3-MIDTERM-SOURCE.md"
OUT = ROOT / "docs/midterm-report/m4"
SRC = OUT / "M4-MIDTERM-SOURCE.md"


# New reference order: first occurrence in the M3 body, i.e.
# old-number -> position. Verified against M3 text order.
NEW_ORDER = [5, 13, 26, 28, 21, 22, 23, 1, 17, 15, 18, 19, 11, 12, 16, 24,
             20, 2, 3, 4, 6, 8, 27, 7, 29, 9, 25, 10, 14]


def build_mapping() -> dict[int, int]:
    # old ref number -> new ref number
    mapping = {}
    for new_no, old_no in enumerate(NEW_ORDER, 1):
        mapping[old_no] = new_no
    return mapping


ALGO_BLOCKS = {
    "算法1 非连续时间策略规范化（Normalize）": (
        "算法1 非连续时间策略规范化（Normalize）\n"
        "输入：已离散化区间序列 P，时间域 T={0,1,…,U-1}\n"
        "输出：规范区间序列 I*\n"
        "1: 将 P 中每个区间按左端点升序排序，同左端点按右端点升序\n"
        "2: 初始化空分量序列 cur ← []\n"
        "3: FOR EACH 区间 [l,r) ∈ 排序后序列 DO\n"
        "4:   IF cur 非空 AND l ≤ cur.right 或 l = cur.right THEN\n"
        "5:     cur.right ← max(cur.right, r)   /* 合并相交或相邻区间 */\n"
        "6:   ELSE\n"
        "7:     将 cur 加入 I*；cur ← [l,r)      /* 开始新分量 */\n"
        "8:   END IF\n"
        "9: END FOR\n"
        "10: 将最后一个 cur 加入 I*\n"
        "11: 返回 I*  /* 有序、互斥、互不相邻 */\n"
        "算法结束"
    ),
    "算法2 Dyadic 层次覆盖生成（Cover）": (
        "算法2 Dyadic 层次覆盖生成（Cover）\n"
        "输入：规范区间 I=[l,r)，槽总数 U（L=2^⌈log2 U⌉）\n"
        "输出：最大对齐覆盖节点集合 C\n"
        "1: 初始化 C ← ∅，pos ← l\n"
        "2: WHILE pos < r DO\n"
        "3:   size ← 当前位置可用的最大 2 的幂对齐块\n"
        "4:   WHILE size > r-pos DO size ← size ≫ 1  /* 不超过剩余长度 */\n"
        "5:   将节点 (pos,size) 加入 C\n"
        "6:   pos ← pos + size\n"
        "7: END WHILE\n"
        "8: 返回 C  /* 节点互斥、首尾相接、并集等于 I */\n"
        "算法结束"
    ),
    "算法3 确定性策略编译与摘要生成（PolicyCompile）": (
        "算法3 确定性策略编译与摘要生成（PolicyCompile）\n"
        "输入：时区感知起点 t0、时间粒度 Δ、槽总数 U、区间序列 P\n"
        "输出：唯一语义表示 I*、层次执行表示 C、规范字节串 B、策略摘要 pd\n"
        "1: 校验 t0 可转换为 UTC、Δ>0、U>0 且 P 的端点均落在 [0,U) 内\n"
        "2: I* ← Normalize(P)                    /* 唯一语义表示 */\n"
        "3: C ← Cover(I*, U)                     /* 派生执行表示，可再生成 */\n"
        "4: B ← NTP1Serialize(t0, Δ, U, I*)      /* 固定宽度规范编码 */\n"
        "5: pd ← SHA-256(B)                      /* 策略摘要 */\n"
        "6: 返回 (I*, C, B, pd)\n"
        "算法结束"
    ),
    "算法4 CAP2 能力签发（Issue）": (
        "算法4 CAP2 能力签发（Issue）\n"
        "输入：授权请求（资源、用户、操作）、链上确认状态\n"
        "输出：签名能力 CAP2 或拒绝码\n"
        "1: 在确认区块读取资源状态与用户状态\n"
        "2: 校验资源与用户均为 ACTIVE，且 policyDigest 与注册一致\n"
        "3: 校验 SHA-256(用户公钥) = userKeyId，且当前时间落入策略允许窗口\n"
        "4: 生成一次性 Nonce、生效与失效时间，组装待签字段\n"
        "5: 签名前在同一确认区块复读资源与用户状态\n"
        "6: IF 两次快照不一致 THEN 返回 REJECT  /* 防止签发时点竞态 */\n"
        "7: 规范化编码并以 Ed25519 私钥签名，返回 CAP2\n"
        "算法结束"
    ),
    "算法5 CAP2 验证与共享 Nonce 消费（Verify）": (
        "算法5 CAP2 验证与共享 Nonce 消费（Verify）\n"
        "输入：CAP2 能力、请求上下文\n"
        "输出：ACCEPT 或对应拒绝码\n"
        "1: 解析规范编码；失败返回 MALFORMED_TOKEN\n"
        "2: 验证 Ed25519 签名；失败返回 INVALID_SIGNATURE\n"
        "3: 读取确认链上状态；失败返回 SYSTEM_STATE_UNAVAILABLE\n"
        "4: 逐项复核：资源/用户状态、policyDigest、epoch、链与合约绑定、版本、操作与时间窗口\n"
        "5: 重新执行 I* 时间策略检查\n"
        "6: 以 (chain,contract,resource,epoch,nonce) 为唯一键原子消费共享 Nonce；冲突返回 NONCE_REPLAY\n"
        "7: 全部通过且消费成功时返回 ACCEPT\n"
        "算法结束"
    ),
    "算法6 HEADER_ONLY 更新流程": (
        "算法6 HEADER_ONLY 更新流程\n"
        "输入：受影响资源、授权语义变化（撤销/暂停/策略更新）\n"
        "输出：新 Header 与链上登记记录\n"
        "1: 解析受影响资源，生成 Header 更新意图\n"
        "2: 构造新 Header：headerVersion ← h+1，bodyVersion 与 keyVersion 保持不变\n"
        "3: JCS 规范序列化并以 Ed25519 签名\n"
        "4: 将 (hdrHash, objHash) 登记至 HeaderRegistry\n"
        "5: Header 进入 current 后恢复合法材料释放；不更换数据密钥\n"
        "算法结束"
    ),
    "算法7 BODY_ROTATION 流程": (
        "算法7 BODY_ROTATION 流程\n"
        "输入：需要轮换的密文对象（密钥或内容变化）\n"
        "输出：新 Body、新内容密钥 CK′、新 Header\n"
        "1: 生成新内容密钥 CK′\n"
        "2: 使用 CK′ 对 Body 进行 AES-256-GCM 分块加密\n"
        "3: 为每个接收者以 HPKE 生成新 EncryptedCKRecord\n"
        "4: 构造新 Header：(headerVersion, bodyVersion, keyVersion) ← (h+1, b+1, k+1)\n"
        "5: JCS 序列化、Ed25519 签名并登记 HeaderRegistry\n"
        "算法结束"
    ),
    "算法8 RecoveryCoordinator 故障恢复": (
        "算法8 RecoveryCoordinator 故障恢复\n"
        "输入：候选对象（本地或隔离副本）、期望摘要 objHash\n"
        "输出：一致对象或 FAIL_CLOSED\n"
        "1: 读取候选对象；读取失败返回 FAIL_CLOSED\n"
        "2: 计算 SHA-256 摘要；与 objHash 不一致返回 FAIL_CLOSED\n"
        "3: 结构验证（Header/Body 格式与版本关系）；不合法返回 FAIL_CLOSED\n"
        "4: 原子恢复至 LocalObjectStore\n"
        "5: 记录修复来源与修复数量，供审计\n"
        "6: 返回一致对象\n"
        "算法结束"
    ),
}


STAGE_RESULTS = (
    "[1] 王威, 夏琦, 高建彬, 夏虎. 基于许可联盟链状态锚定与共享 Nonce 的授权执行方法[J]. 软件学报（论文初稿已完成，拟投稿）.\n"
    "[2] 王威, 高建彬, 王鹏. 一种非连续时间访问策略的确定性编译方法及系统: 中国, [P].（专利撰写中，拟申请）.\n"
    "[3] 王威, 高建彬, 王鹏. 一种链上可信授权与版本化密文对象管理方法及系统: 中国, [P].（专利撰写中，拟申请）.\n"
    "另：三套可复现原型与冻结实验数据集（时间策略编译、许可链授权执行、版本化密文头部与撤销恢复）。"
)


NEW_PROBLEMS = (
    "（1）三项研究内容的整体理论贯通与统一抽象仍需加强。研究内容一至三分别形成了较为完整的方法、原型与实验结果，但作为一篇完整的中期研究报告，需要把时间语义表示、链上状态锚定、密文对象版本化三者的接口关系与安全假设整理为连续、自洽的学术论证；研究内容二的安全属性与故障模型、研究内容三的版本一致性论证目前仍以实验验证为主，需要进一步明确实验验证与形式化证明的边界，避免对安全性质作过强概括。\n\n"
    "（2）关键机制的对比论证与实验支撑仍需强化。本报告引用的相关路线（普通令牌、属性基加密、中心化授权、去中心化存储等）在背景部分已有初步对照，但面向时间约束策略表示、状态锚定执行、版本化撤销传导等机制的定量对比仍不充分；实验方面，缓存与层次覆盖的协议级收益、批量密文头更新与更多验证实例的一致性表现尚未在更大规模下验证，现有结论的适用范围需要随证据边界如实表述。\n\n"
    "（3）最终论文集成、规范表达与成果凝练仍需推进。三项研究内容的核心机制与正式实验均已形成，但作为中期报告后续向学位论文过渡，仍需统一符号与术语体系、完善相关工作综述、规范参考文献与图表的交叉引用，并把阶段性成果整理为符合发表规范的论文与专利文本。"
)


NEW_SOLUTIONS = (
    "（1）针对理论贯通与统一抽象问题，将按“统一语义—可信授权执行—密文生命周期闭合”的主线重构论证结构，统一符号与术语，把三项研究内容之间的接口关系整理为可引用的命题形式；理论层面补充研究内容二的安全属性说明与研究内容三的版本一致性论证，明确区分实验验证与形式化证明的边界。验证方式为逐章对照审稿检查表，完成标准为各研究内容接口一致、术语统一、边界表述与冻结证据一致。\n\n"
    "（2）针对对比论证与实验支撑问题，将基于已核验的文献扩充相关工作综述，以对比表整理各路线在时间语义表达、状态锚定、重放控制、撤销传导与恢复能力上的差异；对每一处创新性表述建立证据对照。实验方面按预注册设计补充协议级收益与规模扩展实验，每项扩展先明确假设与指标再执行，无法完成的扩展如实列入论文局限与未来工作。验证方式为文献来源抽查与实验设计预注册检查，完成标准为创新边界与证据一致、扩展实验边界明确。\n\n"
    "（3）针对论文集成与成果凝练问题，将统一全文符号与参考文献系统，完善图表交叉引用与阶段性成果的规范表述；论文初稿围绕研究内容二或三组织核心章节，专利文本按当前方案方向撰写，所有成果状态均采用“已完成初稿/拟投稿/拟申请”的稳妥表述，不虚构发表或授权状态。验证方式为格式规范逐项检查，完成标准为中期报告可直接作为学位论文相关章节的写作基础。"
)


def rewrite_algorithms(text: str) -> str:
    # replace every [算法框：...] block with the canonical text
    def repl(m: re.Match) -> str:
        old = m.group(1)
        for name, new in ALGO_BLOCKS.items():
            if name.split(" ")[0] in old:
                clean = new.replace("算法结束]", "算法结束")
                return f"[算法框：{clean}]"
        return m.group(0)
    return re.sub(r"\[算法框：([^\]]+)\]", repl, text)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    text = io.open(M3, encoding="utf-8").read()
    text = text.replace("# 专业学位研究生学位论文中期考评表（M3 精细重构候选稿）",
                        "# 专业学位研究生学位论文中期考评表（M4 精细重构候选稿）")
    text = re.sub(r"^---\s*$", "", text, flags=re.M)
    # figure 2/3: source order is IR-relation before compile-flow, so swap
    # numbering so that document order matches figure numbers.
    text = text.replace("[方法图：图3 语义主表示—摘要—派生执行IR关系]",
                        "[方法图：图2 语义主表示—摘要—派生执行IR关系]")
    text = text.replace("[方法图：图2 非连续时间策略确定性编译流程]",
                        "[方法图：图3 非连续时间策略确定性编译流程]")
    mapping = build_mapping()

    # 1. renumber citations in the body and the reference list
    def renum(m: re.Match) -> str:
        old = int(m.group(1))
        return f"[{mapping.get(old, old)}]"
    # 1a. renumber citations in the body only (before the reference list)
    ref_heading = "### 参考文献\n"
    body_end = text.find(ref_heading)
    body = re.sub(r"\[(\d+)\]", renum, text[:body_end])
    tail = text[body_end:]

    # 1b. rebuild the reference list in first-occurrence order
    ref_entries = {}
    ref_zone = tail[: tail.find("### 4．阶段性研究成果")] if "### 4．阶段性研究成果" in tail else tail
    for m in re.finditer(r"^\[(\d+)\]\s*(.+)$", ref_zone, re.M):
        ref_entries[int(m.group(1))] = m.group(2).strip()
    new_refs = "\n\n".join(f"[{new_no}] {ref_entries[old_no]}" for new_no, old_no in enumerate(NEW_ORDER, 1))
    tail = re.sub(r"### 参考文献\n\n.*?(?=### 4．阶段性研究成果|## 二、)", f"### 参考文献\n\n{new_refs}\n\n", tail, count=1, flags=re.S)
    text = body + tail

    # 2. remove section (8), keep the completion table moved into section (7)
    s8 = text.find("**（8）阶段性实验结果与研究认识总结**")
    refs = text.find("### 参考文献")
    s8_block = text[s8:refs]
    table_m = re.search(r"\| 研究内容 \| 当前状态 \| 主要证据 \|.*?(?=\n\n)", s8_block, re.S)
    table_txt = table_m.group(0) if table_m else ""
    text = text[:s8] + text[refs:]
    # absorb the table into the end of section (7)
    s7_end = text.find("\n\n**（8）") if "**（8）" in text else text.find("\n\n### 参考文献")
    if s7_end < 0:
        s7_end = text.find("### 参考文献")
    addendum = (
        "\n\n整体完成度可汇总如下：三项研究内容均覆盖“模型—算法—实现—测试—实验”的完整链条，"
        "每项内容都有明确的阶段性结论、负结果与适用边界，为学位论文的后续写作提供了完整的证据基础。\n\n"
        + table_txt + "\n"
    )
    text = text[:s7_end] + addendum + text[s7_end:]

    # 3. rewrite algorithm blocks
    text = rewrite_algorithms(text)

    # 4. stage results rewrite
    sr_start = text.find("### 4．阶段性研究成果")
    sr_end = text.find("## 二、存在的主要问题和解决办法")
    if sr_start >= 0 and sr_end > sr_start:
        seg = text[sr_start:sr_end]
        lines = seg.splitlines()
        keep = [ln for ln in lines if ln.startswith("### ") or ln.startswith("#") or not ln.strip()]
        new_seg = "### 4．阶段性研究成果\n\n" + STAGE_RESULTS + "\n"
        text = text[:sr_start] + new_seg + text[sr_end:]

    # 5. problems/solutions rewrite (3+3, research-advancement themes)
    p_start = text.find("总体来看，当前研究已经形成")
    p_end = text.find("从计划管理角度看")
    if p_start >= 0 and p_end > p_start:
        intro = ("总体来看，当前研究已形成“策略表示—可信授权执行—密文生命周期治理”的技术闭环，"
                 "三项研究内容的核心机制与正式实验均已达到阶段性完成状态。对照中期考评对“技术路线基本闭合、"
                 "后续转向整合与深化”的定位，当前仍存在以下三个需要进一步推进的问题。\n\n")
        text = text[:p_start] + intro + NEW_PROBLEMS + text[p_end:]
    s_start = text.find("针对上述问题，后续将围绕")
    s_end = text.find("下一步具体研究计划（时间以实际中期考评与毕业安排为准）")
    if s_start >= 0 and s_end > s_start:
        intro2 = ("针对上述问题，后续将沿理论贯通、对比强化、集成凝练三条主线继续推进，"
                  "每条问题均有对应的解决办法与可验证的完成标准，具体时间安排统一在后续研究计划中说明。\n\n")
        text = text[:s_start] + intro2 + NEW_SOLUTIONS + text[s_end:]

    OUT.mkdir(parents=True, exist_ok=True)
    io.open(SRC, "w", encoding="utf-8").write(text)
    print(json.dumps({
        "renumberedRefs": len(mapping),
        "section8Removed": "（8）阶段性实验结果与研究认识总结" not in text,
        "algorithms": len(re.findall(r"\[算法框：", text)),
        "refList": len(re.findall(r"^\[\d+\] ", text, re.M)),
        "srcChars": len(text),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
