# LOCAL VS PUBLIC ASSETS — 公开仓库与本地完整资料的区别

> 公开 GitHub 仓库（`wangw-hub/thesis`）是**研究内容与治理层**的入口；
> 本地 `D:\Research` 是**完整研究资料**的唯一完整来源。

## PUBLIC / GITHUB 包含

- 三个研究内容（RC1/RC2/RC3）的源码、合约、测试、脚本、部署/基础设施配置（不含运行时二进制）；
- 全部报告（验收、审稿、claim-evidence、实验设计、修订追踪）；
- 论文集成母本、最终手稿候选（MD + DOCX/PDF）、中期考评表最终固化版（DOCX/PDF）、文献核验材料；
- 治理层：`docs/project-governance/`（CURRENT-SNAPSHOT、AUTHORITY-MAP、索引、状态 JSON 等）+ 根 README。

## LOCAL ONLY 包含（不进入公开仓库）

| 类别 | 说明 | 本地位置 |
|---|---|---|
| 正式实验 raw | RC1 E1 raw、RC2 V13 raw（requests/chain-reads 共约 310 MB）、RC3 I11 raw（180 sealed RUNs） | `crypto_thesis/*/experiments/` |
| 大型归档 | 实验运行包、tar/zip 快照（.codex-temp、tmp 等） | `D:\Research\.codex-temp\`、`tmp\` |
| 区块链运行时/依赖 | Besu 26.5.0、JDK、node_modules、.tools、虚拟环境 | `crypto_thesis/*/blockchain/`、`.venv*`、`.tools/` |
| 历史 Git 历史 | 三个子项目完整提交历史 | `D:\Research\.git-backups\` |
| 敏感材料 | 密钥、口令、种子、数据库凭据、Besu 节点密钥等 | 不在任何版本控制中：`SECRET_MATERIAL_NOT_VERSIONED` |
| 隔离/检疫资产 | 安全事件检疫副本、旧链证据 | `crypto_thesis/security-quarantine/`、旧链报告 |

## 对 AI 会话的提醒

1. 公开仓库不含 raw，正式数字请以各正式运行的 manifest/analysis 与治理层清单（EXPERIMENT-DATA-MANIFEST.md）为准。
2. 本地 raw 只读；任何会话不得修改。
3. 敏感材料一律不写入任何清单正文；需要记录时仅写 `SECRET_MATERIAL_NOT_VERSIONED`。
4. 历史 Git 历史在 `.git-backups\`，需要解析提交谱系时按 COMMIT-LINEAGE.md 的校验方式执行。
