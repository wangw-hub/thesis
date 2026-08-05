# EXPERIMENT DATA MANIFEST — 实验数据资产清单

> 本清单记录正式/预实验数据资产的本地位置、运行规模与证据哈希状态。
> 公开 GitHub 仓库**不包含**原始实验数据；本地资料完整。路径相对仓库根 `D:\Research`。
> SHA-256 均采用既有冻结证据（`HASH_NOT_RECOMPUTED_EXISTING_EVIDENCE_USED`），未重新计算数百 GB 文件。

## RC1 — E1 正式实验（time-policy）

| 字段 | 值 |
|---|---|
| datasetId | RC1-E1-FORMAL |
| researchContent | 1 |
| experiment | E1（E1-A 主效应 108 + E1-B 冗余 36 + E1-C 边界 24 = 168 配置） |
| status | FORMAL_ACCEPTED（E1_experiment_acceptance.md 8/8 退出标准通过） |
| localPath | `crypto_thesis/time-policy/experiments/runs/e1_20260727_ec8b193_r3/` |
| runCount | 168 配置 / 15,120 正式记录（E1-C 补充 540 记录在 `e1c_power2_supplement_20260727_87d0010/`） |
| rawAvailable | 是（`raw/results.csv`、`raw/shard_*.csv`、`datasets/e1_samples.jsonl`，只读冻结） |
| analysisAvailable | 是（`processed/` 统计摘要与图表数据） |
| archiveAvailable | 本地 Git 历史（`.git-backups/time-policy.git`） |
| sha256 | 既有证据：raw_data_audit.md / E1-C 审计记录（HASH_NOT_RECOMPUTED_EXISTING_EVIDENCE_USED） |
| formalOrPilot | FORMAL |
| includedInThesis | 是（第四章 V1.2，图 4-2..4-5、表 4-2/4-4） |
| authoritative | 是 |
| notes | 冻结提交 `ec8b193`；pilot_20260727_* 为 PILOT_ONLY，不得混用 |

## RC2 — V13 正式复跑（epoch-authorization）

| 字段 | 值 |
|---|---|
| datasetId | RC2-V13-FORMAL |
| researchContent | 2 |
| experiment | formal_auth_multihost_rerun_v13 |
| status | FORMAL_ACCEPTED（completeness accepted=true） |
| localPath | `crypto_thesis/epoch-authorization/experiments/runs/formal_auth_multihost_rerun_v13_20260729T073007Z_8a3d795/` |
| runCount | 108 因子配置 / 324 种子配置 / 9,720 run blocks / 77,760 请求 / 233,280 链读 |
| rawAvailable | 是（`raw/requests.jsonl` 130 MB、`raw/chain-reads.jsonl` 180 MB、`raw/batches.jsonl`，只读） |
| analysisAvailable | 是（`analysis/`：independent-analysis-summary、paired-run-differences、factor-effects 等） |
| archiveAvailable | 本地 Git 历史 + formal-artifact-sha256.json |
| sha256 | requests `00dbdc62c2…`；chain-reads `3e7f5c49…`；raw index `3cb273c3…`（既有证据，未重算） |
| formalOrPilot | FORMAL |
| includedInThesis | 是（第五章 8 图 / 2 机制图 / 6 表） |
| authoritative | 是（RC2 唯一可引用正式性能证据） |
| notes | 首轮 `formal_auth_multihost_20260729_34af4ff`（103,680 记录）为 INVALIDATED，仅审计保留 |

## RC2 — 其他资产

| datasetId | 类型 | 位置/规模 |
|---|---|---|
| RC2-PILOT | PILOT_ONLY | `crypto_thesis/epoch-authorization/experiments/runs/pilot_multihost_20260729_990acbe/`（108 配置 / 3,780 记录；SHA `a4d0fcb1…`） |
| RC2-INFRA-CHAIN | 基础设施验收 | `crypto_thesis/epoch-authorization/infra/besu-qbft-multihost/`（chainId 2026072801，4V+1RPC） |
| RC2-FORMAL-CHAIN | 正式授权链 | `infra/besu-qbft-multihost/formal-authorization-chain/`（chainId 2026072901，genesis SHA `7d431f01…`） |
| RC2-INVALIDATED | INVALIDATED | `crypto_thesis/epoch-authorization/experiments/runs/formal_auth_multihost_20260729_34af4ff/`（103,680 记录，协议偏差） |

## RC3 — I9 Pilot（r3-prep）

| 字段 | 值 |
|---|---|
| datasetId | RC3-I9-PILOT |
| researchContent | 3 |
| experiment | I9 Pilot（P9-A/B/C/D） |
| status | COMPLETED_PILOT_ONLY（93/93 valid；P9-A 8、P9-B 45、P9-C 16、P9-D 24） |
| localPath | `crypto_thesis/epoch-authorization-r3-prep/experiments/r3/i9-pilot/`（约 173 MB） |
| rawAvailable | 是（`i9-run-index.json` 含 runId/attemptId/rawManifestDigest；rawShaErrors=0） |
| sha256 | Pilot baseline digest `6de936e9d7ef8357530b7361e0b06a862c0474212e1147b69f5dd67fc4779d8a`（既有证据） |
| formalOrPilot | PILOT_ONLY |
| includedInThesis | 作为工程开发验证（不构成正式结论） |
| authoritative | 否（冻结基线，IMMUTABLE_PILOT_BASELINE） |

## RC3 — I11 Formal（r3-prep）

| 字段 | 值 |
|---|---|
| datasetId | RC3-I11-FORMAL |
| researchContent | 3 |
| experiment | I11 Formal（E1–E5；29 冻结配置） |
| status | FORMAL_ACCEPTED（145/145 有效；invalid/replacement/excluded=0） |
| localPath | `crypto_thesis/epoch-authorization-r3-prep/experiments/r3/formal/`（raw 11 MB / 3,780 文件；analysis、manifests、figures、tables） |
| runCount | 35 warmup + 145 measured = 180 sealed RUNs（E1 20 / E2 30 / E3 45 / E4 10 / E5 40） |
| rawAvailable | 是（`raw/` 180 个 runId 目录；远程权威与本地镜像一致，0 missing/0 extra） |
| analysisAvailable | 是（`analysis/`：accepted-run-index、descriptive-statistics、effect-sizes、bootstrap 等） |
| sha256 | 每 RUN rawManifestDigest 记录于 `i11/formal-run-index.json`（既有证据，未重算） |
| formalOrPilot | FORMAL |
| includedInThesis | 是（第六章：3 正式图 + 5 正式表，来自 `experiments/r3/formal/figures|tables/i12-final/`） |
| authoritative | 是 |
| notes | attempt `FORMAL_20260802T095534Z_4d12daf`；执行 Git SHA `4d12daf`；preregistration digest `5c957cdf…` |

## 汇总

| 数据集 | Formal? | 记录规模 | 是否入论文 | 权威 |
|---|---|---|---|---|
| RC1 E1 | 是 | 168 配置 / 15,120 记录 | 是（第 4 章） | 是 |
| RC2 V13 | 是 | 77,760 请求 / 233,280 链读 | 是（第 5 章） | 是 |
| RC2 首轮 | 否（INVALIDATED） | 103,680 记录 | 否 | 否（审计） |
| RC3 I9 Pilot | 否（PILOT_ONLY） | 93 RUNs | 否（开发验证） | 否 |
| RC3 I11 | 是 | 180 RUNs（145 measured） | 是（第 6 章） | 是 |
