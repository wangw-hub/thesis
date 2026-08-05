# 面向非连续时间约束的区块链数据共享关键技术研究及实现 — 研究工作存档

本仓库是学位论文《面向非连续时间约束的区块链数据共享关键技术研究及实现》全部研究工作的存档，目的是让任何后续大模型或智能体在克隆本仓库后，能够完整了解已经完成的工作：研究问题、技术方案、工程实现、实验验证与论文写作状态。

## 仓库结构

| 路径 | 内容 |
|---|---|
| `crypto_thesis/论文实施蓝图V1.0.md` | 论文总体实施蓝图：研究定位、三部分贡献、环境冻结（Besu QBFT、Solidity、Web3.py）、实验设计 |
| `crypto_thesis/开题报告系统级审查与重构报告.md` | 开题报告严格审查结论与重构方案 |
| `crypto_thesis/中期答辩与投稿执行蓝图.md` | 中期答辩范围、可主张贡献与投稿执行计划 |
| `crypto_thesis/研究内容一技术设计V1.0.md` | 研究内容一（非连续时间策略编译）技术设计 |
| `crypto_thesis/time-policy/` | 研究内容一（论文第四章）工程原型：时间区间规范化、层次覆盖、NTP1 编码、策略摘要 |
| `crypto_thesis/epoch-authorization/` | 研究内容二（论文第五章）工程原型：Epoch 驱动的授权状态管理、Besu QBFT 真实链后端、CAP1/CAP2 编码 |
| `crypto_thesis/epoch-authorization-r3-prep/` | 研究内容三准备与实现（版本化密文头部、HPKE、前瞻性撤销），并含中期答辩报告与最终手稿文档 |
| `crypto_thesis/artifacts/` | 开题报告等已解包文档 |
| `thesis_literature_verified_2026-07-30/` | 文献核验清单、阅读报告与参考文献库 |
| `academic-research-suite-usage-guide.md` | 研究流水线（ARS）使用说明 |

## 建议阅读顺序

1. 先读顶层三份蓝图/审查文档（`论文实施蓝图V1.0.md`、`开题报告系统级审查与重构报告.md`、`中期答辩与投稿执行蓝图.md`），建立总体认知。
2. 再进入各子项目，读各自的 `README.md` 与 `AGENTS.md`，了解工程边界与运行方式。
3. 需要核实结论时，读各项目根目录的验收/审稿报告（如“研究内容二”系列报告、“第四章”系列修订稿）与 `docs/` 下的写作文档。

## 上传范围与排除说明

- 原始实验数据（各 `experiments/` 目录，约 1.6 GB，含超过 GitHub 单文件 100 MB 上限的数据）未上传；如有需要可后续通过 Git LFS 单独加入。
- 区块链运行时（`blockchain/` 下的 Besu、JDK 与安装包，约 950 MB）未上传，可按各项目文档自行下载。
- 密钥与敏感目录（`.funding-review-secrets/`、`crypto_thesis/secrets/`、`security-quarantine/`）一律不上传。
- 临时与缓存目录（`.codex-temp/`、`tmp/`、虚拟环境、缓存等）不上传。
- 三个子项目原有的 git 历史已安全移至本地 `D:\Research\.git-backups\`（未上传，如需恢复可移回）。
