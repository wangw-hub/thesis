# HPKE 候选矩阵

| 候选 | 稳定/Py3.13 | 目标 Suite | info/AAD | 确定性 skE | Exporter | RFC 向量 | 决定 |
|---|---|---|---|---|---|---|---|
| PyHPKE 0.6.4 | 是/是 | 是 | 是/是 | 公开 API | 是 | 完整通过 | QUALIFIED |
| PyCryptodome 3.23.0 | 是/是 | 是 | 是/是 | 否 | 否 | 接收端交叉通过 | PARTIALLY_QUALIFIED |
| hpke.py 0.3.2 | 是/是 | 顶层 API 无 X25519 | — | — | — | 不适用 | REJECTED |
| rfc9180 0.3.0 | Alpha/是 | 声明支持 | 声明支持 | 未进入执行门 | 声明支持 | 未执行 | FUTURE_ONLY |
| cryptography 49.0.0 | 是/是 | 当前路径不完整 | 失败 | 不满足 | 未完成 | InvalidTag | REJECTED |
