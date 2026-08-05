# -*- coding: utf-8 -*-
"""M7: dump cover paragraph XML for checkbox fix."""
from __future__ import annotations

import re
import sys

from docx import Document


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    user_docx = r"D:\Users\wangw\Desktop\中期和小论文\王威专业学位研究生学位论文中期考评表.docx"
    doc = Document(user_docx)
    for para in doc.paragraphs:
        t = para.text
        if any(k in t for k in ("攻读学位级别", "硕士", "培养方式", "全日制", "非全日制")):
            print("=" * 80)
            print("TEXT:", repr(t))
            xml = para._p.xml
            xml = re.sub(r"\sxmlns:[a-zA-Z0-9]+=\"[^\"]*\"", "", xml)
            print(xml[:3500])


if __name__ == "__main__":
    main()
