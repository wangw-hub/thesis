# -*- coding: utf-8 -*-
"""Spot-check the FINAL source."""
from __future__ import annotations

import re
import sys


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = r"D:\Research\crypto_thesis\epoch-authorization-r3-prep\docs\midterm-report\final\FINAL-MIDTERM-SOURCE.md"
    s = open(p, encoding="utf-8").read()
    absent = [
        "[2026-08-02]",
        "2014[2026-08-02]",
        "公开账本",
        "公开事实源",
        "公开状态",
        "论文初稿已完成",
        "普通令牌通常只包含",
        "于同一确认区块复读",
        "在同一确认区块读取",
        "当前位置可用的最大 2 的幂对齐块",
        "一致对象或关闭状态",
        "共同保证系统在正常路径与故障路径下都不会出现",
        "先完成论文结构整合与理论表述（问题一）",
        "论文初稿围绕研究内容二或三组织核心章节",
        "（问题三）",
        "（问题二）",
        "数据库控制面解决的是",
        "任务状态机管理链上写入：任务显式提交后",
        "完整性权威[34]",
    ]
    present = [
        "Cluster Computing, 2025, 28(7): 437.",
        "传统角色/属性访问控制及密码学访问控制机制[1-4]",
        "以内容寻址标识关联副本对象[34]",
        "\\begin{array}{l}\\operatorname{headerCoreDigest}",
        "seal_base(pk_R, CK, info, aad) 一致",
        "size ← 不大于 remaining 的最大 2 的幂",
        "size ← 可整除 pos 的最大 2 的幂",
        "读取最新确认区块上的资源状态与用户状态",
        "在签名前再次读取最新确认区块上的资源状态与用户状态",
        "根据当前授权状态确定合法接收者集合",
        "复用当前内容密钥与密文主体",
        "revokedRecipientAbsent、legalRecipientRetained、bodyDigestUnchanged 均为真",
        "一致对象或恢复判定（RecoveryDisposition）",
        "FAIL_CLOSED_MISSING_OBJECT",
        "FAIL_CLOSED_CORRUPT_OBJECT",
        "IRRECOVERABLE_CONTENT_LOSS",
        "MANUAL_RECONCILIATION_REQUIRED",
        "在当前冻结实现、故障模型与实验覆盖范围内",
        "学位论文初稿按照三项递进研究内容组织核心章节",
        "正在形成论文稿，拟投稿《软件学报》",
        "提交结果不确定（COMMIT_UNKNOWN）",
        "\\begin{array}{l}",
        "不纳入恢复时延比较",
        "五元组 \\(U_u=(account",
        "冗余度 \\(R_d=2\\)",
        "R_d\\in\\{1,2,4,8\\}",
        "sk_I,B_{cap}",
        "B_{cap}=\\operatorname{Encode}",
        "首先完成理论贯通与全文结构整合",
    ]
    print("--- absent ---")
    for x in sorted(set(absent)):
        print(f"{'OK-absent' if x not in s else 'STILL-PRESENT'} | {x}")
    print("--- present ---")
    for x in sorted(set(present)):
        print(f"{'OK-present' if x in s else 'MISSING'} | {x}")
    print("formulas:", len(re.findall(r"^\[公式：", s, re.M)))
    print("algorithms:", len(re.findall(r"^\[算法块：", s, re.M)))
    print("figures:", len(re.findall(r"^\[方法图：", s, re.M)))
    print("tables:", len(re.findall(r"^\[表：", s, re.M)))


if __name__ == "__main__":
    main()
