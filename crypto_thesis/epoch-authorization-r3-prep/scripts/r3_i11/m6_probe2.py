# -*- coding: utf-8 -*-
"""M6: probe specific M5 source issues."""
from __future__ import annotations

import io
import json
import re
import sys
from pathlib import Path


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
SRC = ROOT / "docs/midterm-report/m5/M5-MIDTERM-SOURCE.md"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    t = io.open(SRC, encoding="utf-8").read()
    out = {}

    # every algorithm marker start position and first line
    algos = []
    for m in re.finditer(r"\[算法框：", t):
        start = m.start()
        end = t.find("算法结束", start)
        body = t[start:end + 4]
        algos.append({
            "start": start,
            "first_line": t[start:start + 120].replace("\n", " "),
            "has_close_bracket": body.rstrip().endswith("]"),
            "end_tail": repr(body[-40:]),
            "lines": len(body.splitlines()),
        })
    out["algorithm_markers"] = algos

    # "算法结束]" occurrences
    out["algo_end_with_bracket"] = t.count("算法结束]")
    out["algo_end_plain"] = t.count("算法结束")

    # SHA occurrences context
    sha_ctx = []
    for m in re.finditer("SHA", t):
        ctx = t[max(0, m.start() - 45):m.end() + 45].replace("\n", " ")
        sha_ctx.append(ctx)
    out["sha_contexts"] = sha_ctx

    # duplicate E4/E5 paragraph check
    e4 = t.count("E4 覆盖撤销后的 pending 窗口")
    out["e4_paragraph_count"] = e4

    # citation ranges like [5][6] or [13][14] collapsed
    out["citation_style"] = re.findall(r"\[(\d+)\](?:\[(\d+)\])", t[: t.find("### 参考文献")])

    Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep\scripts\r3_i11\_m6_probe2_out.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "algo_markers": len(algos),
        "algo_end_with_bracket": out["algo_end_with_bracket"],
        "algo_end_plain": out["algo_end_plain"],
        "sha_contexts": len(sha_ctx),
        "e4_paragraph_count": e4,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
