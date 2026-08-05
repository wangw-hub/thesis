# 6周深度阅读计划

## 第1周：时间策略、时态访问控制和规范化表示
- 必读：L03→L04→L05→L06→L01；选读L02、L07、L08、L44。
- 回答：已有周期授权解决什么；唯一有效授权集与I*有何不同；为何C(P)不能写成普适O(log U)压缩；半开区间和相邻合并如何定义。
- 绘图：时态访问控制谱系、I*规范化流水线、I*/C(P)双层表示。
- 公式：规范化、语义等价、Dyadic分解正确性和输出敏感复杂度。
- 比较表：Temporal Authorization/TRBAC/GTRBAC/I*。
- 对应：第2—4章。验收：无稿证明I*语义保持并说清已有工作边界。

## 第2周：能力安全、Nonce、重放控制和Fail-Closed
- 必读：L23→L24→L18→L53→L55；选读L17、L21。
- 回答：Bearer/PoP/caveated capability差异；CAP2字段阻止何种替换；授权Nonce、operationId和交易Nonce为何不同；失败状态如何Fail-Closed。
- 绘图：CAP2字段—攻击矩阵、Issuer/Verifier/DB时序、拒绝顺序。
- 公式：签名消息、域分离、原子Nonce状态转换。
- 比较表：Macaroons/DPoP/BlendCAC/CAP2。
- 对应：第5章。验收：逐字段解释CAP2并设计至少12个负向测试。

## 第3周：许可链、QBFT、链上状态和多节点授权
- 必读：L27→L31→L32→L20→L30；选读L28、L29、L19、L22、L25。
- 回答：3f+1和法定人数交集；理论、规范和应用论文如何分工引用；4 Validator+1 RPC能证明什么；链读时延如何分解。
- 绘图：QBFT消息流程、五节点拓扑、授权时延分解。
- 公式：故障阈值、法定人数、配对效应量。
- 比较表：Fabric许可链ABAC/SC-CAAC/Besu CAP2。
- 对应：第5—6章。验收：解释故障模型、最终性和全部冻结配置，不使用“绝对可信”。

## 第4周：混合加密、HPKE、AEAD、版本化Header和KeyStore
- 必读：L33→L34→L35→L36→L37→L38→L39→L40→L41；选读L45、L46。
- 回答：Body CK、HPKE和签名密钥用途；分块nonce如何唯一；RFC定义与应用层格式边界；JCS字节如何签名；软件KeyStore与HSM边界。
- 绘图：加解密数据流、Header字段图、密钥生命周期。
- 公式：AEAD输入、HPKE context、HeaderDigest和previousHeaderDigest。
- 比较表：CP-ABE/PRE/HPKE逐接收者封装。
- 对应：第7章。验收：独立写出加解密伪代码并解释字段安全目的。

## 第5周：撤销、密钥更新、链上链下一致性和故障恢复
- 必读：L42→L43→L44→L14→L50→L51→L52→L54→L55；选读L47—L49、L53。
- 回答：六类撤销的区别；为何不能收回既得材料；UNKNOWN如何恢复；SKIP LOCKED/租约/CAS/幂等/死信分别解决什么；为何不是单一ACID事务。
- 绘图：撤销状态机、Header重建、崩溃点矩阵、Saga补偿图。
- 公式：状态转换前置条件、CAS版本、租约条件。
- 比较表：Plutus/SUE/ABPRE-DR/VersionedHeaderV1。
- 对应：第7—8章。验收：对每个崩溃点说明重复执行安全性和恢复路径。

## 第6周：实验设计、统计方法、相关工作和创新判断
- 必读：L56→L57→L58→L59→L60，并回看L20/L30。
- 回答：请求/运行/机器/workload哪个是推断单位；配对Bootstrap怎样保持层级；怎样报告缓存和C(P)无稳定收益；为何只能写NO_DIRECT_MATCH_FOUND。
- 绘图：实验单位层级、配对设计、效应量CI、创新证据矩阵。
- 公式：配对差值、cluster bootstrap、效应量和CI。
- 比较表：已有—新增—证据—禁止主张。
- 对应：第2、4、6、9章及摘要结论。验收：完成30分钟无稿答辩。
