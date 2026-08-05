# 创新性与重合风险

> NO_DIRECT_MATCH_FOUND仅表示本次可审计检索未找到完整同构工作，不等于证明不存在。

|问题|判定|解释|
|---|---|---|
|一篇论文同时覆盖三项研究内容|NO_DIRECT_MATCH_FOUND|时态授权、链上访问控制、HPKE/撤销和跨系统恢复分别成熟，但未找到同时覆盖I*、CAP2共享Nonce、版本化HPKE Header和崩溃恢复的正式论文。|
|与I*相同的确定性非连续时间表示|PARTIAL_OVERLAP|周期授权、TRBAC/GTRBAC、区间规范化和唯一授权语义已有；未找到完全相同的I*字节规范与policyDigest组合。|
|与CAP2相同的完整状态绑定|PARTIAL_OVERLAP|Macaroons、DPoP和区块链能力分别覆盖上下文、请求/密钥绑定和链上授权；未找到完全相同字段集合。|
|链状态+共享Nonce+多Verifier|NO_DIRECT_MATCH_FOUND|本次未找到与Besu链状态、共享PostgreSQL单次Nonce和多Verifier一致性完整同构的正式工作。|
|VersionedHeaderV1相同字段与版本链|NO_DIRECT_MATCH_FOUND|TUF、in-toto、内容寻址和加密格式覆盖部分机制，但未找到同字段集合。|
|AuthorizationState+HeaderRegistry双合约|NO_DIRECT_MATCH_FOUND|存在多合约和注册表架构，但未找到同状态语义和事件闭环。|
|HPKE多接收者Header+前瞻撤销|PARTIAL_OVERLAP|HPKE、多接收者封装、lazy revocation和密文更新均已有；你的组合是自然系统整合而非新密码原语。|
|链状态+对象+DB任务+崩溃恢复|PARTIAL_OVERLAP|Saga、幂等、租约、SKIP LOCKED和回执恢复是成熟模式；完整冻结组合未找到。|
|总体创新类型|SYSTEM_INNOVATION / ENGINEERING_INTEGRATION|核心价值在跨层不变量、完整绑定、恢复闭环、真实多节点和诚实负面结果。|

## 高风险主张
1. “首次提出非连续时间访问控制”——已有深厚时态授权研究。
2. “Dyadic覆盖普遍压缩至O(log U)”——理论和真实实验均不足。
3. “字段组合是新密码协议”——应定位系统协议结构。
4. “区块链提供绝对可信状态/时间”——只能在许可链和网络假设下表述。
5. “前瞻撤销可收回旧明文/CK”——错误。
6. “IPFS提供机密性、授权和永久可用性”——错误。
7. “测试通过等同形式化证明”——错误。
8. “逐请求样本量代表独立重复”——存在伪重复。

## 可保留的论文价值
- I*的确定、唯一、可序列化和摘要绑定，以及C(P)边界实证。
- CAP2的链/合约/资源/状态/用户完整绑定与多Verifier原子单次消费。
- AuthorizationState和HeaderRegistry的明确组合不变量。
- 标准HPKE/AEAD/Ed25519/JCS上的版本化Header与前瞻撤销。
- operationId、CAS、租约、SKIP LOCKED、重试/死信和UNKNOWN恢复闭环。
- 真实多节点、运行级配对和无稳定收益的负面结果。
