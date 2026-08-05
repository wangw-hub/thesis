# MAJOR问题统一登记

| ID | 原始问题 | RQ/模块 | 分类 | 证据与处理 | V13/用户/原型 | 关闭标准 | 状态 |
|---|---|---|---|---|---|---|---|
| M-01 | HPKE库与suite未冻结 | RQ3-1/ CryptoService | REQUIRES_MINIMAL_PROTOTYPE | pyca/cryptography 49.0.0已提供RFC 9180 HPKE；推荐Base/X25519/HKDF-SHA256/AES-128-GCM | 否/否/是 | RFC Appendix A.1向量、负向测试、许可证/后端记录通过 | OPEN_GATED |
| M-02 | 分块nonce、上限、向量未冻结 | RQ3-1/BodyFormat | CLOSED_BY_DESIGN_EVIDENCE | 每Body新随机256-bit CK；96-bit nonce=`64-bit nonceBase || uint32_be(chunkIndex)`；chunkCount≤2^32-1；128-bit tag；AAD绑定资源和完整分块位置 | 否/否/否 | [密码决定](04-CRYPTOGRAPHIC-SUITE-DECISION.md)与Schema一致 | CLOSED |
| M-03 | V2迁移和双地址验证不闭合 | RQ3-2/链状态 | CLOSED_BY_DESIGN_EVIDENCE | 拒绝修改或迁移AuthorizationState；采用独立HeaderRegistry，在提交时只读校验旧合约 | 否/否/否 | S1–S5比较与客户端双合约不变量完整 | CLOSED |
| M-04 | UNKNOWN交易、重组、孤儿恢复待证 | RQ3-4/Recovery | REQUIRES_FORMAL_IMPLEMENTATION | 先receipt与链状态对账、operationId去重、blockHash游标、候选不可接受；正确性需I4–I7故障注入 | 否/否/否 | E8全部崩溃点零不变量违反 | OPEN_GATED |
| M-05 | E6–E9实验单位/计时/排除未冻结 | RQ3-6/Experiment | CLOSED_BY_DESIGN_EVIDENCE | 运行级单位、批次计时、缓存分层、配对键、排除和原始证据在[实验蓝图](14-TEST-AND-EXPERIMENT-BLUEPRINT-V1.md)冻结 | 否/否/否 | 预注册模板字段齐全且不预填结果 | CLOSED |
| M-06 | 贡献与成本/撤销措辞可能夸大 | 全部/论文 | CLOSED_BY_DESIGN_EVIDENCE | 贡献定位为可验证系统组合；单Header与Body解耦，不声称总成本O(1)或追回既得秘密 | 否/否/否 | 准入包、主张矩阵与盲审一致 | CLOSED |
| M-07 | 接收者线性膨胀及管理员/终端边界 | RQ3-3/Header | ACCEPTED_LIMITATION | 每接收者一次HPKE封装导致O(N)；管理员、终端和既得CK不在可撤回边界；E7如实测量 | 否/否/否 | 论文限制、E7变量和拒绝选项一致 | ACCEPTED |

汇总：关闭4；最小原型1；正式实现1；接受限制1；依赖V13为0；用户决策为0。接受限制不等于问题消失。
