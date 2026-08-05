# HeaderUpdateKind

| 类型 | 版本规则 | Body/CK 规则 |
|---|---|---|
| INITIAL | header/body/key 均为 1；previous=0 | 三个对象摘要非零 |
| HEADER_ONLY | header+1；body/key 不变 | bodyObjectDigest 必须不变 |
| BODY_ROTATION | header/body/key 均 +1；key=body | bodyObjectDigest 必须改变；必须使用新 CK 和新 Body |

`HEADER_ONLY` 用于 Envelope 或签名材料更新，不能描述为追回既有 CK。`BODY_ROTATION` 在没有新 Body 对象时不得成功。
