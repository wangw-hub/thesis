# Formal Run Integrity

从最终 raw 镜像重算：

- Warmup：35；Measured：145；统计样本：145
- E1 20 / E2 30 / E3 45 / E4 10 / E5 40
- VALID_SUCCESS 120；VALID_EXPECTED_FAIL_CLOSED 25；Excluded 0；Replacement 0
- duplicate runId 0；Pilot mixed 0；warmup mixed 0；superseded mixed 0
- raw/mirror SHA errors 0/0；wrong material release 0；state consistency violations 0；invalid 0

VALID_EXPECTED_FAIL_CLOSED 是预注册故障场景下的有效 Formal 样本，不是实验失败。
