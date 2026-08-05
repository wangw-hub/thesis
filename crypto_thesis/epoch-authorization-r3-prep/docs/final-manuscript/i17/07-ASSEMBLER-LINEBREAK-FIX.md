# Assembler Linebreak Fix

旧组装器（build_i16_docx.py）将每个源行渲染为一个 Word 段落；V2 组装器（build_i17_docx.py）改为：Markdown 段落内普通换行→空格/连续文本（CJK 边界不插空格、ASCII 边界补空格），空行→新段落，代码围栏→原样保留（显式 `<w:br/>`）。回归用例 A/B/C/D 见脚本 `prepare_i17_source.py` 的 join_lines。
