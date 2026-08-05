# Formal Statistical Reproduction

从最终 accepted raw 重新执行冻结统计 pipeline（RUN 单位、bootstrap 10000、95% percentile CI、median difference/ratio/Cliff's delta、Holm within RQ family）：

- descriptive 复现：PASS
- bootstrap 复现：PASS
- effect size 复现：PASS

未引入未预注册的显著性检验；所有数字来自 `formal-analysis/*.json` 与 raw 索引。
