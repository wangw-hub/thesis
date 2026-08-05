# 上下文恢复报告

- 恢复基线：`8a3d795e22e5d9373c3053245e3b4040cd062dd5`；隔离分支 `research-content-3-preparation`。
- 已完整读取根 `AGENTS.md`、治理包 00–10 与 `project-state.json`，并读取现存 R2 严格审稿、重跑状态、合约、CAP2 序列化和正式链清单。
- R2 结论采用最新具体状态 `FORMAL_EVIDENCE_REQUIRES_RERUN`。主工作树存在 R2 干跑产物和扫描文件修改；本任务未修改它们。
- 任务点名的审稿文件 `02-EXPERIMENTAL-FAIRNESS-REVIEW.md`、`03-STATISTICAL-UNIT-AND-PSEUDOREPLICATION-AUDIT.md`、`08-STRICT-PEER-REVIEW.md`、`review-issue-tracker.json`在当前 HEAD 不存在；等价事实由 `01`、`09`、`10`、`STRICT-REVIEW-HARD-STOP.md`及 `rerun/`材料恢复。
- 未发现 Git 锁；本机未发现 Python/Java/PostgreSQL采集进程。V13干跑最后写入为 2026-07-29 15:29:39；远端正式链是否持续运行不能由本机进程表证明。

事实优先级、冲突和硬停止遵循治理包。设计入口见 [问题定义](02-PROBLEM-DEFINITION.md)；待合并治理项见 `PROPOSED-GOVERNANCE-UPDATES.md`。
