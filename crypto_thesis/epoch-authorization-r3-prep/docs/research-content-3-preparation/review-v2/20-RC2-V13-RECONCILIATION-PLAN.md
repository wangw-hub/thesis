# 研究内容二 V13 结束后的只读对账计划

## 触发条件

仅在主任务正式生成 V13 最终完整性审计、运行级配对统计和严格审稿结论后执行。本轮不读取、分析或猜测 V13 结果。

## 对账输入

- V13 最终审计报告和主任务明确冻结的 Git SHA；
- 最终 `BesuStateGateway` 请求边界与 `chain_read` 行为；
- Issuer、Verifier、CAP2、PostgreSQL schema、拒绝顺序和服务配置；
- 研究内容二最终状态及 Artifact SHA。

## 十项核对

| ID | 核对项 | 允许结果 | 触发设计修订的差异 |
|---|---|---|---|
| R-01 | BesuStateGateway | 只改变性能采集或内部实现 | 请求/响应语义、UNKNOWN 或确认策略变化 |
| R-02 | chain_read | fail-closed 语义不变 | 降级、缓存或错误分类变化 |
| R-03 | Verifier | CAP2 校验输入输出不变 | 校验顺序或字段含义变化 |
| R-04 | Issuer | nonce、链状态确认和签发边界不变 | 在不确定状态签发或材料释放边界变化 |
| R-05 | PostgreSQL | 仅实验表/索引变化 | 授权、nonce 或审计表语义变化 |
| R-06 | CAP2 | 字段和 canonical signing bytes 不变 | 字段新增、删除、重编码或 chain binding 变化 |
| R-07 | 拒绝顺序 | 安全结果保持 fail-closed | 任何可接受旧状态的路径 |
| R-08 | 服务配置 | 合约地址、chainId 配置边界清晰 | 隐式默认值或多链语义变化 |
| R-09 | Git HEAD | 可定位最终冻结提交 | 无法定位或工作区证据不洁净 |
| R-10 | RC2 最终状态 | 最终审稿通过并记录限制 | 仍要求重跑、接口未冻结或证据失效 |

## 差异分类

1. **PERFORMANCE_ONLY**：只改变采集、日志或性能实现，不改变协议接口；R3 文档无需重构，只更新依赖 SHA。
2. **COMPATIBLE_INTERFACE_REFINEMENT**：类型或错误枚举细化但语义不变；更新适配说明和契约测试。
3. **PROTOCOL_INTERFACE_CHANGE**：CAP2、状态字段、签发/验证或 fail-closed 语义变化；暂停准入，重新执行 02、03、07、09、18 的差异审查。
4. **EVIDENCE_INVALIDATING_CHANGE**：需要修改 RC2 核心语义或使其正式证据失效；触发硬停止，不进入 R3 实现。

## 输出

未来单独生成 `RC2-V13-RECONCILIATION-REPORT.md`，记录输入 SHA、逐项差异、分类、需要重开的设计问题和最终准入建议。对账只读，不在主仓库执行 checkout、stash、merge、rebase 或提交。
