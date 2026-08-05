# -*- coding: utf-8 -*-
"""I17: transform MASTER-SOURCE into the reconstructed academic-prose source.

Transforms:
  1. Line reflow: markdown hard wraps -> joined paragraphs (ASCII-aware spacing).
  2. Remove internal assembly notes (blockquotes, source lines, markers).
  3. Split inline numbered lists ("1. x 2. y 3. z" in one paragraph) into items.
  4. Merge adjacent citation brackets [a][b] -> [a, b].
  5. Renumber ch4/ch5 tables so every table is sequentially numbered with a caption.
  6. Swap figure numbers 5-6/5-7/5-8 so appearance order is monotonic.
  7. 第5章 -> 第五章 heading normalization.
"""
from __future__ import annotations

import io
import json
import re
from pathlib import Path


ROOT = Path(r"D:\Research\crypto_thesis\epoch-authorization-r3-prep")
MASTER = ROOT / "docs/final-manuscript/MASTER-SOURCE.md"
OUT = ROOT / "docs/final-manuscript/i17"
SRC_OUT = ROOT / "docs/final-manuscript/i17/I17-SOURCE.md"


def is_cjk(ch: str) -> bool:
    return ord(ch) > 0x2E7F


def join_lines(lines: list[str]) -> str:
    if not lines:
        return ""
    out = lines[0].strip()
    for ln in lines[1:]:
        s = ln.strip()
        if not s:
            continue
        prev = out[-1] if out else ""
        nxt = s[0]
        if (prev and prev.isascii() and prev.isalnum() and nxt.isascii() and nxt.isalnum()) or \
           (prev and prev.isascii() and prev.isalnum() and not nxt.isascii() and not nxt.isspace()) or \
           (nxt and nxt.isascii() and nxt.isalnum() and prev and not prev.isascii() and not prev.isspace()):
            out += " "
        out += s
    return out


def split_numbered_list(text: str) -> list[str]:
    """Split '1. a 2. b 3. c' paragraphs into items; returns list of item strings."""
    # find markers "N." where N increments
    parts = re.split(r"(?<=[。；;])\s*(?=\d+\.\s)", text)
    if len(parts) <= 1:
        parts = re.split(r"\s+(?=\d+\.\s)", text)
    items = [p.strip() for p in parts if p.strip()]
    nums = [int(m.group(1)) for p in items for m in [re.match(r"^(\d+)\.", p)] if m]
    if len(items) >= 2 and nums == list(range(1, len(items) + 1)):
        return items
    return [text]


def transform(text: str) -> tuple[str, dict]:
    manifest: dict = {"paragraphSplits": [], "citationGroups": 0, "noteRemovals": 0,
                      "tableRenumbers": {}, "figureRenumbers": {}}
    paras = []
    cur: list[str] = []
    in_fence = False
    fence: list[str] = []
    lines = text.splitlines()
    n = len(lines)
    i = 0

    def flush():
        if cur:
            paras.append(("para", "\n".join(cur)))
            cur.clear()

    while i < n:
        ln = lines[i]
        s = ln.strip()
        if in_fence:
            fence.append(ln)
            if s.startswith("```"):
                paras.append(("raw", "\n".join(fence)))
                fence, in_fence = [], False
            i += 1
            continue
        if s.startswith("```"):
            flush()
            in_fence = True
            fence = [ln]
            i += 1
            continue
        if not s:
            flush()
            paras.append(("blank", ""))
            i += 1
            continue
        if s.startswith("|"):
            flush()
            tbl = []
            while i < n and lines[i].strip().startswith("|"):
                tbl.append(lines[i])
                i += 1
            paras.append(("raw", "\n".join(tbl)))
            continue
        if re.match(r"^(#{1,4})\s", s) or s.startswith("![") or \
                re.match(r"^\*\*(图|表|算法)", s):
            flush()
            paras.append(("raw", ln))
            i += 1
            continue
        cur.append(ln)
        i += 1
    flush()
    if fence:
        paras.append(("raw", "\n".join(fence)))

    out: list[str] = []
    for kind, payload in paras:
        if kind == "blank":
            if out and not out[-1].startswith("```"):
                out.append("")
            continue
        if kind == "raw":
            out.append(payload)
            out.append("")
            continue
        s = payload.strip()
        if s.startswith(">") or s.startswith("[文献") or s.startswith("[LITERATURE") or \
                s.startswith("来源：") or s == "---" or s.startswith("第一章 绪论；"):
            manifest["noteRemovals"] += 1
            continue
        if re.match(r"^\d+\.\s", s):
            items = split_numbered_list(s)
            if len(items) > 1:
                manifest["paragraphSplits"].append({"from": s[:60], "toItems": len(items)})
                for it in items:
                    out.append(it)
                out.append("")
                continue
        # citation grouping
        new_s = re.sub(r"\]\[(\d+)\]", lambda m: ", " + m.group(1) + "]", s)
        if new_s != s:
            manifest["citationGroups"] += 1
        out.append(new_s)
        out.append("")
    return "\n".join(out), manifest


def renumber_tables(text: str) -> tuple[str, dict]:
    # ch4: old->new
    ch4_map = {"表4-2": "表4-4", "表4-3": "表4-5", "表4-4": "表4-6", "表4-5": "表4-7"}
    ch5_map = {"表5-1": "表5-2", "表5-2": "表5-3"}
    text = text.replace("如表4-2前的分阶段分析所示", "见本节分阶段分析")
    # single-pass with placeholders to avoid cascading
    tmp = {}
    for old in list(ch4_map) + list(ch5_map):
        tmp[old] = "TMPTBL_" + old.replace("表", "").replace("-", "_")
    for old, t in tmp.items():
        text = text.replace(old, t)
    for old, new in ch4_map.items():
        text = text.replace(tmp[old], new)
    for old, new in ch5_map.items():
        text = text.replace(tmp[old], new)
    # add captions for the four unnumbered tables by inserting caption lines
    # caption inserts are done at DOCX build time via block positions; here record mapping
    return text, {"ch4": ch4_map, "ch5": ch5_map}


def renumber_figures(text: str) -> tuple[str, dict]:
    fig_map = {"图5-7": "图5-6", "图5-8": "图5-7", "图5-6": "图5-8"}
    # single-pass mapping (5-6->5-8, 5-7->5-6, 5-8->5-7) - apply via placeholder
    tmp = {}
    for old in ("图5-6", "图5-7", "图5-8"):
        tmp[old] = "TMP_" + old.replace("-", "")
    for old, t in tmp.items():
        text = text.replace(old, t)
    for old, new in fig_map.items():
        text = text.replace(tmp[old], new)
    return text, fig_map


def renumber_lemmas(text: str) -> str:
    # single-pass to avoid cascading (引理4.2 must not become 引理4.4.2)
    def sub(m: re.Match) -> str:
        kind = m.group(1)
        num = m.group(2)
        return f"{kind}4.{num}"

    text = re.sub(r"(引理)([1-4])(?![0-9.])", sub, text)
    text = re.sub(r"(定理)([1-4])(?![0-9.])", sub, text)
    return text


def main() -> None:
    text = io.open(MASTER, encoding="utf-8").read()
    text, manifest = transform(text)
    text, tmap = renumber_tables(text)
    text, fmap = renumber_figures(text)
    text = renumber_lemmas(text)
    text = text.replace("第5章 链上状态驱动的可信授权执行机制", "第五章 链上状态驱动的可信授权执行机制")
    OUT.mkdir(parents=True, exist_ok=True)
    io.open(SRC_OUT, "w", encoding="utf-8").write(text)
    manifest["tableRenumbers"] = tmap
    manifest["figureRenumbers"] = fmap
    io.open(OUT / "i17-transform-manifest.json", "w", encoding="utf-8").write(
        json.dumps({"schemaVersion": "I17TransformManifestV1", "manifest": manifest},
                   ensure_ascii=False, indent=2))
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
