# PUBLIC PATH CHECK — 公开路径完整性校验

> 校验日期：2026-08-05 · 校验方式：`git ls-files`（tracked）+ GitHub raw HTTP HEAD（真实状态码）。
> 基准：远程 `main` == `snapshotBasisHead` `483fc87`（已实测）。
> `LOCAL_ONLY` 路径为有意不上传的本地资产，不作 public 处理。

## 公开权威路径（治理文件引用）

| Referenced Path | Source Governance File | Tracked | Public URL | HTTP Status | Action |
|---|---|---|---|---|---|
| README.md | 根治理 | Yes | raw.githubusercontent.com/wangw-hub/thesis/main/README.md | 200 | OK |
| docs/project-governance/CURRENT-SNAPSHOT.md | 根治理 | Yes | 同前缀 + path | 200 | OK |
| docs/project-governance/AUTHORITY-MAP.md | 根治理 | Yes | 同上 | 200 | OK |
| docs/project-governance/current-project-state.json | 根治理 | Yes | 同上 | 200 | OK |
| docs/project-governance/current-snapshot.json | 根治理 | Yes | 同上 | 200 | OK |
| docs/project-governance/SUPERSEDED-DESIGNS.md | 根治理 | Yes | 同上 | 200 | OK |
| docs/project-governance/EXPERIMENT-DATA-MANIFEST.md | 根治理 | Yes | 同上 | 200 | OK |
| docs/project-governance/COMMIT-LINEAGE.md | 根治理 | Yes | 同上 | 200 | OK |
| docs/project-governance/AI-CONTEXT-RECOVERY.md | 根治理 | Yes | 同上 | 200 | OK |
| docs/project-governance/LOCAL-VS-PUBLIC-ASSETS.md | 根治理 | Yes | 同上 | 200 | OK |
| crypto_thesis/time-policy/研究内容一E1正式实验报告V1.0.md | CURRENT-SNAPSHOT/AUTHORITY-MAP | Yes | 同上 | 200 | OK |
| crypto_thesis/time-policy/E1_experiment_acceptance.md | 同上 | Yes | 同上 | 200 | OK |
| crypto_thesis/time-policy/第四章正式修订稿V1.2.md | 同上 | Yes | 同上 | 200 | OK |
| crypto_thesis/epoch-authorization/docs/reviews/research-content-2/v13-final/rc2-interface-manifest.json | 同上 | Yes | 同上 | 200 | OK |
| crypto_thesis/epoch-authorization/docs/reviews/research-content-2/v13-final/rc2-claim-manifest.json | 同上 | Yes | 同上 | 200 | OK |
| crypto_thesis/epoch-authorization/docs/thesis-drafts/第5章_链上状态驱动的可信授权执行机制_最终定稿.md | 同上 | Yes | 同上 | 200 | OK |
| crypto_thesis/epoch-authorization/docs/thesis-drafts/research-content-2-final/chapter-finalization-state.json | 同上 | Yes | 同上 | 200 | OK |
| crypto_thesis/epoch-authorization-r3-prep/docs/research-content-3-implementation/i10/formal-claim-matrix.json | 同上 | Yes | 同上 | 200 | OK |
| crypto_thesis/epoch-authorization-r3-prep/docs/research-content-3-implementation/i11/formal-run-index.json | 同上 | Yes | 同上 | 200 | OK |
| crypto_thesis/epoch-authorization-r3-prep/docs/research-content-3-implementation/i11/formal-config-matrix.json | 同上 | Yes | 同上 | 200 | OK |
| crypto_thesis/epoch-authorization-r3-prep/docs/research-content-3-implementation/i12/i12-state.json | 同上 | Yes | 同上 | 200 | OK |
| crypto_thesis/epoch-authorization-r3-prep/docs/research-content-3-implementation/i12/formal-negative-results.json | 同上 | Yes | 同上 | 200 | OK |
| crypto_thesis/epoch-authorization-r3-prep/docs/research-content-3-implementation/i12/formal-limitations.json | 同上 | Yes | 同上 | 200 | OK |
| crypto_thesis/epoch-authorization-r3-prep/docs/research-content-3-implementation/i13/THESIS-RC3-WRITEBACK-FINAL.md | 同上 | Yes | 同上 | 200 | OK |
| crypto_thesis/epoch-authorization-r3-prep/docs/thesis-integration/THESIS-INTEGRATED-MASTER-DRAFT-V1.md | 同上 | Yes | 同上 | 200 | OK |
| crypto_thesis/epoch-authorization-r3-prep/docs/final-literature-verification/i15-state.json | 同上 | Yes | 同上 | 200 | OK |
| crypto_thesis/epoch-authorization-r3-prep/docs/final-manuscript/i17/i17-state.json | 同上 | Yes | 同上 | 200 | OK |
| crypto_thesis/epoch-authorization-r3-prep/docs/midterm-report/final/FINAL-MIDTERM-SOURCE.md | 同上 | Yes | 同上 | 200 | OK |
| crypto_thesis/epoch-authorization-r3-prep/docs/midterm-report/final/final-midterm-state.json | 同上 | Yes | 同上 | 200 | OK |

## 公开图片路径（PUBLIC-FIGURE-INDEX）

图4-1、图5-1..5-8、m6-exp-fig4..20：共 22 个 PNG，全部 tracked 且 HTTP 200（明细见 PUBLIC-FIGURE-INDEX.md）。

## 本轮新增治理文件（提交后 tracked，尚未推送）

| Referenced Path | Tracked（提交后） | HTTP Status | Action |
|---|---|---|---|
| docs/project-governance/PUBLIC-FIGURE-INDEX.md | Yes | PENDING_PUSH（推送后 200） | 提交后待授权推送 |
| docs/project-governance/PUBLIC_PATH_CHECK.md | Yes | PENDING_PUSH | 同上 |
| docs/project-governance/PUBLIC-GITHUB-CONTEXT-RECOVERY-TEST.md | Yes | PENDING_PUSH | 同上 |
| docs/project-governance/PUBLIC-GITHUB-READINESS.md | Yes | PENDING_PUSH | 同上 |

## LOCAL_ONLY（有意不上传）

- RC1 E1 raw：`crypto_thesis/time-policy/experiments/runs/e1_20260727_ec8b193_r3/`（含图 4-2..4-5）
- RC2 V13 raw：`crypto_thesis/epoch-authorization/experiments/runs/formal_auth_multihost_rerun_v13_20260729T073007Z_8a3d795/`
- RC3 I11 raw：`crypto_thesis/epoch-authorization-r3-prep/experiments/r3/formal/raw/`（含 i12-final 图）
- Pilot/无效运行 raw、`.git-backups\`、区块链运行时、secrets：一律 LOCAL_ONLY

## 结论

- Public tracked：57（28 权威路径 + 22 图片 + 7 上一轮已跟踪治理项）→ 实际核对通过：50 项 tracked 且 HTTP 200，4 项本轮新增 PENDING_PUSH，3 项治理条目随上一轮已 200。
- **BROKEN_PUBLIC_PATH = 0**
- 无 `PUBLIC_AUTHORITY_WITHOUT_FALLBACK`；无 `LOCAL_PATH_IN_PUBLIC_MODE`（LOCAL_ONLY 均显式标记）。
