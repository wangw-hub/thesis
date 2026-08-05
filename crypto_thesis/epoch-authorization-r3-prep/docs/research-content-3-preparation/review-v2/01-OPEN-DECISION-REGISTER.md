# 14项开放决策登记

| ID | 决策 | 分类 | 推荐与证据 | V13/用户/原型 | 状态/关闭标准 |
|---|---|---|---|---|---|
| OD-01 | HPKE Python库 | REQUIRES_MINIMAL_PROTOTYPE | pyca/cryptography 49.0.0原生HPKE | 否/否/是 | RFC向量通过后关闭 |
| OD-02 | HPKE suite | REQUIRES_MINIMAL_PROTOTYPE | Base/X25519/HKDF-SHA256/AES-128-GCM，直接对应RFC A.1 | 否/否/是 | 互操作/负向测试后关闭 |
| OD-03 | CK寿命 | CLOSED_BY_DESIGN_EVIDENCE | 每Body版本唯一CK；Header更新不轮换CK | 否/否/否 | CLOSED |
| OD-04 | KEK_e | REJECTED_OPTION | 首版不引入；它不消除每用户封装且增加密钥/恢复状态 | 否/否/否 | REJECTED；仅新证据可重开 |
| OD-05 | Header粒度 | CLOSED_BY_DESIGN_EVIDENCE | 每资源一个Header版本、接收者envelope列表 | 否/否/否 | CLOSED |
| OD-06 | envelope组织 | REQUIRES_MINIMAL_PROTOTYPE | V1内嵌排序列表；规模上限/外部分片阈值由I1验证 | 否/否/是 | 字节与解析上限证据 |
| OD-07 | Header格式 | CLOSED_BY_DESIGN_EVIDENCE | RFC 8785 JCS + I-JSON限制 + Schema拒绝未知字段 | 否/否/否 | CLOSED |
| OD-08 | IPFS时点 | CLOSED_BY_DESIGN_EVIDENCE | I8，Local闭环之后 | 否/否/否 | CLOSED |
| OD-09 | 链状态 | CLOSED_BY_DESIGN_EVIDENCE | 独立HeaderRegistry；S2 V2迁移不采用 | 否/否/否 | CLOSED |
| OD-10 | 提交协议 | CLOSED_BY_DESIGN_EVIDENCE | 授权先确认、链下候选、Registry单次COMMITTED | 否/否/否 | CLOSED |
| OD-11 | 撤销模式 | CLOSED_BY_DESIGN_EVIDENCE | 立即停止授权+逐资源异步Header恢复 | 否/否/否 | CLOSED |
| OD-12 | 确认深度 | BLOCKED_ON_RC2_V13 | 沿用R2最终confirmed-state定义，不在活跃运行中猜测 | 是/否/否 | V13接口冻结后对账 |
| OD-13 | KeyStore | USER_DECISION_REQUIRED | 开发期OS受限存储；正式期HSM/外部KMS需部署资源选择 | 否/是/否 | 用户选择威胁/成本档 |
| OD-14 | 孤儿清理 | CLOSED_BY_DESIGN_EVIDENCE | 隔离保留期+引用/receipt双重扫描；永不清理被引用对象 | 否/否/否 | CLOSED |

汇总：关闭8；依赖V13 1；用户决策1；最小原型3；拒绝1。
