# RQ-1 Result

E1（4 configs，20 RUN）：valid 20/20，state consistency 20/20，wrong material release 0。

在受控 Formal 环境下，E1 的 20 个 RUN 全部通过冻结不变量：状态更新与幂等性检查通过、链/数据库/对象最终状态一致、无错误材料释放。这是实验验证而非形式化证明。

各配置中位数/95% CI 见 `formal-rq-results.json`（E1-C1..C4）。
