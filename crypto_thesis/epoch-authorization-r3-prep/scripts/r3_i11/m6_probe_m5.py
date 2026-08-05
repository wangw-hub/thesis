# -*- coding: utf-8 -*-
"""M6: dump M5 source structure (equations, algorithms, figures, tables, refs)."""
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

    out["chars"] = len(t)
    out["lines"] = len(t.splitlines())

    eqs = [(i, m.group(1)) for i, m in enumerate(re.finditer(r"\[公式：([^\]]+)\]", t), 1)]
    out["equations"] = [{"n": i, "latex": e} for i, e in eqs]

    algos = [(i, m.group(1)) for i, m in enumerate(re.finditer(r"\[算法框：([^\]]+)\]", t), 1)]
    out["algorithms"] = [{"n": i, "text": a} for i, a in algos]

    figs = [m.group(1) for m in re.finditer(r"\[方法图：([^\]]+)\]", t)]
    out["figure_markers"] = figs

    tables = [m.group(1) for m in re.finditer(r"\[表：([^\]]+)\]", t)]
    out["table_markers"] = tables

    refs = []
    for m in re.finditer(r"^\[(\d+)\] ([^\n]+)", t, re.M):
        refs.append({"n": int(m.group(1)), "text": m.group(2)})
    out["references"] = refs

    # citation anchors in body order (before the reference list heading)
    body = t[: t.find("### 参考文献")]
    cites = []
    for m in re.finditer(r"\[(\d+)(?:-(\d+))?(?:,(\d+))?\]", body):
        cites.append(m.group(0))
    out["citation_anchors_in_body"] = cites

    tags = ["RC1", "RC2", "RC3", "E1-A", "E1-B", "E1-C", "V13", "v13", "P9",
            "Pilot", "Formal", "attempt", "runId", "SHA", "I9", "I10", "I11",
            "I12", "I13", "I14", "I15", "I16", "I17", "CAP2", "Baseline-I",
            "Proposed-C", "HEADER_ONLY", "BODY_ROTATION", "E2", "E3", "E4", "E5",
            "LOCAL_ONLY", "KUBO_REPLICA", "INITIAL", "REVOCATION", "RESTORE",
            "Normalize", "PolicyCompile", "Cover", "Nonce", "HeaderRegistry",
            "AuthorizationState"]
    tag_counts = {}
    for tag in tags:
        n = t.count(tag)
        if n:
            tag_counts[tag] = n
    out["internal_tag_counts"] = tag_counts

    # md tables
    md_tables = []
    lines = t.splitlines()
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i].strip())
                i += 1
            md_tables.append(rows)
        else:
            i += 1
    out["md_tables"] = md_tables

    Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep\scripts\r3_i11\_m6_probe_out.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "chars": out["chars"],
        "equations": len(out["equations"]),
        "algorithms": len(out["algorithms"]),
        "figures": len(out["figure_markers"]),
        "tables": len(out["table_markers"]),
        "md_tables": len(out["md_tables"]),
        "references": len(out["references"]),
        "citation_anchors": len(out["citation_anchors_in_body"]),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
