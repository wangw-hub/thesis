# RC3 实验图数据审计

- E1 配置数：4（四路径）；E2 配置数：6（HEADER_ONLY 6 配置）；E3 配置数：9（BODY_ROTATION 9 配置）；E5 配置数：8
- 图17 数据 = E1 四路径；图18 数据 = E2 HEADER_ONLY；图19 数据 = E3 BODY_ROTATION；图20 数据 = E5 恢复

## 图17 E1 四类生命周期路径端到端时延

- figure: 图17
- experiment: E1
- configs: 4
- runs: 20
- x_axis: INITIAL / BODY_ROTATION / REVOCATION / RESTORE
- y_axis: 端到端中位时延 (ms)
- aggregation: median + Bootstrap 95% CI
- source: experiments/r3/formal/analysis/descriptive-statistics.json + bootstrap-results.json + i11/formal-config-matrix.json
- consistent_with_text: True

## 图18 E2 HEADER_ONLY 规模影响

- figure: 图18
- experiment: E2
- configs: 6
- runs: 30
- x_axis: 接收者数 2/8/32
- group_by: 受影响资源数 1/4
- y_axis: 端到端中位时延 (ms)
- aggregation: median + Bootstrap 95% CI
- source: 同上
- consistent_with_text: True

## 图19 E3 BODY_ROTATION 规模影响

- figure: 图19
- experiment: E3
- configs: 9
- runs: 45
- x_axis: Body 64 KiB/1 MiB/8 MiB
- group_by: 接收者 2/8/32
- y_axis: 端到端中位时延 (ms)
- aggregation: median + Bootstrap 95% CI
- source: 同上
- consistent_with_text: True

## 图20 LOCAL_ONLY 与 KUBO_REPLICA 恢复时延对比

- figure: 图20
- experiment: E5
- configs: 4
- runs: 40
- x_axis: LOCAL_ONLY/KUBO_REPLICA × 故障类别
- y_axis: 恢复端到端中位时延 (ms)
- aggregation: median + Bootstrap 95% CI
- source: 同上
- consistent_with_text: True
