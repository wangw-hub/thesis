# I1 后拟议治理更新

- 研究内容三状态建议：`I1_REQUIRES_REVISION`。
- I1 已获批准并开始，但未完成；不得进入 I2。
- FATAL：所选 cryptography 49.0.0 公开 HPKE API 无法执行 RFC 9180 A.1.1
  非空 AAD 原始向量，也不暴露确定性封装或 exporter。
- 必须重开 I0 的最小 HPKE 依赖候选审查；不得自行拼装 HPKE。
- KeyStore 方案 A、RC2 冻结接口和“不提出新密码原语”的论文定位不变。
- 本轮未形成性能、安全证明或正式实验结论。

