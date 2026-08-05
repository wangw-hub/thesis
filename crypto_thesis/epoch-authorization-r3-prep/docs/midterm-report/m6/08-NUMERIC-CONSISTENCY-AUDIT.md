# 08 数值一致性审计

## 1. 核验范围

- 研究内容一：168 配置、15120 条记录、81 项测试、98.61% 覆盖率、查询中位数（350.4/561.0/1984.7 ns）、逻辑字节中位数（24000/2808/3664）。
- 研究内容二：五节点链、108 因素配置、324 含种子配置、9720 运行块、77760 请求、233280 链读取、2430 配对、10000 次 Bootstrap、时延 196–199 ms、链读取 98.66%–98.80%。
- 研究内容三：29 配置、35 预热、145 有效运行、E1 中位 3080/5120/7118/3147 ms、E2 5115–5144 ms、E3 5083→6696 ms、E5 恢复 3112.2/3129.6 ms、错误材料释放 0。

## 2. 冻结数据对照

- RC3：`experiments/r3/formal/analysis/descriptive-statistics.json`（29 配置；E1-C1..C4 中位 3080/5120/7118/3147；E2-C1..C6 中位 5114.7–5144.2；E3-C1=5083.2、E3-C7=6696.3；恢复时长 3112.164/3129.640）与 `bootstrap-results.json`、`i11/formal-config-matrix.json` 一致。
- RC2：`figure-5-2-run-latency.csv`（B0/B1/C0/C1 运行块中位 196.128/196.583/198.682/198.939，均值 209.714/211.402/211.029/212.448）、`figure-5-3-paired-effects.csv`、`figure-5-4-concurrency.csv`、`figure-5-7-stage-share.csv` 一致。
- 恢复时长：`i12/formal-rq-results.json` recoveryTable（LOCAL_ONLY 3112.164024、KUBO_REPLICA 3129.640055）。

## 3. 本轮修正

- M5 表4（四种方法总体统计）B1/C0/C1 的时延、均值、吞吐量、缓存命中率、链读取占比与冻结 CSV 不一致，已按冻结 CSV 修正。
- M5 表5（配对比较）C1-C0、C0-B0 两行数值不一致，已按冻结 `figure-5-3-paired-effects.csv` 修正。
- 正文“吞吐量中位数 17.78～17.93 请求/s”修正为“17.7～18.0 请求/s”；缓存命中率补充节点缓存方法的 0.625/0.75/0.125 分布。

## 4. 结论

- 检查项 28 项，缺失 0 项（无）。
- WRONG_NUMERIC_VALUE = 0；INVENTED_DATA = 0；UNSUPPORTED_CLAIM = 0；FORBIDDEN_CLAIM = 0；PILOT_FORMAL_MIX = 0。
