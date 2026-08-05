# RQ-3 Result

E3（BODY_ROTATION，9 configs，45 RUN），全部 valid。每配置 median/IQR/95% CI（ms）：

| config (body/recipient) | median | IQR | 95% CI |
|---|---:|---:|---:|
| body=1048576,recipient=32 | 5071.3 | 42.1 | 5047-5155 |
| body=1048576,recipient=2 | 4978.2 | 65.8 | 4464-5137 |
| body=1048576,recipient=8 | 5061.7 | 79.1 | 5030-5150 |
| body=8388608,recipient=32 | 5104.8 | 34.7 | 4998-5161 |
| body=65536,recipient=32 | 5067.1 | 136.7 | 4843-5154 |
| body=8388608,recipient=2 | 6696.3 | 1759.7 | 5063-7111 |
| body=65536,recipient=8 | 5095.0 | 4.6 | 5072-5142 |
| body=65536,recipient=2 | 5083.2 | 9.5 | 5061-5106 |
| body=8388608,recipient=8 | 5089.9 | 37.1 | 5046-5217 |

- body 64KiB→8MiB（recipient=2）：median 差 1613.1 ms，ratio 1.317，Cliff's delta 0.60
- 密码正确性：old CK cannot decrypt new body 45/45；body digest changed 45/45；全部 45/45 valid。

性能与正确性分开表述：性能为描述性工程测量；正确性为逐 RUN 不变量通过。
