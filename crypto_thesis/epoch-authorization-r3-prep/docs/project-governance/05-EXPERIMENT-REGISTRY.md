# Experiment Registry

| Experiment | Status | Formal result | Records/configs | Evidence |
|---|---|---:|---:|---|
| E1 policy representation | COMPLETED | yes | frozen in time-policy run | Research Content 1 formal report |
| Local authorization prototype | TESTED | no | 92 pytest tests passed in current repo | `tests/` |
| Infrastructure validation chain | VALIDATED | infrastructure only | 4 validators + 1 RPC | old-chain reports |
| PostgreSQL shared Nonce | VALIDATED | security evidence | 50/100/500, one success each | Stage B reports |
| Formal authorization chain | VALIDATED | system evidence | chainId 2026072901 | formal-chain F5-F10 evidence |
| PILOT_ONLY authorization run | PILOT_ONLY | no | 108 configs / 3,780 records | `experiments\runs\pilot_multihost_20260729_990acbe` |
| Formal performance experiment | NOT_STARTED | no | 0 | admission approved; separate execution required |
| Research Content 3 experiments | NOT_STARTED | no | 0 | none |
| I9 accepted Pilot baseline | COMPLETED_PILOT_ONLY | no | 93 RUNs | `experiments/r3/i9-pilot/final-analysis/i9-run-index.json`; not formal evidence |
| I10 formal design/preregistration | DESIGN_FROZEN | no | 29 configs / 145 measured planned RUNs | `docs/research-content-3-implementation/i10/`; frozen protocol |
| I11 formal experiment (Research Content 3) | COMPLETED | yes | E1-E5, 29 configs, 35 warmups + 145 measured RUNs (180 total), seed 20260802 | `docs/research-content-3-implementation/i11/`; `experiments/r3/formal/raw` (180 sealed RUNs, FORMAL_EXPERIMENT) |
| I12 formal results review (Research Content 3) | COMPLETED | analysis/review | 145 RUN statistical dataset; RQ cards; claim-evidence matrix; figures/tables; writeback candidates | `docs/research-content-3-implementation/i12/`; `experiments/r3/formal/figures|tables/i12-final/` |
| I13 thesis writeback (Research Content 3) | COMPLETED | chapter draft | RC3 chapter (第六章 draft): design + E1-E5 results + discussion + limitations + 3 figures + 5 tables | `docs/research-content-3-implementation/i13/THESIS-RC3-WRITEBACK-FINAL.md` |
| I14 full-thesis final review | COMPLETED_WITH_LITERATURE_QUEUE | integration/review | integrated master draft (ch1-7 + abstract + references) + 27 review docs + 11 JSON audits | `docs/thesis-integration/`; `docs/full-thesis-final-review/` |
| I15 final literature verification | COMPLETED | verification/audit | 16 verified references (11 VERIFIED + 5 VERIFIED_WITH_CORRECTION), queue 6/6 closed, DOI corrections 2, citation closure 0/0, coverage MINIMALLY_SUFFICIENT, FATAL/MAJOR 0, MINOR 2 | `docs/final-literature-verification/` (14 md + 8 JSON + 32 evidence files) |
| I16 final manuscript assembly & formatting | COMPLETED_AS_FORMAT_CANDIDATE | assembly/formatting | Word format candidate (55-page PDF, 7 chapters + refs + appendix), 16 figures / 16 tables / 19 numbered equations + 190 inline / 5 algorithms, global citation renumbering, I15 MINOR 2/2 closed; FATAL/MAJOR 0, MINOR 4 (format-only); awaiting official school template | `docs/final-manuscript/` (19 md + 10 JSON + DOCX/PDF) |
| I17 academic prose reconstruction + official template | COMPLETED_WITH_OFFICIAL_TEMPLATE_APPLIED | prose/formatting | paragraph reflow (287 body paras, avg 94.8 chars), manual breaks unintentional 0, numbered-list splits, table/figure/lemma renumbering, official UESTC cover/flyleaf + writing spec applied, V2 DOCX/PDF (55 pages), 16/16 figures/tables, refs 16/16; FATAL/MAJOR 0, MINOR 3 | `docs/final-manuscript/i17/` (16 md + 6 JSON + I17-SOURCE.md) |
| M1 midterm assessment report | COMPLETED_AWAITING_USER_REVIEW | report writing | midterm form candidate (14-page PDF, 3 real figures), research progress per frozen results, 4 problems/solutions + 3-phase plan, opening date corrected to 2025-12-24, opinions left blank; FATAL/MAJOR 0, MINOR 3 | `docs/midterm-report/` (14 md + 5 JSON + final draft + DOCX/PDF) |
| M2 full midterm report reconstruction | COMPLETED_AWAITING_USER_REVIEW | report writing | official blank template (附件2) base, no prior-version reference, 30-page PDF / ~2.2万汉字, progress ~1.76万, problems+solutions ~4.1千, RC1/2/3 fully expanded, 8 real figures / 6 tables / 3 algorithms, legacy content 0, opinions blank; FATAL/MAJOR 0, MINOR 3 | `docs/midterm-report/m2/` (17 md + 5 JSON + full draft + figures + DOCX/PDF) |

PILOT_ONLY raw SHA-256: `a4d0fcb12de587afe31e8af49854a9db7bcc40a04e5ef2a38865cd1c7d4d27b3`.

| R2 formal performance | COMPLETED | yes | 324 seeded configs / 103,680 records | `experiments\runs\formal_auth_multihost_20260729_34af4ff` |

The row above is superseded by strict review: status is
`INVALIDATED_MATERIAL_PROTOCOL_DEVIATION`; the immutable data are retained for audit
but are not thesis-formal performance evidence.
