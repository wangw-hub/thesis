# Project Constitution

## Mission

This repository supports the computer-technology professional master's thesis **《面向非连续时间约束的区块链数据共享关键技术研究及实现》**. The thesis is an engineering and systems study: its conclusions must be supported by implementable mechanisms, real experiments, reproducible assets, and traceable evidence. It does not seek unsupported new cryptographic primitives.

## Research Contents

| ID | Current scope | Status |
| --- | --- | --- |
| R1 | Deterministic normalization, semantic representation, compilation, and boundary experiments for non-continuous time policies. | COMPLETED_WITH_SCOPE_ADJUSTMENT |
| R2 | Trusted authorization-state execution on a real Besu QBFT consortium chain, CAP2 binding, shared nonce control, and identity/state consistency. | COMPLETED_WITH_VALID_RERUN_EVIDENCE |
| R3 | Versioned ciphertext headers, standard hybrid encryption, forward-looking revocation, on-chain/off-chain state closure, and recovery. | FORMAL_COMPLETED（在 r3-prep 工作树实现；本仓库范围至 RC2） |

## Frozen Method Positioning

`I*` is the sole semantic primary representation. It is the basis for canonical NTP1 serialization, `policyDigest`, and ordinary interval membership matching. `C(P)` is deterministically derived from `I*` and is an optional, hierarchical execution IR. It is retained for ablation/falsification and potential later protocol consumption; it is not a universally better compression or one-dimensional query structure.

The R2 mainline is Baseline-I and Baseline-I-Cache. Proposed-C and Proposed-C-Cache are comparison and falsification variants only.

> Updated 2026-08-05：R2 以 V13 有效复跑关闭（见 `01-CURRENT-STATE.md`）；
> RC3 已在 `epoch-authorization-r3-prep` 工作树实现并完成 I11 Formal，本仓库不再承担 RC3。

## Explicit Non-Goals And Claim Limits

- Do not revive the superseded self-designed ABE route or on-chain secret-trapdoor design.
- Do not claim unconditional `O(log U)` representation for arbitrary non-continuous policies.
- Do not claim that revocation recovers plaintext or data keys already obtained.
- Do not claim that blockchain provides an absolute trusted clock.
- Do not translate implementation tests into cryptographic proofs.
- Do not describe component composition as a new cryptographic primitive.
- Do not state that `C(P)` is generally smaller or faster than interval lists.

## Evidence And Change Rules

Project facts follow this order: (1) code, Git history, raw data, reports, and acceptance evidence; (2) latest frozen governance decisions; (3) current explicit user instruction; (4) historical design documents; (5) chat memory. Conflicts are recorded as CURRENT, SUPERSEDED, PARTIALLY_VALID, HISTORICAL_ONLY, or UNRESOLVED. Never silently reconcile conflicts by rewriting old records.

An item may be marked COMPLETED only after implementation, tests, raw evidence, a report, and Git freeze exist. Plans and PILOT_ONLY data are not completed research results. All work must preserve reproducibility, version traceability, and secret hygiene.
