# 检索日志

- 搜索日期：2026-07-30。
- 平台类型：ACM DL、IEEE Xplore、SpringerLink、Wiley、USENIX、NDSS、IETF、NIST、Besu、PostgreSQL、DBLP、Crossref/DOI、arXiv/IACR、软件学报、计算机学报/机构库、Google/Semantic聚合，共16类。
- 原始进入证据台账的候选记录：94。
- 合并预印本/正式版、会议/期刊扩展版和重复索引：19。
- 去重后独立候选：75。
- 双源核验并纳入核心：60。
- UNVERIFIED/观察：15。
- 完整三主线同构工作：0；模块部分相似工作：至少16。

|平台|主要主题|实际审阅候选|纳入|主要排除原因|
|---|---|---:|---:|---|
|ACM DL|时态授权、能力、系统、实验|21|15|仅引用命中、版本重复、主题偏离|
|IEEE Xplore|GTRBAC、撤销、SC-CAAC|11|5|缺少系统闭环或元数据不足|
|SpringerLink|ABE、HPKE、撤销、2025综述|16|9|已有正式版的预印本被合并|
|USENIX/NDSS|PBFT、Macaroons、Plutus、IPFS|13|9|工具介绍或过远主题|
|IETF/NIST|密码和授权规范|12|10|非核心辅助规范|
|Besu/PostgreSQL|工程规范|7|3|教程/旧版本重复|
|中文官方期刊/机构库|时态、ABE、区块链访问控制|13|5|双源信息不足或质量/相关性不足|
|arXiv/IACR|最新线索与版本映射|14|3（明确预印本）|未正式发表、正式版已存在|

## 去重规则
1. arXiv/ePrint与正式版合并，核心引用正式版并记录预印本。
2. 会议与期刊扩展仅在内容确有独立价值时同时保留。
3. RFC的HTML/PDF/Datatracker视为同一规范。
4. 官方文档不同版本不重复计入核心。
5. ResearchGate等仅作第二线索，不替代出版商。

## 检索空白
- 未找到专门以“非连续时间策略规范化+确定性序列化+policyDigest”为完整主题的高质量论文。
- 未找到公开论文披露与CAP2完全相同字段集合。
- 链交易UNKNOWN、对象存储和PostgreSQL任务状态机的完整组合在学术文献中较分散。
- 2026年部分新工作只有预印本或出版元数据尚不稳定，未纳入核心。
