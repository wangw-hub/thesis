# 04 实验结果图审计

全部 13 张实验结果图由冻结正式数据重新绘制；Pilot/Formal 不混用；统计口径与冻结分析一致；横坐标均采用分面/分组/有限刻度，无标签堆叠。

| 图号 | 文件 | 数据源 | 指标 | 呈现方式 | 横坐标可读性 |
|---|---|---|---|---|---|
| 图4 | `m6-exp-fig4-match.png` | `time-policy/experiments/runs/e1_20260727_ec8b193_r3/processed/figure_4_4_data.csv` | 匹配查询中位时延 | 分面（按覆盖率），箱线图，横轴 3 个表示名 | 可读 |
| 图5 | `m6-exp-fig5-rep-size.png` | `同上 figure_4_2_data.csv` | 逻辑规模（对数坐标） | 分面箱线图 | 可读 |
| 图6 | `m6-exp-fig6-boundary.png` | `同上 figure_4_5_data.csv` | 压缩比与适用边界 | 分组箱线图，覆盖率分组 | 可读 |
| 图9 | `m6-exp-fig9-concurrency.png` | `RC2 figure-sources/figure-5-4-concurrency.csv` | 并发度效应 | 折线图，4 种方法 | 可读 |
| 图10 | `m6-exp-fig10-latency.png` | `RC2 figure-sources/figure-5-2-run-latency.csv` | 运行级时延分布 | 小提琴图+箱线 | 可读 |
| 图11 | `m6-exp-fig11-locality.png` | `RC2 figure-sources/figure-5-6-locality-cache.csv` | 局部性与缓存 | 双面板柱状图 | 可读 |
| 图12 | `m6-exp-fig12-stage.png` | `RC2 figure-sources/figure-5-7-stage-share.csv` | 阶段占比 | 堆叠柱状图（96-100%） | 可读 |
| 图13 | `m6-exp-fig13-paired.png` | `RC2 figure-sources/figure-5-3-paired-effects.csv` | 配对 Bootstrap CI | 误差线图 | 可读 |
| 图14 | `m6-exp-fig14-frag.png` | `RC2 figure-sources/figure-5-5-fragmentation.csv` | 碎片率效应 | 折线图 | 可读 |
| 图17 | `m6-exp-fig17-e1-paths.png` | `experiments/r3/formal/analysis/*.json` | 四类路径时延 | 误差线图，4 个路径名 | 可读 |
| 图18 | `m6-exp-fig18-e2-header.png` | `同上 + i11/formal-config-matrix.json` | 仅密文头更新规模 | 分组误差线图 | 可读 |
| 图19 | `m6-exp-fig19-e3-body.png` | `同上` | 密文主体轮换规模 | 分组误差线图 | 可读 |
| 图20 | `m6-exp-fig20-e5-recovery.png` | `同上` | 故障恢复时延 | 柱状误差线图 | 可读 |

结论：UNREADABLE_X_AXIS = 0；DATA_SOURCE_UNVERIFIED = 0；PILOT_MIXED_WITH_FORMAL = 0。
