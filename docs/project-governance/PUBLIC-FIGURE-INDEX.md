# PUBLIC FIGURE INDEX — 公开图片索引

> 用途：PUBLIC_GITHUB_MODE 的新 GPT 即使遇到论文 Markdown 中的本地绝对图片路径
> （如 `D:/Research/...`），仍可通过本索引找到公开版本或确认其不可公开。
> 本索引不修改任何冻结论文文件；不复制/生成大图。
> 路径均为仓库根相对路径；`PUBLIC` = GitHub 可访问（2026-08-05 实测 HTTP 200），
> `LOCAL_ONLY` = 仅本机存在（experiments 未上传）。

## RC1（第四章）

| Figure ID | Document | Meaning | Original local reference | Public repository image path | Availability |
|---|---|---|---|---|---|
| 图4-1 | `crypto_thesis/time-policy/第四章正式修订稿V1.2.md` | 确定性时间策略编译流程 | `D:/Research/crypto_thesis/time-policy/figures/图4-1确定性时间策略编译流程.png` | `crypto_thesis/time-policy/figures/图4-1确定性时间策略编译流程.png` | PUBLIC |
| 图4-2 | E1 正式实验报告 / 第四章 | 表示规模比较 | `D:/Research/crypto_thesis/time-policy/experiments/runs/e1_20260727_ec8b193_r3/figures/figure_4_2_representation_size.png` | — | LOCAL_ONLY（公开替代：E1 正式报告 + 验收文档） |
| 图4-3 | 同上 | 编译时间 | `.../figure_4_3_compile_time.png` | — | LOCAL_ONLY |
| 图4-4 | 同上 | 匹配时延 | `.../figure_4_4_match_latency.png` | — | LOCAL_ONLY |
| 图4-5 | 同上 | 适用边界 | `.../figure_4_5_applicability_boundary.png` | — | LOCAL_ONLY |

## RC2（第五章）

| Figure ID | Document | Meaning | Original local reference | Public repository image path | Availability |
|---|---|---|---|---|---|
| 图5-1 | `crypto_thesis/epoch-authorization/docs/thesis-drafts/第5章_链上状态驱动的可信授权执行机制_最终定稿.md` | 系统设计 | `research-content-2-final/figures/figure-5-1-design.png`（相对引用） | `crypto_thesis/epoch-authorization/docs/thesis-drafts/research-content-2-final/figures/figure-5-1-design.png` | PUBLIC |
| 图5-2 | 同上 | 端到端运行时延 | figure-5-2-run-latency.png | `.../figures/figure-5-2-run-latency.png` | PUBLIC |
| 图5-3 | 同上 | 配对方法差异 | figure-5-3-paired-effects.png | `.../figures/figure-5-3-paired-effects.png` | PUBLIC |
| 图5-4 | 同上 | 并发效应 | figure-5-4-concurrency.png | `.../figures/figure-5-4-concurrency.png` | PUBLIC |
| 图5-5 | 同上 | 碎片化效应 | figure-5-5-fragmentation.png | `.../figures/figure-5-5-fragmentation.png` | PUBLIC |
| 图5-6 | 同上 | 局部性/缓存 | figure-5-6-locality-cache.png | `.../figures/figure-5-6-locality-cache.png` | PUBLIC |
| 图5-7 | 同上 | 阶段占比 | figure-5-7-stage-share.png | `.../figures/figure-5-7-stage-share.png` | PUBLIC |
| 图5-8 | 同上 | 链稳定性 | figure-5-8-chain-stability.png | `.../figures/figure-5-8-chain-stability.png` | PUBLIC |

## RC3（第六章）

| Figure ID | Document | Meaning | Original local reference | Public repository image path | Availability |
|---|---|---|---|---|---|
| fig-rq2-header-only-duration | `crypto_thesis/epoch-authorization-r3-prep/docs/research-content-3-implementation/i12/15-FORMAL-FIGURE-INDEX.md` | E2 HEADER_ONLY 类内时长 | `experiments/r3/formal/figures/i12-final/fig-rq2-header-only-duration.png` | — | LOCAL_ONLY（公开替代：i12 图索引 + formal-figure-index.json） |
| fig-rq3-body-rotation-duration | 同上 | E3 BODY_ROTATION 类内时长 | `.../fig-rq3-body-rotation-duration.png` | — | LOCAL_ONLY（同上） |
| fig-rq5-recovery-local-kubo | 同上 | E5 LOCAL vs KUBO 恢复 | `.../fig-rq5-recovery-local-kubo.png` | — | LOCAL_ONLY（同上） |

## Midterm（FINAL-CLEAN）

| Figure ID | Document | Meaning | Original local reference | Public repository image path | Availability |
|---|---|---|---|---|---|
| m6-exp-fig4..20（13 图） | `crypto_thesis/epoch-authorization-r3-prep/docs/midterm-report/final/FINAL-MIDTERM-SOURCE.md`（图片嵌入 DOCX/PDF） | 匹配/表示规模/边界/并发/时延/局部性/阶段/配对/碎片化/E1 路径/E2 HEADER/E3 BODY/E5 恢复 | 嵌入 `crypto_thesis/epoch-authorization-r3-prep/docs/midterm-report/final/output/王威-…-最终固化版.docx/.pdf` | `crypto_thesis/epoch-authorization-r3-prep/docs/midterm-report/final/figures/m6-exp-fig4-match.png` … `m6-exp-fig20-e5-recovery.png` | PUBLIC |

## 汇总

- 登记图项：RC1 5（1 PUBLIC + 4 LOCAL_ONLY）、RC2 8（8 PUBLIC）、RC3 3（3 LOCAL_ONLY）、Midterm 13（13 PUBLIC）。
- Public available：22 · Local-only：7 · **PUBLIC_NOT_AVAILABLE（无任何公开版本）**：0（所有 LOCAL_ONLY 图均有公开文字/索引/报告替代）。
