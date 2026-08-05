# Manual Line Break Audit

ManualLineBreakAuditV1：V1 DOCX 共 82 个 `<w:br/>`（81 个 text_wrap + 1 个 page）；其中 81 个位于算法/代码框（INTENTIONAL），正文非代码段落无意手动换行 = 0。V2 DOCX 共 84 个 `<w:br/>`（81 个代码框 + 3 个版式换行），UNINTENTIONAL_MANUAL_BREAKS=0。结论：碎片化的真正来源不是手动换行符，而是源稿硬换行被旧组装器逐行成段。
