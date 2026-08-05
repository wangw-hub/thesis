# -*- coding: utf-8 -*-
"""M5: incremental fixes on top of the M4 midterm source.

1. Fix the dangling "问题四" reference in the problems/solutions section.
2. Remove the obsolete RC3 figure markers (17/18) and re-insert the correct
   four RC3 figure markers at their semantic anchors:
     - 图17 E1 四类生命周期路径
     - 图18 E2 HEADER_ONLY 规模影响
     - 图19 E3 BODY_ROTATION 规模影响
     - 图20 E5 恢复对比
3. Normalize algorithm end marker ("算法结束]" -> "算法结束").
"""
from __future__ import annotations

import io
import json
import re
import sys
from pathlib import Path


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
M4 = ROOT / "docs/midterm-report/m4/M4-MIDTERM-SOURCE.md"
OUT = ROOT / "docs/midterm-report/m5"
SRC = OUT / "M5-MIDTERM-SOURCE.md"


def para_end(text: str, pos: int) -> int:
    nl = text.find("\n\n", pos)
    return nl if nl >= 0 else len(text)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    text = io.open(M4, encoding="utf-8").read()
    text = text.replace("# 专业学位研究生学位论文中期考评表（M4 精细重构候选稿）",
                        "# 专业学位研究生学位论文中期考评表（M5 定稿修复候选稿）")

    # 1. fix 问题四
    text = text.replace("（问题二、问题四）", "（问题二）")
    text = text.replace("问题四", "问题二")

    # 2. remove old RC3 figure markers
    text = re.sub(r"\[方法图：图17 [^\]]*\]", "", text)
    text = re.sub(r"\[方法图：图18 [^\]]*\]", "", text)
    text = re.sub(r"\[方法图：图19 [^\]]*\]", "", text)

    # 3. split the E1/E2/E3 results paragraph into three blocks, each followed
    #    by its own figure marker; insert the E5 marker after the recovery text.
    e1_m = re.search(r"E1 覆盖 INITIAL、BODY_ROTATION、REVOCATION 与 RESTORE 四种路径", text)
    e2_m = re.search(r"E2 在 HEADER_ONLY 语义下覆盖接收者规模 2/8/32 与受影响资源数 1/4", text)
    e3_m = re.search(r"E3 覆盖 Body 规模 64 KiB/1 MiB/8 MiB 与接收者 2/8/32", text)
    if e1_m and e2_m and e3_m:
        p_start = text.rfind("\n\n", 0, e1_m.start()) + 2
        p_end = para_end(text, e1_m.start())
        para = text[p_start:p_end]
        # break into three sentences-turned-paragraphs at the E2/E3 boundaries
        e2_pos = para.find("E2 在 HEADER_ONLY")
        e3_pos = para.find("E3 覆盖 Body")
        part1 = para[:e2_pos].strip()
        part2 = para[e2_pos:e3_pos].strip()
        part3 = para[e3_pos:].strip()
        new_para = (
            f"{part1}\n\n[方法图：图17 E1 四类生命周期路径端到端时延（RC3 正式实验结果）]\n\n"
            f"{part2}\n\n[方法图：图18 E2 HEADER_ONLY 规模影响（接收者×受影响资源，RC3 正式实验结果）]\n\n"
            f"{part3}\n\n[方法图：图19 E3 BODY_ROTATION 规模影响（Body 规模×接收者，RC3 正式实验结果）]"
        )
        text = text[:p_start] + new_para + text[p_end:]
    r5 = re.search(r"恢复端到端时延中位数约 3.1～3.2 s", text)
    if r5:
        end = para_end(text, r5.start())
        text = text[:end] + "\n\n[方法图：图20 LOCAL_ONLY 与 KUBO_REPLICA 恢复时延对比（RC3 E5）]\n" + text[end:]

    # 4. algorithm end marker
    text = text.replace("算法结束]", "算法结束")

    OUT.mkdir(parents=True, exist_ok=True)
    io.open(SRC, "w", encoding="utf-8").write(text)
    print(json.dumps({
        "problemFour": text.count("问题四"),
        "algoEndBracket": text.count("算法结束]"),
        "rc3FigMarkers": [m.group(0)[:50] for m in re.finditer(r"\[方法图：图(1[7-9]|20)[^\]]*\]", text)],
        "srcChars": len(text),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
