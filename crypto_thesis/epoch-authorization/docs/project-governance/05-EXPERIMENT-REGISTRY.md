# Experiment Registry

| Experiment | Status | Formal result | Records/configs | Evidence |
|---|---|---:|---:|---|
| E1 policy representation | COMPLETED | yes | frozen in time-policy run | Research Content 1 formal report |
| Local authorization prototype | TESTED | no | 97 pytest tests passed in current repo | `tests/` |
| Infrastructure validation chain | VALIDATED | infrastructure only | 4 validators + 1 RPC | old-chain reports |
| PostgreSQL shared Nonce | VALIDATED | security evidence | 50/100/500, one success each | Stage B reports |
| Formal authorization chain | VALIDATED | system evidence | chainId 2026072901 | formal-chain F5-F10 evidence |
| PILOT_ONLY authorization run | PILOT_ONLY | no | 108 configs / 3,780 records | `experiments\runs\pilot_multihost_20260729_990acbe` |
| Formal performance experiment V13 | COMPLETED | yes | 108 factors / 324 seeded / 9,720 runs / 77,760 requests / 233,280 reads | `experiments/runs/formal_auth_multihost_rerun_v13_20260729T073007Z_8a3d795` |

PILOT_ONLY raw SHA-256: `a4d0fcb12de587afe31e8af49854a9db7bcc40a04e5ef2a38865cd1c7d4d27b3`.

| R2 first formal performance | INVALIDATED_PROTOCOL_DEVIATION | no | 324 seeded configs / 103,680 records | `experiments\runs\formal_auth_multihost_20260729_34af4ff` |

The row above is superseded by strict review: status is
`INVALIDATED_MATERIAL_PROTOCOL_DEVIATION`; the immutable data are retained for audit
but are not thesis-formal performance evidence.

The V13 request SHA-256 is
`00dbdc62c21a7c12143394118df5dc00bbe7108d822a4af41bd6a96aa89cc4ce`;
its raw artifact index is
`3cb273c3d1938fb4af2dee4d9f0c78f69033380efd0c37f68ae3258990720680`.

Chapter 5 is finalized from this V13 evidence. No additional experiment was run
for chapter finalization, and no V13 raw record was changed.

> Updated 2026-08-05：RC3 实验（I9 Pilot 93/93、I11 Formal 180 RUNs）在
> `epoch-authorization-r3-prep` 工作树完成；旧行“Research Content 3 experiments
> NOT_STARTED”标记为 **SUPERSEDED（本仓库范围）**。
