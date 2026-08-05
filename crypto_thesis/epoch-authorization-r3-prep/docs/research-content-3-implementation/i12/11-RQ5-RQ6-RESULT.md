# RQ-5/RQ-6 Result

E5（8 configs，40 RUN）全部 valid。Baseline-R = LOCAL_ONLY/NONE（匹配输入与语义）。

| fault | replica | n | disposition | recovery disposition | duration median (ms) | recovery median (ms) |
|---|---|---:|---|---|---:|---:|
| BOTH_MISSING | LOCAL_ONLY | 5 | VALID_EXPECTED_FAIL_CLOSED | FAIL_CLOSED | 3112.2 | N/A |
| BOTH_MISSING | KUBO_REPLICA | 5 | VALID_EXPECTED_FAIL_CLOSED | FAIL_CLOSED | 3129.6 | N/A |
| CID_MISMATCH | LOCAL_ONLY | 5 | VALID_EXPECTED_FAIL_CLOSED | FAIL_CLOSED | 3107.4 | N/A |
| CID_MISMATCH | KUBO_REPLICA | 5 | VALID_EXPECTED_FAIL_CLOSED | FAIL_CLOSED | 3125.6 | N/A |
| CORRUPT_RESTORE | LOCAL_ONLY | 5 | VALID_EXPECTED_FAIL_CLOSED | UNRECOVERABLE | 3163.5 | N/A |
| CORRUPT_RESTORE | KUBO_REPLICA | 5 | VALID_SUCCESS | CONSISTENT | 3132.6 | N/A |
| NONE | LOCAL_ONLY | 5 | VALID_SUCCESS | CONSISTENT | 3184.3 | N/A |
| NONE | KUBO_REPLICA | 5 | VALID_SUCCESS | CONSISTENT | 3136.1 | N/A |

配对效应（LOCAL vs KUBO，同 fault/seed）见 `formal-rq-results.json` 与 `formal-analysis/effect-sizes.json`；跨语义不比较。
