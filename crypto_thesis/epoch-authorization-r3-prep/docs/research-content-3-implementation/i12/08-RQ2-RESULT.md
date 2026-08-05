# RQ-2 Result

E2（HEADER_ONLY，6 configs，30 RUN），全部 valid。每配置 median/IQR/95% bootstrap CI（ms）：

| config (recipient/affected) | median | IQR | 95% CI |
|---|---:|---:|---:|
| recipient=32,affected=1 | 5144.2 | 116.8 | 5002-5235 |
| recipient=2,affected=1 | 5117.2 | 135.2 | 4949-5164 |
| recipient=2,affected=4 | 5129.7 | 36.7 | 5016-5178 |
| recipient=32,affected=4 | 5130.3 | 48.6 | 5039-5166 |
| recipient=8,affected=4 | 5114.7 | 89.8 | 5009-5153 |
| recipient=8,affected=1 | 5119.0 | 5.6 | 4985-5183 |

- recipient 2→32（affected=1）：median 差 27.0 ms，ratio 1.005，Cliff's delta 0.12
- affected 1→4（recipient=2）：median 差 12.5 ms，ratio 1.002，Cliff's delta 0.20

结论：在该受控环境中，HEADER_ONLY 端到端开销以链上交易等待为主，recipient/affected 因素效应小；仅为描述性观察，不与其他语义类比较。
