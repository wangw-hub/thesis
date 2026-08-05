# 核心文献清单（60项）

检索与核验日期：2026-07-30。每项至少包含“出版商/官方页面 + DBLP、第二官方页面、机构库或正式索引”两路核验。普通论文的撤稿检查仅表示核验页面未见撤稿标识，不等于穷尽所有讨论平台。

## L01 Maintaining Knowledge about Temporal Intervals
- **作者、年份与来源**：James F. Allen（1983），Communications of the ACM, 26(11): 832–843。
- **DOI**：10.1145/182.358434。
- **双源核验**：https://dl.acm.org/doi/10.1145/182.358434；https://dblp.org/rec/journals/cacm/Allen83。
- **发表状态**：正式发表（同行评审期刊论文）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：A；Q1–Q8=4/4/5/3/3/4/4/4。
- **主要问题**：建立时间区间关系的定性推理框架。
- **核心方法**：定义13种基本区间关系及其组合推理，用于表达先后、重叠、包含等关系。
- **主要结论**：区间关系代数是处理时间窗口相交、包含和边界关系的理论基础，但它不自动给出策略规范形式。
- **实验环境/证据类型**：理论模型与示例，无现代系统性能实验。
- **局限**：不讨论授权、确定性序列化、摘要绑定或Dyadic覆盖。
- **与你方案相同点**：都需要精确定义区间关系和边界语义。
- **不同点**：你的I*处理窗口集合的规范化与唯一字节表示，而Allen代数处理关系推理。
- **可支撑表述**：可支撑区间语义、关系分类和边界讨论。
- **不能支撑的过强表述**：不能支撑I*新颖性、压缩性或区块链执行。
- **推荐阅读**：关系定义、组合表、推理算法与不完备性讨论；建议顺序=4；必须下载全文=是。

## L02 A Temporal Authorization Model
- **作者、年份与来源**：Elisa Bertino; Claudio Bettini; Pierangela Samarati（1994），ACM CCS 1994。
- **DOI**：10.1145/191177.191202。
- **双源核验**：https://dl.acm.org/doi/10.1145/191177.191202；https://dblp.org/rec/conf/ccs/BertinoBS94。
- **发表状态**：正式发表（同行评审会议论文）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：A；Q1–Q8=5/4/5/3/3/4/4/4。
- **主要问题**：把授权有效期和时间依赖纳入访问控制模型。
- **核心方法**：以时间区间、授权和规则形式化授权状态及其演化。
- **主要结论**：时间维度应作为授权语义的一等元素，并需分析不良授权状态。
- **实验环境/证据类型**：理论模型，无现代分布式实验。
- **局限**：没有I*、policyDigest、编译器或区块链状态。
- **与你方案相同点**：都把时间有效性纳入授权判定。
- **不同点**：本文重心是时态授权逻辑；你的重心是受限窗口集合的规范化、编译和复现。
- **可支撑表述**：可支撑“时态授权已有长期理论基础”。
- **不能支撑的过强表述**：不能支撑“首次引入时间约束访问控制”。
- **推荐阅读**：形式模型、时间依赖、更新操作、不良状态；建议顺序=5；必须下载全文=是。

## L03 An Access Control Model Supporting Periodicity Constraints and Temporal Reasoning
- **作者、年份与来源**：Elisa Bertino; Claudio Bettini; Elena Ferrari; Pierangela Samarati（1998），ACM Transactions on Database Systems, 23(3)。
- **DOI**：10.1145/293910.293151。
- **双源核验**：https://dl.acm.org/doi/10.1145/293910.293151；https://dblp.org/rec/journals/tods/BertinoBFS98。
- **发表状态**：正式发表（同行评审期刊论文）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：S；Q1–Q8=5/5/5/3/3/5/4/5。
- **主要问题**：表达周期性授权并进行时间推理。
- **核心方法**：使用周期表达式、时间依赖规则和有效授权集语义，讨论物化计算。
- **主要结论**：周期和非连续时间授权可被形式化计算，但表达能力、唯一性和执行成本需共同分析。
- **实验环境/证据类型**：模型、算法和示例为主。
- **局限**：不解决确定性字节序列化、policyDigest或链上执行。
- **与你方案相同点**：与你的多窗口、周期性和唯一语义目标高度相关。
- **不同点**：其唯一性对象是推理后的有效授权集合；I*是输入窗口集合规范化后的唯一语义表示。
- **可支撑表述**：可支撑相关工作基线和“贡献必须定位在确定性编译而非时间授权空白”。
- **不能支撑的过强表述**：不能支撑任意策略O(log U)压缩或C(P)必优。
- **推荐阅读**：周期表达式、授权语义、唯一性、物化算法和复杂度；建议顺序=1；必须下载全文=是。

## L04 TRBAC: A Temporal Role-Based Access Control Model
- **作者、年份与来源**：Elisa Bertino; Piero A. Bonatti; Elena Ferrari（2001），ACM Transactions on Information and System Security, 4(3)。
- **DOI**：10.1145/501978.501979。
- **双源核验**：https://dl.acm.org/doi/10.1145/501978.501979；https://dblp.org/rec/journals/tissec/BertinoBF01。
- **发表状态**：正式发表（同行评审期刊论文）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：S；Q1–Q8=5/5/5/3/3/5/4/5。
- **主要问题**：将周期时间、角色启用/禁用和触发器纳入RBAC。
- **核心方法**：定义周期表达式、角色状态事件和触发规则。
- **主要结论**：时间约束会改变角色状态机和冲突处理，不能仅作为静态属性比较。
- **实验环境/证据类型**：模型与案例为主。
- **局限**：角色中心，不提供通用窗口编译与摘要绑定。
- **与你方案相同点**：都需处理边界、重叠、状态变化和确定执行顺序。
- **不同点**：你的模型故意缩小表达范围以换取唯一表示和可复现编译。
- **可支撑表述**：可支撑时态RBAC谱系和执行语义。
- **不能支撑的过强表述**：不能证明I*、policyDigest或C(P)的新颖性。
- **推荐阅读**：模型、周期表达式、触发器、冲突与执行语义；建议顺序=2；必须下载全文=是。

## L05 Generalized Temporal Role Based Access Control Model
- **作者、年份与来源**：James B. D. Joshi; Elisa Bertino; Usman Latif; Arif Ghafoor（2005），IEEE Transactions on Knowledge and Data Engineering, 17(1)。
- **DOI**：10.1109/TKDE.2005.1。
- **双源核验**：https://ieeexplore.ieee.org/document/1377049；https://dblp.org/rec/journals/tkde/JoshiBLG05。
- **发表状态**：正式发表（同行评审期刊论文）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：S；Q1–Q8=5/5/5/3/3/5/4/5。
- **主要问题**：统一更一般的周期角色启用、时间约束、运行时事件和优先级。
- **核心方法**：GTRBAC形式模型、事件/触发器语义和约束优先级。
- **主要结论**：复杂时态授权必须定义冲突、优先级和运行时状态，否则实现会产生非确定行为。
- **实验环境/证据类型**：理论与案例。
- **局限**：表达力远高于你的冻结范围，未提供规范化字节表示。
- **与你方案相同点**：可帮助检查时间策略组合和冲突边界。
- **不同点**：你的贡献不是替代GTRBAC，而是提供窄范围的确定编译。
- **可支撑表述**：可支撑设计取舍：降低表达力换取确定性和可验证性。
- **不能支撑的过强表述**：不能宣称你的策略语言覆盖GTRBAC。
- **推荐阅读**：模型要素、事件、优先级、约束与安全语义；建议顺序=3；必须下载全文=是。

## L06 Security Analysis for Temporal Role Based Access Control
- **作者、年份与来源**：Emre Uzun; Vijayalakshmi Atluri; Jaideep Vaidya; Shamik Sural; Anna Lisa Ferrara; Gennaro Parlato; P. Madhusudan（2014），Journal of Computer Security, 22(6): 961–996。
- **DOI**：10.3233/JCS-140510。
- **双源核验**：https://content.iospress.com/articles/journal-of-computer-security/jcs510；https://experts.illinois.edu/en/publications/security-analysis-for-temporal-role-based-access-control。
- **发表状态**：正式发表（同行评审期刊论文）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：S；Q1–Q8=4/5/5/3/3/5/5/5。
- **主要问题**：分析时态RBAC的安全可达性及复杂性。
- **核心方法**：建立形式语义，将安全查询转化为可分析问题并研究复杂度。
- **主要结论**：时间触发和状态变化会引入非直观可达路径，测试与形式分析必须区分。
- **实验环境/证据类型**：形式分析和案例。
- **局限**：不覆盖I*编译器、区块链和密码撤销。
- **与你方案相同点**：可作为语义保持、等价性和拒绝状态的严格参照。
- **不同点**：你的证据若是定理与测试，就不能写成完整模型检查。
- **可支撑表述**：可支撑证据等级和安全查询设计。
- **不能支撑的过强表述**：不能把pytest通过描述为形式化安全证明。
- **推荐阅读**：形式语义、安全查询、复杂度、案例；建议顺序=6；必须下载全文=是。

## L07 带时间特性的角色访问控制
- **作者、年份与来源**：黄建; 卿斯汉; 温红子（2003），软件学报, 14(11): 1944–1954。
- **DOI**：无DOI/不适用。
- **双源核验**：https://www.jos.org.cn/1000-9825/14/1944.htm；https://www.jos.org.cn/jos/article/issue/2003_14_11。
- **发表状态**：正式发表（中文核心期刊论文）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：A；Q1–Q8=4/4/3/3/3/4/4/4。
- **主要问题**：在中文研究语境中建立带时间特性的RBAC模型。
- **核心方法**：在角色、权限和会话关系中引入时间约束并讨论状态变化。
- **主要结论**：国内较早系统研究时态RBAC，可用于中文相关工作谱系。
- **实验环境/证据类型**：模型与示例。
- **局限**：年代较早，不涉及确定性序列化和区块链。
- **与你方案相同点**：与时间窗口和角色有效期相关。
- **不同点**：你的研究不以角色模型为中心，而以策略编译为中心。
- **可支撑表述**：可支撑国内时态访问控制研究基础。
- **不能支撑的过强表述**：不能作为2021—2026最新进展或系统性能证据。
- **推荐阅读**：模型定义、时间约束、安全分析与示例；建议顺序=7；必须下载全文=是。

## L08 基于周期时间限制的自主访问控制委托模型
- **作者、年份与来源**：张宏; 贺也平; 石志国（2006），计算机学报, 29(8): 1427–1437。
- **DOI**：无DOI/不适用。
- **双源核验**：http://cjc.ict.ac.cn/online/onlinepaper/zhanghong-2006810102936.pdf；https://ir.iscas.ac.cn/handle/311060/3770。
- **发表状态**：正式发表（中文权威期刊论文）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：A；Q1–Q8=4/4/3/3/3/4/4/4。
- **主要问题**：研究周期时间限制下的自主访问控制委托。
- **核心方法**：把周期约束与委托授权传播结合。
- **主要结论**：时间约束不仅影响直接访问，也影响权限传播和派生。
- **实验环境/证据类型**：模型和案例。
- **局限**：委托不是你的核心模块，也无确定性编译。
- **与你方案相同点**：可用于检查派生权限中的时间语义。
- **不同点**：你的冻结方案不以委托为主。
- **可支撑表述**：可支撑中文周期时间约束相关工作。
- **不能支撑的过强表述**：不能支撑CAP2或VersionedHeader设计。
- **推荐阅读**：周期表示、委托规则、安全性讨论；建议顺序=8；必须下载全文=是。

## L09 Fuzzy Identity-Based Encryption
- **作者、年份与来源**：Amit Sahai; Brent Waters（2005），EUROCRYPT 2005。
- **DOI**：10.1007/11426639_27。
- **双源核验**：https://link.springer.com/chapter/10.1007/11426639_27；https://dblp.org/rec/conf/eurocrypt/SahaiW05。
- **发表状态**：正式发表（同行评审密码学会议论文）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：B；Q1–Q8=5/3/5/3/3/4/4/3。
- **主要问题**：提出基于属性相似性的模糊身份加密，为ABE奠基。
- **核心方法**：使用门限属性匹配和双线性对构造。
- **主要结论**：加密访问控制可以把资格编码到密钥/密文关系。
- **实验环境/证据类型**：密码方案与安全证明。
- **局限**：不是时间策略编译，也不是当前实现主线。
- **与你方案相同点**：都涉及按策略控制数据访问。
- **不同点**：你的论文使用标准混合加密和在线授权，ABE仅为背景。
- **可支撑表述**：可支撑ABE概念源流。
- **不能支撑的过强表述**：不能支撑链状态授权或CAP2。
- **推荐阅读**：引言、安全模型、构造概览；建议顺序=22；必须下载全文=否。

## L10 Attribute-Based Encryption for Fine-Grained Access Control of Encrypted Data
- **作者、年份与来源**：Vipul Goyal; Omkant Pandey; Amit Sahai; Brent Waters（2006），ACM CCS 2006。
- **DOI**：10.1145/1180405.1180418。
- **双源核验**：https://dl.acm.org/doi/10.1145/1180405.1180418；https://dblp.org/rec/conf/ccs/GoyalPSW06。
- **发表状态**：正式发表（同行评审密码学/安全会议论文）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：B；Q1–Q8=5/3/5/3/3/4/4/3。
- **主要问题**：提出KP-ABE并实现细粒度加密访问控制。
- **核心方法**：访问树/属性集合与双线性对。
- **主要结论**：策略可绑定于密钥或密文，但动态撤销与系统运维并未自动解决。
- **实验环境/证据类型**：理论方案与初步效率。
- **局限**：不处理链上状态、Nonce或故障恢复。
- **与你方案相同点**：策略驱动的数据共享。
- **不同点**：你的主方案不采用自研ABE。
- **可支撑表述**：可支撑加密访问控制与在线授权的差异。
- **不能支撑的过强表述**：不能把你的系统写成ABE方案。
- **推荐阅读**：模型、构造、表达力和效率；建议顺序=23；必须下载全文=否。

## L11 Ciphertext-Policy Attribute-Based Encryption
- **作者、年份与来源**：John Bethencourt; Amit Sahai; Brent Waters（2007），IEEE Symposium on Security and Privacy 2007。
- **DOI**：10.1109/SP.2007.11。
- **双源核验**：https://ieeexplore.ieee.org/document/4223236；https://dblp.org/rec/conf/sp/BethencourtSW07。
- **发表状态**：正式发表（同行评审安全会议论文）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：A；Q1–Q8=4/4/5/3/3/4/4/4。
- **主要问题**：提出实用CP-ABE，使访问策略嵌入密文。
- **核心方法**：访问树和双线性对，并给出原型实现。
- **主要结论**：CP-ABE支持细粒度离线解密，但撤销、策略更新和密钥治理仍需额外机制。
- **实验环境/证据类型**：原型运算开销实验。
- **局限**：安全模型和构造与HPKE逐接收者封装不同。
- **与你方案相同点**：都服务于加密数据共享。
- **不同点**：你的V1按接收者直接封装CK，不采用CP-ABE。
- **可支撑表述**：可支撑CP-ABE背景与功能对比。
- **不能支撑的过强表述**：不能声称HPKE封装等同CP-ABE。
- **推荐阅读**：系统模型、构造、安全讨论、实现；建议顺序=24；必须下载全文=是。

## L12 Identity-Based Encryption with Efficient Revocation
- **作者、年份与来源**：Alexandra Boldyreva; Vipul Goyal; Virendra Kumar（2008），ACM CCS 2008。
- **DOI**：10.1145/1455770.1455823。
- **双源核验**：https://dl.acm.org/doi/10.1145/1455770.1455823；https://dblp.org/rec/conf/ccs/BoldyrevaGK08。
- **发表状态**：正式发表（同行评审安全会议论文）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：A；Q1–Q8=5/4/5/3/3/4/4/4。
- **主要问题**：降低身份加密中的撤销与密钥更新成本。
- **核心方法**：使用树结构、时间更新密钥和广播式更新。
- **主要结论**：撤销通常需要显式纪元/更新机制，且未来和历史访问必须区分。
- **实验环境/证据类型**：理论与效率比较。
- **局限**：不是HPKE Header，也不处理链上链下恢复。
- **与你方案相同点**：都关注版本、纪元和撤销后的材料更新。
- **不同点**：你的V1选择更简单的逐接收者重建Header。
- **可支撑表述**：可支撑撤销分类和更新成本讨论。
- **不能支撑的过强表述**：不能支撑你的具体Header字段或前瞻性撤销证明。
- **推荐阅读**：撤销模型、树结构、更新算法、效率；建议顺序=25；必须下载全文=是。

## L13 Systematizing Core Properties of Pairing-Based Attribute-Based Encryption to Uncover Remaining Challenges in Enforcing Access Control in Practice
- **作者、年份与来源**：Marloes Venema; Greg Alpár; Jaap-Henk Hoepman（2023），Designs, Codes and Cryptography, 91(1)。
- **DOI**：10.1007/s10623-022-01093-5。
- **双源核验**：https://link.springer.com/article/10.1007/s10623-022-01093-5；https://eprint.iacr.org/2021/1172。
- **发表状态**：正式发表（同行评审期刊论文；有IACR ePrint前版）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：A；Q1–Q8=4/4/3/3/3/5/5/4。
- **主要问题**：系统化ABE核心性质及其在实际访问控制中的兼容性与缺口。
- **核心方法**：Systematization of Knowledge，以性质矩阵比较方案。
- **主要结论**：动态性、撤销、隐藏、外包等性质难以同时低成本满足，不能把ABE当作万能替代。
- **实验环境/证据类型**：系统化文献分析。
- **局限**：不针对Besu、CAP2或HPKE文件格式。
- **与你方案相同点**：帮助界定密码访问控制与在线授权的职责。
- **不同点**：你的主线是标准组件系统闭环而非新ABE。
- **可支撑表述**：可支撑主动放弃自研ABE和逐项论证工程性质。
- **不能支撑的过强表述**：不能直接证明你的系统创新性。
- **推荐阅读**：性质分类、矩阵、实践缺口、未来挑战；建议顺序=19；必须下载全文=是。

## L14 Attribute-Based Proxy Re-Encryption With Direct Revocation Mechanism for Data Sharing in Clouds
- **作者、年份与来源**：Chunpeng Ge; Willy Susilo; Zhe Liu; Joonsang Baek; Xiaofeng Chen; Liming Fang（2024），IEEE Transactions on Dependable and Secure Computing, 21(2): 949–960。
- **DOI**：10.1109/TDSC.2023.3265979。
- **双源核验**：https://ieeexplore.ieee.org/document/10098892；https://dblp.org/rec/journals/tdsc/GeSLBCF24。
- **发表状态**：正式发表（同行评审期刊论文；在线优先2023、卷期2024）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：S；Q1–Q8=5/5/3/3/3/5/5/5。
- **主要问题**：实现属性代理重加密和直接撤销。
- **核心方法**：ABPRE-DR、代理转换、直接撤销和安全证明。
- **主要结论**：更强的密码撤销功能需要更复杂的代理、密钥和证明机制。
- **实验环境/证据类型**：密码运算性能与方案比较。
- **局限**：不处理链状态、任务UNKNOWN和崩溃恢复。
- **与你方案相同点**：都研究撤销后阻止后续有效访问并更新材料。
- **不同点**：你的方案用标准HPKE逐接收者封装，功能更窄但实现和边界更透明。
- **可支撑表述**：可作为撤销能力和性能的强竞争工作。
- **不能支撑的过强表述**：不能声称你的简单封装在密码功能上全面优于ABPRE-DR。
- **推荐阅读**：系统模型、撤销算法、安全证明、性能；建议顺序=12；必须下载全文=是。

## L15 属性基加密机制
- **作者、年份与来源**：苏金树; 曹丹; 王小峰; 孙一品; 胡乔林（2011），软件学报, 22(6): 1299–1315。
- **DOI**：无DOI/不适用。
- **双源核验**：https://jos.org.cn/jos/article/abstract/3993；https://www.jos.org.cn/jos/article/issue/2011_22_6。
- **发表状态**：正式发表（中文核心期刊综述）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：A；Q1–Q8=4/4/3/3/3/4/4/4。
- **主要问题**：综述ABE模型、代表方案和研究问题。
- **核心方法**：分类梳理KP-ABE、CP-ABE及其安全与效率性质。
- **主要结论**：适合建立中文密码访问控制术语与研究谱系。
- **实验环境/证据类型**：综述，无统一复现实验。
- **局限**：年代较早，需结合2023 SoK。
- **与你方案相同点**：涉及策略驱动的加密数据共享。
- **不同点**：你的实现不以ABE为核心。
- **可支撑表述**：可支撑中文背景与术语。
- **不能支撑的过强表述**：不能支撑2024—2026最新状态或你的工程结论。
- **推荐阅读**：分类、安全模型、代表方案、开放问题；建议顺序=26；必须下载全文=是。

## L16 Blockchain-based access control and privacy preservation in healthcare: a comprehensive survey
- **作者、年份与来源**：Ahmed M. Tawfik; Ayman Al-Ahwal; Adly S. Tag Eldien; Hala H. Zayed（2025），Cluster Computing, 28, Article 529。
- **DOI**：10.1007/s10586-025-05308-x。
- **双源核验**：https://link.springer.com/article/10.1007/s10586-025-05308-x；https://dblp.org/rec/journals/cluster/TawfikAEZ25a。
- **发表状态**：正式发表（同行评审期刊综述）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：B；Q1–Q8=4/3/3/5/3/4/4/3。
- **主要问题**：系统梳理医疗场景区块链访问控制、隐私技术和共识平台。
- **核心方法**：结构化筛选并分类许可链/非许可链和隐私增强方法。
- **主要结论**：近年应用仍普遍面临隐私、性能、互操作和治理权衡。
- **实验环境/证据类型**：综述45篇重点研究及案例。
- **局限**：医疗场景限制明显，不能代替通用授权系统对比。
- **与你方案相同点**：覆盖区块链数据共享、智能合约授权与隐私。
- **不同点**：你的系统聚焦Besu状态绑定、共享Nonce和可恢复撤销。
- **可支撑表述**：可支撑2025年最新应用趋势和开放问题。
- **不能支撑的过强表述**：不能把医疗应用结论直接泛化为你的性能与安全结论。
- **推荐阅读**：选择方法、分类框架、平台比较、开放问题；建议顺序=40；必须下载全文=是。

## L17 FairAccess: a new Blockchain-based access control framework for the Internet of Things
- **作者、年份与来源**：Aafaf Ouaddah; Anas Abou Elkalam; Abdellah Ait Ouahman（2017），Security and Communication Networks, 9(18)。
- **DOI**：10.1002/sec.1748。
- **双源核验**：https://onlinelibrary.wiley.com/doi/10.1002/sec.1748；https://www.researchgate.net/publication/313847688。
- **发表状态**：正式发表（同行评审期刊论文；在线/卷期元数据存在2016–2017差异，按正式卷期2017记录）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：A；Q1–Q8=4/4/3/5/3/5/4/4。
- **主要问题**：用区块链管理IoT授权的授予、获取、委托和撤销。
- **核心方法**：基于OrBAC和区块链交易构建分散授权框架，并在树莓派和本地区块链上概念验证。
- **主要结论**：链上授权可提升审计和去中心化，但性能、隐私和治理仍需明确。
- **实验环境/证据类型**：Raspberry Pi与本地链PoC。
- **局限**：平台和威胁模型较早，缺少CAP2全绑定和共享Nonce。
- **与你方案相同点**：都使用链上授权状态和撤销。
- **不同点**：你的系统采用许可链、版本化能力和多Verifier一致性。
- **可支撑表述**：可作为早期区块链授权系统对比。
- **不能支撑的过强表述**：不能支撑区块链天然可扩展或绝对可信。
- **推荐阅读**：参考模型、交易类型、架构、PoC与限制；建议顺序=27；必须下载全文=是。

## L18 BlendCAC: A Smart Contract Enabled Decentralized Capability-Based Access Control Mechanism for the IoT
- **作者、年份与来源**：Ronghua Xu; Yu Chen; Erik Blasch; Genshe Chen（2018），Computers, 7(3), 39。
- **DOI**：10.3390/computers7030039。
- **双源核验**：https://www.mdpi.com/2073-431X/7/3/39；https://arxiv.org/abs/1804.09267。
- **发表状态**：正式发表（同行评审期刊论文；有arXiv预印本）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：A；Q1–Q8=3/4/3/5/3/5/4/4。
- **主要问题**：通过智能合约实现分散能力授权、委托和撤销。
- **核心方法**：能力令牌、智能合约注册与传播、私有链和边缘设备原型。
- **主要结论**：链上能力管理能降低单点授权，但令牌上下文、新鲜度和撤销语义仍需精确定义。
- **实验环境/证据类型**：树莓派/边缘设备与私有Ethereum原型。
- **局限**：未覆盖chainId、contract、stateVersion、userVersion全绑定和共享Nonce。
- **与你方案相同点**：都采用能力结构、智能合约与撤销状态。
- **不同点**：CAP2字段更完整，且你的实验强调多Verifier与Fail-Closed。
- **可支撑表述**：最接近的区块链能力访问控制对比之一。
- **不能支撑的过强表述**：不能据其结果声称你的Besu系统性能或协议优势。
- **推荐阅读**：能力模型、合约、令牌管理、实验；建议顺序=13；必须下载全文=是。

## L19 Blockchain Based Access Control Systems: State of the Art and Challenges
- **作者、年份与来源**：Sara Rouhani; Ralph Deters（2019），IEEE/WIC/ACM International Conference on Web Intelligence。
- **DOI**：10.1145/3350546.3352561。
- **双源核验**：https://dl.acm.org/doi/10.1145/3350546.3352561；https://dblp.org/rec/conf/webi/RouhaniD19。
- **发表状态**：正式发表（同行评审会议论文；有arXiv预印本）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：A；Q1–Q8=3/4/3/5/3/4/4/4。
- **主要问题**：分类区块链访问控制系统及挑战。
- **核心方法**：从模型、平台、策略执行和审计等维度综述。
- **主要结论**：审计和去中心化不会自动解决隐私、性能、治理与撤销。
- **实验环境/证据类型**：综述，无统一基准。
- **局限**：截至2019，不能代表最新Besu工程状态。
- **与你方案相同点**：覆盖智能合约、能力和属性访问控制。
- **不同点**：你的系统聚焦完整绑定、Nonce和真实多节点。
- **可支撑表述**：可支撑相关工作分类和挑战。
- **不能支撑的过强表述**：不能支撑你的具体性能或创新结论。
- **推荐阅读**：分类框架、代表系统、挑战；建议顺序=28；必须下载全文=是。

## L20 Distributed Attribute-Based Access Control System Using Permissioned Blockchain
- **作者、年份与来源**：Sara Rouhani; Rafael Belchior; Rui S. Cruz; Ralph Deters（2021），World Wide Web, 24(5): 1617–1644。
- **DOI**：10.1007/s11280-021-00874-7。
- **双源核验**：https://link.springer.com/article/10.1007/s11280-021-00874-7；https://dblp.org/rec/journals/www/RouhaniBCD21。
- **发表状态**：正式发表（同行评审期刊论文；有arXiv前版）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：S；Q1–Q8=4/5/3/5/5/5/4/5。
- **主要问题**：在许可链上实现分布式ABAC与可信审计。
- **核心方法**：Hyperledger Fabric架构、链码授权和多配置性能实验。
- **主要结论**：许可链可支持可审计授权，但延迟吞吐取决于共识、数据库和部署。
- **实验环境/证据类型**：Fabric测试床、不同共识/数据库和请求负载。
- **局限**：不具备你的CAP2全绑定、共享PostgreSQL单次Nonce和Besu配对实验。
- **与你方案相同点**：许可链、链上状态、真实实现和性能测试高度相关。
- **不同点**：其核心是ABAC审计；你的核心是状态锚定、能力绑定和多Verifier一致性。
- **可支撑表述**：最重要的系统级对比之一。
- **不能支撑的过强表述**：不能把Fabric结果直接迁移为Besu/QBFT结论。
- **推荐阅读**：架构、链码、部署、性能方法、威胁讨论；建议顺序=9；必须下载全文=是。

## L21 Blockchain for Access Control Systems
- **作者、年份与来源**：Vincent C. Hu（2022），NIST IR 8403。
- **DOI**：10.6028/NIST.IR.8403。
- **双源核验**：https://csrc.nist.gov/pubs/ir/8403/final；https://nvlpubs.nist.gov/nistpubs/ir/2022/NIST.IR.8403.pdf。
- **发表状态**：正式NIST报告（权威技术报告，不是实验论文）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：A；Q1–Q8=5/4/3/5/3/4/4/4。
- **主要问题**：从区块链组件、功能点和访问控制模型角度给出系统化设计考虑。
- **核心方法**：映射PAP/PDP/PIP/PEP等功能到链上或链下组件，并讨论RBAC/ABAC/CBAC。
- **主要结论**：区块链访问控制仍需处理管理、安全、隐私、性能和标准化。
- **实验环境/证据类型**：规范性分析，无独立性能基准。
- **局限**：不提供CAP2或Besu实现证明。
- **与你方案相同点**：直接支撑链上/链下授权功能拆分。
- **不同点**：你的系统进一步具体化链状态、Verifier、数据库Nonce和Fail-Closed。
- **可支撑表述**：可支撑架构选择和边界表述。
- **不能支撑的过强表述**：不能作为你的实验结果或安全证明。
- **推荐阅读**：执行摘要、功能点架构、模型支持、实施考虑；建议顺序=20；必须下载全文=是。

## L22 SC-CAAC: A Smart-Contract-Based Context-Aware Access Control Scheme for Blockchain-Enabled IoT Systems
- **作者、年份与来源**：Mpyana Mwamba Merlec; Hoh Peter In（2024），IEEE Internet of Things Journal, 11(11): 19866–19881。
- **DOI**：10.1109/JIOT.2024.3371504。
- **双源核验**：https://ieeexplore.ieee.org/document/10454577；https://pure.korea.ac.kr/en/publications/sc-caac-a-smart-contract-based-context-aware-access-control-schem/。
- **发表状态**：正式发表（同行评审期刊论文）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：A；Q1–Q8=4/4/3/5/5/5/4/4。
- **主要问题**：在联盟链IoT中实现日期、时间、位置、用途等上下文感知授权。
- **核心方法**：上下文访问控制列表、策略状态机和Hyperledger Besu智能合约实现。
- **主要结论**：上下文可以进入链上授权，但上下文真实性、状态新鲜度和读取成本仍是系统问题。
- **实验环境/证据类型**：Besu实现，测量策略设置、查询和验证延迟。
- **局限**：未覆盖I*规范化、CAP2全状态绑定和共享Nonce。
- **与你方案相同点**：时间上下文、Besu和智能合约授权与论文高度相关。
- **不同点**：你的工作更重视非连续窗口编译、完整域绑定、多Verifier和Fail-Closed。
- **可支撑表述**：可作为2024年最重要竞争性工作。
- **不能支撑的过强表述**：不能支撑“时间上链即可信时间”。
- **推荐阅读**：上下文模型、状态机、Besu实现、性能；建议顺序=10；必须下载全文=是。

## L23 Macaroons: Cookies with Contextual Caveats for Decentralized Authorization in the Cloud
- **作者、年份与来源**：Arnar Birgisson; Joe Gibbs Politz; Úlfar Erlingsson; Ankur Taly; Michael Vrable; Mark Lentczner（2014），NDSS 2014。
- **DOI**：10.14722/ndss.2014.23212。
- **双源核验**：https://www.ndss-symposium.org/ndss2014/ndss-2014-programme/macaroons-cookies-contextual-caveats-decentralized-authorization-cloud/；https://dblp.org/rec/conf/ndss/BirgissonPETVL14。
- **发表状态**：正式发表（同行评审安全会议论文）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：S；Q1–Q8=4/5/3/5/3/5/5/5。
- **主要问题**：构造可衰减、带上下文限制的分布式授权凭证。
- **核心方法**：链式MAC、第一方/第三方caveat和委托。
- **主要结论**：Bearer能力必须通过上下文限制、最小权限和验证语义降低滥用风险。
- **实验环境/证据类型**：原型和授权开销实验。
- **局限**：不提供链状态版本、单次数据库Nonce或PoP本身。
- **与你方案相同点**：都要求能力绑定资源、上下文和限制。
- **不同点**：CAP2是签名与状态绑定结构，不是Macaroon链式MAC。
- **可支撑表述**：可支撑能力安全、衰减和上下文约束。
- **不能支撑的过强表述**：不能声称CAP2是Macaroons的密码学改进。
- **推荐阅读**：威胁模型、构造、caveat、验证、性能；建议顺序=11；必须下载全文=是。

## L24 OAuth 2.0 Demonstrating Proof of Possession (DPoP)
- **作者、年份与来源**：Daniel Fett; Brian Campbell; John Bradley; Torsten Lodderstedt; Michael B. Jones; David Waite（2023），IETF RFC 9449。
- **DOI**：10.17487/RFC9449。
- **双源核验**：https://www.rfc-editor.org/rfc/rfc9449；https://datatracker.ietf.org/doc/rfc9449/。
- **发表状态**：正式IETF RFC（标准规范）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30已检查RFC Editor信息页；实现时仍应固定RFC正文与当日勘误状态。
- **等级与评分**：A；Q1–Q8=5/4/3/5/3/4/5/4。
- **主要问题**：通过持有证明减少Bearer访问令牌被窃后的重放。
- **核心方法**：使用请求绑定签名证明、随机标识、方法和URI等声明。
- **主要结论**：防重放需要把凭证与请求、密钥和受众绑定，而非只验签。
- **实验环境/证据类型**：规范和安全考虑。
- **局限**：OAuth/HTTP语境，不等同链状态和数据库Nonce。
- **与你方案相同点**：与CAP2上下文绑定、受众限制和重放拒绝直接类比。
- **不同点**：CAP2绑定链、合约、资源和状态版本，DPoP绑定HTTP请求和密钥。
- **可支撑表述**：可支撑PoP、请求绑定和重放威胁。
- **不能支撑的过强表述**：不能声称CAP2已经符合OAuth标准。
- **推荐阅读**：协议、证明字段、Nonce、安全考虑；建议顺序=29；必须下载全文=是。

## L25 基于区块链的大数据访问控制机制
- **作者、年份与来源**：刘敖迪; 杜学绘; 王娜; 李少卓（2019），软件学报, 30(9): 2636–2654。
- **DOI**：10.13328/j.cnki.jos.005771。
- **双源核验**：https://www.jos.org.cn/1000-9825/5771.html；https://dds.sciengine.com/cfs/files/pdfs/1000-9825/C12F884627AB402899518D1EDB5C5CEC.pdf。
- **发表状态**：正式发表（中文核心期刊论文）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：A；Q1–Q8=4/4/3/5/3/4/4/4。
- **主要问题**：结合ABAC、区块链和智能合约实现大数据访问控制。
- **核心方法**：形式化ABAC、链上管理策略与实体属性、智能合约执行授权并仿真实验。
- **主要结论**：链上记录可增强审计与验证，但平台性能和链下执行边界仍需分析。
- **实验环境/证据类型**：区块链仿真实验，具体环境需全文复核。
- **局限**：不等同Besu五节点、CAP2和共享Nonce。
- **与你方案相同点**：链上授权状态和数据共享直接相关。
- **不同点**：你的系统强调能力完整绑定、原子单次消费和真实恢复。
- **可支撑表述**：可支撑国内区块链访问控制研究脉络。
- **不能支撑的过强表述**：不能支撑绝对可信或你的性能数字。
- **推荐阅读**：模型、架构、智能合约、实验；建议顺序=30；必须下载全文=是。

## L26 物联网下的区块链访问控制综述
- **作者、年份与来源**：史锦山; 李茹（2019），软件学报, 30(6): 1632–1648。
- **DOI**：10.13328/j.cnki.jos.005740。
- **双源核验**：https://jos.org.cn/jos/ch/reader/view_abstract.aspx?file_no=5740；https://www.jos.org.cn/jos/article/virtual/20250523142617001。
- **发表状态**：正式发表（中文核心期刊综述）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：A；Q1–Q8=4/4/3/5/3/4/4/4。
- **主要问题**：围绕轻量级、海量节点和动态性总结物联网区块链访问控制。
- **核心方法**：比较传统模型和两类区块链访问控制模型。
- **主要结论**：区块链接入访问控制仍受资源约束、动态性和可扩展性限制。
- **实验环境/证据类型**：综述。
- **局限**：截至2019，不能代表最新Besu和智能合约实践。
- **与你方案相同点**：覆盖能力、智能合约和IoT访问控制。
- **不同点**：你的系统是明确的联盟链多节点授权闭环。
- **可支撑表述**：可用于中文相关工作分类。
- **不能支撑的过强表述**：不能替代具体竞争论文的逐项比较。
- **推荐阅读**：分类框架、三类问题、代表方案、未来问题；建议顺序=31；必须下载全文=是。

## L27 Practical Byzantine Fault Tolerance
- **作者、年份与来源**：Miguel Castro; Barbara Liskov（1999），USENIX OSDI 1999: 173–186。
- **DOI**：无DOI/不适用。
- **双源核验**：https://www.usenix.org/legacy/events/osdi99/full_papers/castro/castro.pdf；https://dblp.org/rec/conf/osdi/CastroL99。
- **发表状态**：正式发表（同行评审系统会议论文；无DOI）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：S；Q1–Q8=5/5/5/5/3/4/5/5。
- **主要问题**：在拜占庭故障和异步通信下实现实用状态机复制。
- **核心方法**：三阶段协议、视图变更、认证消息和3f+1副本。
- **主要结论**：BFT安全与活性依赖故障阈值、法定人数交集、网络和实现假设。
- **实验环境/证据类型**：NFS等原型性能实验。
- **局限**：不是区块链共识实现，也不是QBFT规范。
- **与你方案相同点**：为4验证节点容忍1故障提供理论背景。
- **不同点**：Besu QBFT有区块、提议者、轮次和具体工程参数。
- **可支撑表述**：可支撑BFT阈值和法定人数基础。
- **不能支撑的过强表述**：不能直接证明你的Besu网络满足全部PBFT假设。
- **推荐阅读**：系统模型、正常路径、视图变更、安全活性、实验；建议顺序=14；必须下载全文=是。

## L28 Practical Byzantine Fault Tolerance and Proactive Recovery
- **作者、年份与来源**：Miguel Castro; Barbara Liskov（2002），ACM Transactions on Computer Systems, 20(4)。
- **DOI**：10.1145/571637.571640。
- **双源核验**：https://dl.acm.org/doi/10.1145/571637.571640；https://dblp.org/rec/journals/tocs/CastroL02。
- **发表状态**：正式发表（同行评审期刊论文）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：A；Q1–Q8=5/4/5/5/3/4/4/4。
- **主要问题**：通过主动恢复应对长期运行中逐步被攻陷的副本。
- **核心方法**：周期恢复、状态传输和密钥更新。
- **主要结论**：长期容错不只依赖单轮阈值，还涉及恢复、密钥和运维。
- **实验环境/证据类型**：BFT原型和恢复开销。
- **局限**：你的部署未实现完整主动恢复协议。
- **与你方案相同点**：强调恢复与长期运行证据。
- **不同点**：你的节点重启恢复不能称为proactive recovery。
- **可支撑表述**：可支撑故障恢复边界。
- **不能支撑的过强表述**：不能把普通重启测试描述为主动拜占庭恢复。
- **推荐阅读**：恢复机制、安全假设、状态传输、实验；建议顺序=32；必须下载全文=是。

## L29 Hyperledger Fabric: A Distributed Operating System for Permissioned Blockchains
- **作者、年份与来源**：Elli Androulaki et al.（2018），ACM EuroSys 2018。
- **DOI**：10.1145/3190508.3190538。
- **双源核验**：https://dl.acm.org/doi/10.1145/3190508.3190538；https://dblp.org/rec/conf/eurosys/AndroulakiBBCCC18。
- **发表状态**：正式发表（同行评审系统会议论文）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：A；Q1–Q8=4/4/3/5/5/4/4/4。
- **主要问题**：提出模块化许可链架构与execute-order-validate流程。
- **核心方法**：身份许可、背书、排序、验证和可插拔状态数据库。
- **主要结论**：许可链的信任和性能由执行架构、背书、排序和状态数据库共同决定。
- **实验环境/证据类型**：Fabric集群与多工作负载性能。
- **局限**：不是Besu/QBFT，交易流程差异显著。
- **与你方案相同点**：许可链、多节点、状态读取和真实实验相关。
- **不同点**：Fabric和企业Ethereum不能直接互作性能基线。
- **可支撑表述**：可支撑许可链设计空间。
- **不能支撑的过强表述**：不能把Fabric吞吐直接作为Besu基线。
- **推荐阅读**：架构、交易流、信任模型、性能；建议顺序=33；必须下载全文=是。

## L30 BLOCKBENCH: A Framework for Analyzing Private Blockchains
- **作者、年份与来源**：Tien Tuan Anh Dinh; Ji Wang; Gang Chen; Rui Liu; Beng Chin Ooi; Kian-Lee Tan（2017），ACM SIGMOD 2017: 1085–1100。
- **DOI**：10.1145/3035918.3064033。
- **双源核验**：https://dl.acm.org/doi/10.1145/3035918.3064033；https://dblp.org/rec/conf/sigmod/DinhW0LOT17。
- **发表状态**：正式发表（同行评审数据库会议论文；有arXiv前版）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：A；Q1–Q8=5/4/3/5/5/4/4/4。
- **主要问题**：建立私有链的分层性能与功能基准。
- **核心方法**：宏/微基准测量吞吐、延迟、可扩展性和故障容忍。
- **主要结论**：不能只报TPS；应拆分共识、执行和状态访问瓶颈。
- **实验环境/证据类型**：Ethereum、Parity、Fabric私有链实验。
- **局限**：平台版本较旧，不含当前Besu。
- **与你方案相同点**：可借鉴链读、交易、并发和组件分解。
- **不同点**：你的核心是授权端到端配对，不是通用链排行榜。
- **可支撑表述**：可支撑基准结构和瓶颈拆解。
- **不能支撑的过强表述**：不能复用旧平台数值。
- **推荐阅读**：基准设计、工作负载、指标、结果解释；建议顺序=34；必须下载全文=是。

## L31 IBFT 2.0: A Safe and Live Variation of the IBFT Blockchain Consensus Protocol for Eventually Synchronous Networks
- **作者、年份与来源**：Roberto Saltini; David Hyland-Wood（2019），arXiv:1909.10194。
- **DOI**：10.48550/arXiv.1909.10194。
- **双源核验**：https://arxiv.org/abs/1909.10194；https://dblp.org/rec/journals/corr/abs-1909-10194。
- **发表状态**：仅预印本；未核验正式同行评审版本；预印本：仅为arXiv预印本；未找到正式发表版本。
- **撤稿/勘误核验**：arXiv版本可能更新；引用时固定版本日期。
- **等级与评分**：A；Q1–Q8=3/4/5/5/3/4/5/4。
- **主要问题**：给出面向最终同步网络的IBFT 2.0安全与活性变体。
- **核心方法**：区块链化BFT轮次、消息和证明分析。
- **主要结论**：IBFT类协议性质必须精确到网络同步和轮次假设。
- **实验环境/证据类型**：理论协议。
- **局限**：仅预印本，也不是Besu当前QBFT实现规范。
- **与你方案相同点**：与QBFT/IBFT类共识直接相关。
- **不同点**：实现依据必须以Besu官方文档和固定版本为准。
- **可支撑表述**：可支撑IBFT类理论背景。
- **不能支撑的过强表述**：不能作为Besu实现细节唯一权威来源。
- **推荐阅读**：模型、协议、安全、活性；建议顺序=35；必须下载全文=是。

## L32 QBFT Consensus Protocol
- **作者、年份与来源**：Hyperledger Besu Project（2026），Hyperledger Besu Current Documentation。
- **DOI**：无DOI/不适用。
- **双源核验**：https://besu.hyperledger.org/private-networks/how-to/configure/consensus/qbft；https://besu.hyperledger.org/private-networks/concepts/poa。
- **发表状态**：官方工程规范（持续更新，不是学术论文）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：持续更新文档；论文必须记录Besu版本、访问日期和关键配置快照。
- **等级与评分**：S；Q1–Q8=4/5/3/5/3/4/5/5。
- **主要问题**：规定Besu QBFT网络的验证者、配置、最终性和故障条件。
- **核心方法**：实现文档与配置参数说明。
- **主要结论**：至少4个验证者才能在1个验证者故障条件下满足官方建议；最终性仍依赖验证者集合和网络假设。
- **实验环境/证据类型**：官方文档，无独立同行评审基准。
- **局限**：工程规范不是共识理论证明，且会随版本变化。
- **与你方案相同点**：直接对应4 Validator + 1 RPC部署。
- **不同点**：不能替代PBFT/IBFT理论文献。
- **可支撑表述**：可支撑Besu版本、配置和工程行为。
- **不能支撑的过强表述**：不能支撑绝对可信状态或可信时间。
- **推荐阅读**：概念、配置、验证者管理、故障条件；建议顺序=15；必须下载全文=是。

## L33 Design and Analysis of Practical Public-Key Encryption Schemes Secure against Adaptive Chosen Ciphertext Attack
- **作者、年份与来源**：Ronald Cramer; Victor Shoup（2003），SIAM Journal on Computing, 33(1): 167–226。
- **DOI**：10.1137/S0097539702403773。
- **双源核验**：https://epubs.siam.org/doi/10.1137/S0097539702403773；https://dblp.org/rec/journals/siamcomp/CramerS03。
- **发表状态**：正式发表（同行评审期刊论文）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：A；Q1–Q8=4/4/5/3/3/4/4/4。
- **主要问题**：构造实用CCA安全公钥加密并推动KEM/DEM设计范式。
- **核心方法**：公钥加密构造、哈希证明与安全归约。
- **主要结论**：混合加密必须明确封装层和数据加密层的安全组合。
- **实验环境/证据类型**：理论为主。
- **局限**：不是HPKE标准或文件格式。
- **与你方案相同点**：支撑CK封装与Body AEAD分层。
- **不同点**：你的实现采用RFC 9180标准套件。
- **可支撑表述**：可支撑KEM/DEM和CCA安全背景。
- **不能支撑的过强表述**：不能直接支撑HPKE互操作或Header协议。
- **推荐阅读**：安全模型、构造、证明与效率；建议顺序=36；必须下载全文=是。

## L34 Hybrid Public Key Encryption
- **作者、年份与来源**：Richard Barnes; Karthikeyan Bhargavan; Benjamin Lipp; Christopher A. Wood（2022），IETF RFC 9180。
- **DOI**：10.17487/RFC9180。
- **双源核验**：https://www.rfc-editor.org/rfc/rfc9180；https://datatracker.ietf.org/doc/rfc9180/。
- **发表状态**：正式IETF RFC；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：RFC Editor存在公开勘误条目；实现应固定RFC正文与截至实现日期的勘误状态。
- **等级与评分**：S；Q1–Q8=5/5/5/3/3/5/5/5。
- **主要问题**：标准化KEM、KDF和AEAD组合的混合公钥加密。
- **核心方法**：定义Base/PSK/Auth/AuthPSK模式、密钥调度、info、AAD和测试向量。
- **主要结论**：HPKE安全依赖套件、模式、上下文和nonce管理；多接收者结构由应用层定义。
- **实验环境/证据类型**：标准与测试向量。
- **局限**：不定义VersionedHeader、多接收者记录或撤销。
- **与你方案相同点**：直接对应X25519/HKDF-SHA256/AES-128-GCM RecipientEnvelope。
- **不同点**：VersionedHeaderV1是应用层协议。
- **可支撑表述**：可支撑HPKE算法、模式和互操作选择。
- **不能支撑的过强表述**：不能声称RFC定义了你的Header或撤销闭环。
- **推荐阅读**：术语、密钥调度、模式、AAD、安全考虑、测试向量；建议顺序=7；必须下载全文=是。

## L35 Analysing the HPKE Standard
- **作者、年份与来源**：Joël Alwen; Bruno Blanchet; Eduard Hauck; Eike Kiltz; Benjamin Lipp; Doreen Riepel（2021），EUROCRYPT 2021: 87–116。
- **DOI**：10.1007/978-3-030-77870-5_4。
- **双源核验**：https://link.springer.com/chapter/10.1007/978-3-030-77870-5_4；https://dblp.org/rec/conf/eurocrypt/AlwenBHKLR21。
- **发表状态**：正式发表（同行评审密码学会议论文；有IACR ePrint前版）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：S；Q1–Q8=5/5/5/3/3/5/5/5。
- **主要问题**：形式化分析HPKE模式和密钥调度。
- **核心方法**：使用计算安全工具与证明研究标准草案/模式性质。
- **主要结论**：采用标准并不等于应用协议自动安全，必须限定证明范围。
- **实验环境/证据类型**：形式化验证，无端到端系统性能。
- **局限**：不分析HeaderRegistry、KeyStore和任务恢复。
- **与你方案相同点**：直接帮助审查HPKE context和AAD绑定。
- **不同点**：整个系统的安全论证必须分层。
- **可支撑表述**：可支撑HPKE安全分析和证据边界。
- **不能支撑的过强表述**：不能把局部证明扩展为整个系统形式化证明。
- **推荐阅读**：模型、模式、密钥调度、证明范围和限制；建议顺序=8；必须下载全文=是。

## L36 An Interface and Algorithms for Authenticated Encryption
- **作者、年份与来源**：David McGrew（2008），IETF RFC 5116。
- **DOI**：10.17487/RFC5116。
- **双源核验**：https://www.rfc-editor.org/rfc/rfc5116；https://datatracker.ietf.org/doc/rfc5116/。
- **发表状态**：正式IETF RFC；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：已检查RFC Editor勘误页面；实现时固定勘误状态。
- **等级与评分**：A；Q1–Q8=5/4/3/3/3/4/4/4。
- **主要问题**：定义AEAD接口、nonce和AAD语义。
- **核心方法**：统一AEAD输入输出和算法注册。
- **主要结论**：nonce唯一性、AAD和失败处理是分块加密正确性的关键。
- **实验环境/证据类型**：规范。
- **局限**：不定义分块文件framing或崩溃恢复。
- **与你方案相同点**：直接对应Body分块AEAD和Header字段AAD。
- **不同点**：你的格式还需块序号、长度、截断和重排检测。
- **可支撑表述**：可支撑AEAD接口与nonce要求。
- **不能支撑的过强表述**：不能证明自定义分块格式无截断漏洞。
- **推荐阅读**：接口、nonce、AAD、安全考虑；建议顺序=37；必须下载全文=是。

## L37 Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode (GCM) and GMAC
- **作者、年份与来源**：Morris Dworkin（2007），NIST SP 800-38D。
- **DOI**：10.6028/NIST.SP.800-38D。
- **双源核验**：https://csrc.nist.gov/pubs/sp/800/38/d/final；https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38d.pdf。
- **发表状态**：正式NIST规范；NIST已开展修订；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：NIST已宣布修订SP 800-38D；论文应固定使用版本并跟踪最终修订。
- **等级与评分**：A；Q1–Q8=5/4/3/3/3/4/5/4。
- **主要问题**：规范AES-GCM/GMAC及IV、标签和使用限制。
- **核心方法**：模式定义、IV构造与安全边界。
- **主要结论**：重复IV可灾难性破坏安全，分块方案必须定义唯一nonce派生。
- **实验环境/证据类型**：规范与测试要求。
- **局限**：不定义HPKE和应用Header。
- **与你方案相同点**：直接对应AES-256-GCM Body与HPKE AEAD。
- **不同点**：两层GCM使用不同密钥和上下文。
- **可支撑表述**：可支撑GCM参数、标签与nonce管理。
- **不能支撑的过强表述**：不能支撑任意自定义nonce方案。
- **推荐阅读**：IV构造、标签、数据量限制、安全考虑；建议顺序=38；必须下载全文=是。

## L38 Elliptic Curves for Security
- **作者、年份与来源**：Adam Langley; Mike Hamburg; Sean Turner（2016），IETF RFC 7748。
- **DOI**：10.17487/RFC7748。
- **双源核验**：https://www.rfc-editor.org/rfc/rfc7748；https://datatracker.ietf.org/doc/rfc7748/。
- **发表状态**：正式IETF RFC；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：已检查RFC Editor勘误页面；实现时固定勘误状态。
- **等级与评分**：A；Q1–Q8=5/4/3/3/3/4/4/4。
- **主要问题**：标准化X25519和X448。
- **核心方法**：Montgomery曲线标量乘法、编码和测试向量。
- **主要结论**：实现必须遵循输入处理、标量钳制和共享秘密要求。
- **实验环境/证据类型**：规范。
- **局限**：不定义HPKE完整协议。
- **与你方案相同点**：直接对应HPKE KEM的X25519。
- **不同点**：KeyStore、接收者身份和版本绑定在应用层。
- **可支撑表述**：可支撑X25519参数与互操作。
- **不能支撑的过强表述**：不能证明密钥存储安全。
- **推荐阅读**：算法、编码、安全考虑、测试向量；建议顺序=39；必须下载全文=是。

## L39 HMAC-based Extract-and-Expand Key Derivation Function (HKDF)
- **作者、年份与来源**：Hugo Krawczyk; Pasi Eronen（2010），IETF RFC 5869。
- **DOI**：10.17487/RFC5869。
- **双源核验**：https://www.rfc-editor.org/rfc/rfc5869；https://datatracker.ietf.org/doc/rfc5869/。
- **发表状态**：正式IETF RFC；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：已检查RFC Editor勘误页面；实现时固定勘误状态。
- **等级与评分**：A；Q1–Q8=5/4/3/3/3/4/4/4。
- **主要问题**：标准化extract-then-expand密钥派生。
- **核心方法**：HMAC提取与扩展，定义salt和info。
- **主要结论**：域分离和info语义必须明确，不能随意复用密钥上下文。
- **实验环境/证据类型**：规范。
- **局限**：不定义应用密钥层次。
- **与你方案相同点**：直接对应HPKE HKDF-SHA256。
- **不同点**：V1不引入未经论证的KEK_e。
- **可支撑表述**：可支撑HKDF使用和域分离。
- **不能支撑的过强表述**：不能支撑任意自定义KDF字段。
- **推荐阅读**：Extract、Expand、salt/info、安全考虑；建议顺序=40；必须下载全文=是。

## L40 Edwards-Curve Digital Signature Algorithm (EdDSA)
- **作者、年份与来源**：Simon Josefsson; Ilari Liusvaara（2017），IETF RFC 8032。
- **DOI**：10.17487/RFC8032。
- **双源核验**：https://www.rfc-editor.org/rfc/rfc8032；https://datatracker.ietf.org/doc/rfc8032/。
- **发表状态**：正式IETF RFC；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：RFC Editor存在公开勘误记录；实现应固定正文与勘误状态。
- **等级与评分**：A；Q1–Q8=5/4/3/5/3/4/5/4。
- **主要问题**：标准化Ed25519/Ed448签名。
- **核心方法**：定义签名、编码、验证和测试向量。
- **主要结论**：签名保护明确字节串；跨实现必须固定规范化编码。
- **实验环境/证据类型**：规范。
- **局限**：不解决签名密钥的HSM级保护。
- **与你方案相同点**：直接对应SignedVersionedHeader。
- **不同点**：软件KeyStore仅为原型边界。
- **可支撑表述**：可支撑Ed25519算法和测试向量。
- **不能支撑的过强表述**：不能把软件KeyStore描述为HSM。
- **推荐阅读**：Ed25519、编码、验证、测试向量、安全考虑；建议顺序=41；必须下载全文=是。

## L41 JSON Canonicalization Scheme (JCS)
- **作者、年份与来源**：Anders Rundgren; Bret Jordan; Samuel Erdtman（2020），IETF RFC 8785。
- **DOI**：10.17487/RFC8785。
- **双源核验**：https://www.rfc-editor.org/rfc/rfc8785；https://datatracker.ietf.org/doc/rfc8785/。
- **发表状态**：正式IETF RFC；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，RFC Editor列有已验证技术勘误，包括负零（-0）规范化处理；实现必须合并已验证勘误。
- **等级与评分**：A；Q1–Q8=5/4/3/5/3/4/5/4。
- **主要问题**：为JSON签名和哈希提供确定性规范化。
- **核心方法**：I-JSON约束、属性排序、数值和字符串序列化。
- **主要结论**：摘要与签名必须绑定规范化字节，而非抽象对象。
- **实验环境/证据类型**：规范与示例。
- **局限**：不定义字段语义、版本链或回滚保护。
- **与你方案相同点**：直接对应HeaderCore和SignedVersionedHeader。
- **不同点**：policyDigest与Header摘要的域分离由你的协议定义。
- **可支撑表述**：可支撑JCS选型和跨实现一致性。
- **不能支撑的过强表述**：不能证明整个Header协议安全。
- **推荐阅读**：输入约束、排序、数值/字符串、测试；建议顺序=42；必须下载全文=是。

## L42 Plutus: Scalable Secure File Sharing on Untrusted Storage
- **作者、年份与来源**：Mahesh Kallahalla; Erik Riedel; Ram Swaminathan; Qian Wang; Kevin Fu（2003），USENIX FAST 2003。
- **DOI**：无DOI/不适用。
- **双源核验**：https://www.usenix.org/legacy/events/fast03/tech/full_papers/kallahalla/kallahalla.pdf；https://dblp.org/rec/conf/fast/KallahallaRSWF03。
- **发表状态**：正式发表（同行评审系统会议论文；无DOI）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：S；Q1–Q8=4/5/5/3/3/5/5/5。
- **主要问题**：在不可信存储上实现可扩展安全文件共享和密钥管理。
- **核心方法**：文件组、密钥层次、签名和lazy revocation。
- **主要结论**：惰性/前瞻性撤销通常只保护后续更新，已获得的旧密文、密钥和明文无法收回。
- **实验环境/证据类型**：原型文件系统与性能实验。
- **局限**：密码和系统年代较早，不是HPKE或链上注册表。
- **与你方案相同点**：与你的前瞻性撤销边界高度一致。
- **不同点**：你的每Body版本独立CK并重建多接收者Header。
- **可支撑表述**：可支撑撤销不追溯收回既得材料。
- **不能支撑的过强表述**：不能支撑完全即时追溯撤销。
- **推荐阅读**：威胁模型、密钥管理、撤销、性能；建议顺序=6；必须下载全文=是。

## L43 Key Regression: Enabling Efficient Key Distribution for Secure Distributed Storage
- **作者、年份与来源**：Kevin Fu; Seny Kamara; Tadayoshi Kohno（2006），NDSS 2006。
- **DOI**：10.14722/ndss.2006.23231。
- **双源核验**：https://www.ndss-symposium.org/ndss2006/key-regression-enabling-efficient-key-distribution-secure-distributed-storage/；https://dblp.org/rec/conf/ndss/FuKK06。
- **发表状态**：正式发表（同行评审安全会议论文）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：A；Q1–Q8=4/4/5/3/3/4/4/4。
- **主要问题**：在版本化存储中高效派生历史/未来密钥并控制暴露方向。
- **核心方法**：单向密钥演进与回归。
- **主要结论**：密钥更新必须明确暴露后可推导的版本方向和安全目标。
- **实验环境/证据类型**：原型与性能分析。
- **局限**：你的V1明确不采用key regression或KEK_e。
- **与你方案相同点**：都涉及版本、密钥演进和撤销。
- **不同点**：每Body独立CK更简单但封装数量随接收者增长。
- **可支撑表述**：可解释为何不引入复杂密钥层次及权衡。
- **不能支撑的过强表述**：不能声称独立CK具有key regression效率。
- **推荐阅读**：安全目标、构造、存储应用、性能；建议顺序=43；必须下载全文=是。

## L44 Self-Updatable Encryption: Time Constrained Access Control with Hidden Attributes and Better Efficiency
- **作者、年份与来源**：Taehoon Lee; SeongHan Shin; Kwangsu Lee; Jung Hee Cheon（2013），ASIACRYPT 2013。
- **DOI**：10.1007/978-3-642-42033-7_13。
- **双源核验**：https://link.springer.com/chapter/10.1007/978-3-642-42033-7_13；https://dblp.org/rec/conf/asiacrypt/LeeSLC13。
- **发表状态**：正式发表（同行评审密码学会议论文）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：A；Q1–Q8=5/4/5/3/3/5/4/4。
- **主要问题**：让密文可随时间更新并实现时间约束访问。
- **核心方法**：自更新密文、时间编码和安全证明。
- **主要结论**：时间约束与密文更新可在密码层实现，但威胁模型和成本与在线授权不同。
- **实验环境/证据类型**：理论与运算成本。
- **局限**：不采用HPKE，也不处理区块链和任务恢复。
- **与你方案相同点**：时间、版本和撤销交叉。
- **不同点**：你的时间策略在授权层，Header更新在系统层。
- **可支撑表述**：可作为竞争路线和创新边界。
- **不能支撑的过强表述**：不能说你的系统实现SUE性质。
- **推荐阅读**：模型、时间结构、更新算法、安全证明；建议顺序=44；必须下载全文=是。

## L45 Survivable Key Compromise in Software Update Systems
- **作者、年份与来源**：Justin Samuel; Nick Mathewson; Justin Cappos; Roger Dingledine（2010），ACM CCS 2010: 61–72。
- **DOI**：10.1145/1866307.1866315。
- **双源核验**：https://dl.acm.org/doi/10.1145/1866307.1866315；https://dblp.org/rec/conf/ccs/SamuelMCD10。
- **发表状态**：正式发表（同行评审安全会议论文）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：A；Q1–Q8=5/4/3/5/3/5/5/4。
- **主要问题**：在密钥被攻陷时保护软件更新元数据并抵抗回滚和冻结攻击。
- **核心方法**：角色分离、阈值签名、版本/过期元数据。
- **主要结论**：签名元数据必须同时考虑回滚、冻结、密钥轮换和恢复。
- **实验环境/证据类型**：原型与攻击场景。
- **局限**：软件更新场景和信任模型不同。
- **与你方案相同点**：版本化、签名元数据和回滚保护相关。
- **不同点**：你的Header使用previousHeaderDigest和链上HeaderRegistry。
- **可支撑表述**：可支撑版本/回滚威胁模型。
- **不能支撑的过强表述**：不能说VersionedHeader自动达到TUF全部目标。
- **推荐阅读**：攻击模型、元数据角色、回滚/冻结、恢复；建议顺序=45；必须下载全文=是。

## L46 in-toto: Providing Farm-to-Table Guarantees for Bits and Bytes
- **作者、年份与来源**：Santiago Torres-Arias; Hammad Afzali; Trishank Karthik Kuppusamy; Reza Curtmola; Justin Cappos（2019），USENIX Security 2019。
- **DOI**：无DOI/不适用。
- **双源核验**：https://www.usenix.org/conference/usenixsecurity19/presentation/torres-arias；https://dblp.org/rec/conf/uss/Torres-AriasAKC19。
- **发表状态**：正式发表（同行评审安全会议论文；USENIX无DOI）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：A；Q1–Q8=5/4/3/5/3/4/4/4。
- **主要问题**：通过签名布局和链接元数据保证供应链步骤完整性。
- **核心方法**：签名layout/link、步骤约束和验证。
- **主要结论**：可验证元数据需要明确主体、步骤、材料和产物绑定。
- **实验环境/证据类型**：开源实现和案例。
- **局限**：不是加密文件Header或撤销系统。
- **与你方案相同点**：签名、哈希链接、不可变对象和审计相关。
- **不同点**：你的链是Header版本链而非构建步骤链。
- **可支撑表述**：可支撑哈希链接元数据和可审计设计。
- **不能支撑的过强表述**：不能证明你的Header达到供应链保证。
- **推荐阅读**：威胁模型、layout/link、验证、案例；建议顺序=46；必须下载全文=是。

## L47 Venti: A New Approach to Archival Storage
- **作者、年份与来源**：Sean Quinlan; Sean Dorward（2002），USENIX FAST 2002。
- **DOI**：无DOI/不适用。
- **双源核验**：https://www.usenix.org/conference/fast-02/venti-new-approach-archival-data-storage；https://dblp.org/rec/conf/fast/QuinlanD02。
- **发表状态**：正式发表（同行评审系统会议论文；无DOI）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：A；Q1–Q8=4/4/3/5/3/4/4/4。
- **主要问题**：利用内容哈希构建写一次、去重的归档存储。
- **核心方法**：内容寻址块存储和不可变对象。
- **主要结论**：内容地址可验证对象身份和去重，但不提供访问控制、机密性或持久可用性。
- **实验环境/证据类型**：Venti原型、吞吐和存储效率。
- **局限**：使用历史环境，不能直接作为现代密码配置。
- **与你方案相同点**：与LocalObjectStore不可变对象和SHA-256寻址相关。
- **不同点**：你的对象还需加密、签名Header、原子写和链上注册。
- **可支撑表述**：可支撑内容寻址设计。
- **不能支撑的过强表述**：不能支撑IPFS永久可用或保密。
- **推荐阅读**：架构、内容寻址、完整性、性能；建议顺序=47；必须下载全文=是。

## L48 IPFS - Content Addressed, Versioned, P2P File System
- **作者、年份与来源**：Juan Benet（2014），arXiv:1407.3561 / Protocol Labs technical paper。
- **DOI**：10.48550/arXiv.1407.3561。
- **双源核验**：https://arxiv.org/abs/1407.3561；https://research.protocol.ai/publications/ipfs-content-addressed-versioned-p2p-file-system/。
- **发表状态**：仅预印本/技术论文；未作为正式同行评审论文发表；预印本：仅为arXiv/技术论文；无正式同行评审版本。
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：B；Q1–Q8=3/3/3/5/3/4/5/3。
- **主要问题**：提出内容寻址、Merkle DAG和P2P对象交换的IPFS设计。
- **核心方法**：DHT、BitSwap、自认证命名与Merkle DAG。
- **主要结论**：CID绑定内容，不绑定授权、机密性或持久保存。
- **实验环境/证据类型**：早期设计与原型。
- **局限**：非正式同行评审，现实网络已演化。
- **与你方案相同点**：对应未来LocalObjectStore到Kubo/IPFS接入。
- **不同点**：密码安全来自加密、签名和状态验证，不来自IPFS。
- **可支撑表述**：可支撑IPFS架构背景。
- **不能支撑的过强表述**：不能支撑“IPFS保证安全、永久或私密”。
- **推荐阅读**：对象模型、Merkle DAG、命名、交换、限制；建议顺序=48；必须下载全文=是。

## L49 The Eternal Tussle: Exploring the Role of Centralization in IPFS
- **作者、年份与来源**：Yiluo Wei; Dennis Trautwein; Yiannis Psaras; Ignacio Castro; Will Scott; Aravindh Raman; Gareth Tyson（2024），USENIX NSDI 2024: 441–454。
- **DOI**：无DOI/不适用。
- **双源核验**：https://www.usenix.org/conference/nsdi24/presentation/wei；https://dblp.org/rec/conf/nsdi/WeiTPCSR024。
- **发表状态**：正式发表（同行评审系统会议论文；无DOI）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：A；Q1–Q8=5/4/3/5/5/4/5/4。
- **主要问题**：实证分析IPFS网关、提供者和中心化依赖。
- **核心方法**：大规模公开网络测量与组件分析。
- **主要结论**：去中心化协议的现实部署可能依赖中心网关和基础设施，影响可用性和信任。
- **实验环境/证据类型**：公开IPFS网络测量。
- **局限**：不直接分析LocalObjectStore或加密格式。
- **与你方案相同点**：用于评估未来接入IPFS后的可用性和信任边界。
- **不同点**：V1先使用本地不可变对象存储。
- **可支撑表述**：可支撑IPFS现实中心化和可用性风险。
- **不能支撑的过强表述**：不能泛化为所有IPFS部署都不安全。
- **推荐阅读**：测量方法、网关/提供者结果、限制；建议顺序=18；必须下载全文=是。

## L50 Sagas
- **作者、年份与来源**：Hector Garcia-Molina; Kenneth Salem（1987），ACM SIGMOD 1987。
- **DOI**：10.1145/38713.38742。
- **双源核验**：https://dl.acm.org/doi/10.1145/38713.38742；https://dblp.org/rec/conf/sigmod/Garcia-MolinaS87。
- **发表状态**：正式发表（同行评审数据库会议论文）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：S；Q1–Q8=5/5/5/5/3/5/5/5。
- **主要问题**：用可补偿长事务替代长期持锁的全局事务。
- **核心方法**：把长事务分解为子事务和补偿事务。
- **主要结论**：跨链、数据库和对象存储难以获得单一ACID原子性，必须显式设计补偿和恢复状态。
- **实验环境/证据类型**：理论与调度示例。
- **局限**：补偿不能撤回已被外部观察的不可逆效果。
- **与你方案相同点**：直接对应持久任务状态机、重试、补偿和恢复审计。
- **不同点**：你的流程还需处理链交易UNKNOWN和不可变对象。
- **可支撑表述**：可支撑采用Saga/状态机而非伪装全局原子事务。
- **不能支撑的过强表述**：不能声称补偿提供严格全局原子性。
- **推荐阅读**：Saga定义、调度、补偿、故障语义；建议顺序=16；必须下载全文=是。

## L51 Consensus on Transaction Commit
- **作者、年份与来源**：Jim Gray; Leslie Lamport（2006），ACM Transactions on Database Systems, 31(1)。
- **DOI**：10.1145/1132863.1132867。
- **双源核验**：https://dl.acm.org/doi/10.1145/1132863.1132867；https://dblp.org/rec/journals/tods/GrayL06。
- **发表状态**：正式发表（同行评审期刊论文）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：A；Q1–Q8=5/4/5/5/3/4/5/4。
- **主要问题**：比较事务提交和共识并提出Paxos Commit。
- **核心方法**：把提交问题映射为共识实例。
- **主要结论**：提交结果未知和协调者故障是核心问题，不能用盲目重试掩盖。
- **实验环境/证据类型**：理论协议分析。
- **局限**：你的系统未实施Paxos Commit。
- **与你方案相同点**：有助于定义COMMITTED、UNKNOWN和恢复查询。
- **不同点**：你的方案使用幂等、回执恢复和状态机。
- **可支撑表述**：可支撑UNKNOWN结果和提交语义。
- **不能支撑的过强表述**：不能把你的流程称为Paxos Commit或严格原子提交。
- **推荐阅读**：问题、2PC比较、Paxos Commit、故障场景；建议顺序=49；必须下载全文=是。

## L52 Leases: An Efficient Fault-Tolerant Mechanism for Distributed File Cache Consistency
- **作者、年份与来源**：Cary Gray; David Cheriton（1989），ACM SOSP 1989。
- **DOI**：10.1145/74850.74870。
- **双源核验**：https://dl.acm.org/doi/10.1145/74850.74870；https://dblp.org/rec/conf/sosp/GrayC89。
- **发表状态**：正式发表（同行评审系统会议论文）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：A；Q1–Q8=5/4/5/5/3/4/5/4。
- **主要问题**：用有界时间租约在故障下协调缓存一致性和所有权。
- **核心方法**：租约到期、续约和故障恢复。
- **主要结论**：租约降低永久锁风险，但依赖超时/时钟并需防止过期工作者晚到写入。
- **实验环境/证据类型**：分析和系统场景。
- **局限**：租约不等于幂等或CAS。
- **与你方案相同点**：直接对应r3_control工作者租约。
- **不同点**：必须结合operationId、状态版本和CAS阻止陈旧提交。
- **可支撑表述**：可支撑租约设计与边界。
- **不能支撑的过强表述**：不能仅靠租约宣称exactly-once。
- **推荐阅读**：模型、故障、时钟/过期、性能；建议顺序=50；必须下载全文=是。

## L53 Implementing Linearizability at Large Scale and Low Latency
- **作者、年份与来源**：Collin Lee; Seo Jin Park; Ankita Kejriwal; Satoshi Matsushita; John Ousterhout（2015），ACM SOSP 2015: 71–86。
- **DOI**：10.1145/2815400.2815416。
- **双源核验**：https://dl.acm.org/doi/10.1145/2815400.2815416；https://dblp.org/rec/conf/sosp/LeePKMO15。
- **发表状态**：正式发表（同行评审系统会议论文）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：A；Q1–Q8=5/4/3/5/3/4/5/4。
- **主要问题**：通过RIFL等机制在重试和故障下实现线性化和重复请求抑制。
- **核心方法**：唯一请求标识、结果记录、租约和恢复。
- **主要结论**：网络重试下的有效一次效果需要协议状态和去重记录。
- **实验环境/证据类型**：RAMCloud原型、故障和延迟实验。
- **局限**：不是PostgreSQL单次Nonce，exactly-once范围有限。
- **与你方案相同点**：对应operationId、幂等和恢复查询。
- **不同点**：Nonce消费和工作流幂等是两个不同安全问题。
- **可支撑表述**：可支撑重复抑制与重试语义。
- **不能支撑的过强表述**：不能声称唯一约束自动提供端到端exactly-once。
- **推荐阅读**：RIFL、请求跟踪、恢复、实验；建议顺序=51；必须下载全文=是。

## L54 PostgreSQL Documentation: SELECT — Locking Clause and SKIP LOCKED
- **作者、年份与来源**：PostgreSQL Global Development Group（2026），PostgreSQL 18 Current Documentation。
- **DOI**：无DOI/不适用。
- **双源核验**：https://www.postgresql.org/docs/current/sql-select.html；https://www.postgresql.org/docs/16/sql-select.html。
- **发表状态**：官方工程规范（持续更新）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：持续更新文档；论文应引用实际部署的PostgreSQL 16文档并记录版本，当前页仅用于最新交叉核验。
- **等级与评分**：A；Q1–Q8=4/4/3/5/3/4/5/4。
- **主要问题**：定义行锁、NOWAIT和SKIP LOCKED行为。
- **核心方法**：SQL执行语义与锁规范。
- **主要结论**：SKIP LOCKED提供不一致视图，适合队列式多工作者取任务，不适合一般一致性读取。
- **实验环境/证据类型**：规范，需由并发/崩溃实验验证。
- **局限**：不提供完整状态机、租约、重试或审计。
- **与你方案相同点**：直接对应FOR UPDATE SKIP LOCKED。
- **不同点**：还需CAS、租约、幂等和死信。
- **可支撑表述**：可支撑SQL语义和使用边界。
- **不能支撑的过强表述**：不能声称SKIP LOCKED保证公平、exactly-once或无饥饿。
- **推荐阅读**：Locking Clause、SKIP LOCKED、事务隔离；建议顺序=52；必须下载全文=是。

## L55 PostgreSQL Documentation: INSERT — ON CONFLICT
- **作者、年份与来源**：PostgreSQL Global Development Group（2026），PostgreSQL 18 Current Documentation。
- **DOI**：无DOI/不适用。
- **双源核验**：https://www.postgresql.org/docs/current/sql-insert.html；https://www.postgresql.org/docs/16/sql-insert.html。
- **发表状态**：官方工程规范（持续更新）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：持续更新文档；论文应引用实际部署的PostgreSQL 16文档并记录版本。
- **等级与评分**：A；Q1–Q8=4/4/3/5/3/4/5/4。
- **主要问题**：定义唯一约束冲突下的原子插入或更新。
- **核心方法**：唯一索引推断、ON CONFLICT DO NOTHING/UPDATE和并发保证。
- **主要结论**：可用于单次Nonce或幂等键原子争用，但语义受约束和事务隔离设计影响。
- **实验环境/证据类型**：规范，需自行并发故障测试。
- **局限**：不解决跨链/数据库事务。
- **与你方案相同点**：直接对应共享Nonce和operationId。
- **不同点**：Nonce拒绝还需Verifier语义和Fail-Closed处理。
- **可支撑表述**：可支撑原子冲突处理。
- **不能支撑的过强表述**：不能声称提供跨链exactly-once或全局事务。
- **推荐阅读**：ON CONFLICT、唯一索引、并发保证、隔离；建议顺序=53；必须下载全文=是。

## L56 Producing Wrong Data Without Doing Anything Obviously Wrong!
- **作者、年份与来源**：Todd Mytkowicz; Amer Diwan; Matthias Hauswirth; Peter F. Sweeney（2009），ACM ASPLOS 2009。
- **DOI**：10.1145/1508244.1508275。
- **双源核验**：https://dl.acm.org/doi/10.1145/1508244.1508275；https://dblp.org/rec/conf/asplos/MytkowiczDHS09。
- **发表状态**：正式发表（同行评审系统会议论文）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：S；Q1–Q8=4/5/3/3/5/4/5/5。
- **主要问题**：揭示看似无害的环境因素如何扭曲性能结果。
- **核心方法**：控制变量、布局/环境扰动和统计分析。
- **主要结论**：系统实验必须随机化、重复、记录环境并报告不确定性。
- **实验环境/证据类型**：编译器与运行时性能实验。
- **局限**：案例不是区块链，但方法可迁移。
- **与你方案相同点**：直接影响Besu、缓存、并发和Header实验。
- **不同点**：你的运行级配对和冻结环境应落地这些原则。
- **可支撑表述**：可支撑重复、随机化、环境快照和负面结果。
- **不能支撑的过强表述**：不能用大量请求掩盖少量独立运行。
- **推荐阅读**：威胁示例、实验、建议、结论；建议顺序=17；必须下载全文=是。

## L57 Rigorous Benchmarking in Reasonable Time
- **作者、年份与来源**：Tomas Kalibera; Richard Jones（2013），ACM ISMM 2013。
- **DOI**：10.1145/2464157.2464160。
- **双源核验**：https://dl.acm.org/doi/10.1145/2464157.2464160；https://dblp.org/rec/conf/iwmm/KaliberaJ13。
- **发表状态**：正式发表（同行评审会议论文）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：A；Q1–Q8=4/4/3/3/5/4/4/4。
- **主要问题**：在可控成本下识别性能变异层级并分配重复次数。
- **核心方法**：方差分解、层级实验设计和置信区间。
- **主要结论**：应在真正独立层级增加重复，而非无限增加同一运行内请求。
- **实验环境/证据类型**：语言运行时和基准案例。
- **局限**：需按运行、节点、workload重新定义层级。
- **与你方案相同点**：直接支撑运行级实验单位和层级Bootstrap。
- **不同点**：你的配对设计还需按workload-run共同重采样。
- **可支撑表述**：可支撑方差层级和样本量设计。
- **不能支撑的过强表述**：不能把请求数当独立样本量。
- **推荐阅读**：变异层级、方差分解、重复分配、CI；建议顺序=54；必须下载全文=是。

## L58 Stabilizer: Statistically Sound Performance Evaluation
- **作者、年份与来源**：Charlie Curtsinger; Emery D. Berger（2013），ACM ASPLOS 2013。
- **DOI**：10.1145/2451116.2451141。
- **双源核验**：https://dl.acm.org/doi/10.1145/2451116.2451141；https://dblp.org/rec/conf/asplos/CurtsingerB13。
- **发表状态**：正式发表（同行评审系统会议论文）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：A；Q1–Q8=4/4/3/3/5/4/4/4。
- **主要问题**：通过运行时随机化降低代码布局等系统性测量偏差。
- **核心方法**：动态随机化与统计检验。
- **主要结论**：性能差异可能由布局和环境造成，必须设计随机化和重复以获得稳健推断。
- **实验环境/证据类型**：多程序/编译配置实验。
- **局限**：具体工具不能直接用于所有Besu实验。
- **与你方案相同点**：支持环境扰动、随机顺序和稳健差值分析。
- **不同点**：你的系统应在可控范围内随机化运行顺序和配置。
- **可支撑表述**：可支撑统计稳健性和实验顺序设计。
- **不能支撑的过强表述**：不能据其工具宣称你的全部噪声已消除。
- **推荐阅读**：偏差来源、随机化、统计检验、实验；建议顺序=55；必须下载全文=是。

## L59 The Problem of Pseudoreplication in Neuroscientific Studies: Is It Affecting Your Analysis?
- **作者、年份与来源**：Stanley E. Lazic（2010），BMC Neuroscience, 11:5。
- **DOI**：10.1186/1471-2202-11-5。
- **双源核验**：https://bmcneurosci.biomedcentral.com/articles/10.1186/1471-2202-11-5；https://pubmed.ncbi.nlm.nih.gov/20074371/。
- **发表状态**：正式发表（同行评审期刊论文）；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：S；Q1–Q8=4/5/5/3/5/4/5/5。
- **主要问题**：解释把相关观测误当独立重复造成的伪重复。
- **核心方法**：用层级数据示例比较错误和正确分析。
- **主要结论**：同一运行内请求共享状态，不能自动作为独立实验单位。
- **实验环境/证据类型**：方法学案例。
- **局限**：领域为神经科学，但统计原则通用。
- **与你方案相同点**：直接约束请求级记录、运行级单位和Bootstrap层级。
- **不同点**：需转化为系统实验的cluster/run结构。
- **可支撑表述**：可支撑伪重复风险和运行级分析。
- **不能支撑的过强表述**：不能逐请求Bootstrap后声称大量独立样本。
- **推荐阅读**：伪重复类型、示例、正确分析；建议顺序=21；必须下载全文=是。

## L60 An Introduction to the Bootstrap
- **作者、年份与来源**：Bradley Efron; Robert J. Tibshirani（1993），Chapman & Hall/CRC Monographs on Statistics and Applied Probability。
- **DOI**：10.1007/978-1-4899-4541-9。
- **双源核验**：https://link.springer.com/book/10.1007/978-1-4899-4541-9；https://search.worldcat.org/title/An-introduction-to-the-bootstrap/oclc/26809777。
- **发表状态**：正式出版统计专著；预印本：未发现需替代正式版本的同名预印本
- **撤稿/勘误核验**：截至2026-07-30，出版商/DBLP或第二核验页面未见撤稿标识；未进行PubPeer等平台的穷尽性审计。
- **等级与评分**：A；Q1–Q8=4/4/5/3/5/4/4/4。
- **主要问题**：系统介绍Bootstrap估计、标准误和置信区间。
- **核心方法**：非参数重采样、偏差校正和配对数据方法。
- **主要结论**：配对Bootstrap应共同重采样配对实验单位；有层级相关时需按cluster/run设计。
- **实验环境/证据类型**：统计例题和理论。
- **局限**：不会自动确定你的系统实验单位。
- **与你方案相同点**：直接支撑配对Bootstrap和置信区间。
- **不同点**：你的实现应以workload-run配对为主重采样单位。
- **可支撑表述**：可支撑Bootstrap方法和报告。
- **不能支撑的过强表述**：不能把任意逐请求重采样称为正确。
- **推荐阅读**：基本法、置信区间、配对数据、复杂结构；建议顺序=56；必须下载全文=是。
