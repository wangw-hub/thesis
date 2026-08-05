# JCS库候选

| 候选 | 能力 | 风险 | 决定 |
|---|---|---|---|
| rfc8785 0.1.4 | 纯Python、无依赖、UTF-8 bytes、拒绝非字符串键 | Beta；需验证UTF-16键排序、数字和负零errata | **SELECTED_CANDIDATE_NOT_INSTALLED** |
| 自写JCS | 可控制字段 | Unicode/ECMAScript数字和排序高风险 | PROHIBITED |
| 普通`json.dumps(sort_keys=True)` | 本地确定性 | 不保证RFC8785数字/UTF-16排序 | REJECTED |

Schema继续把uint64、地址、摘要和二进制表示为受约束字符串，避免超出I-JSON安全整数及二进制歧义。I1/I3必须覆盖Unicode键、控制字符、数字边界、`-0`拒绝、递归排序、重复键预解析拒绝和RFC样例。

来源：[RFC 8785](https://www.rfc-editor.org/rfc/rfc8785.html)、[RFC 8785 verified errata](https://www.rfc-editor.org/errata/rfc8785)、[rfc8785 PyPI](https://pypi.org/project/rfc8785/)。
