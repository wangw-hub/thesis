# 文献地图

|研究内容|子问题|应掌握理论|代表方向|建议关键词|核心数量|优先级|论文对应|
|---|---|---|---|---|---:|---|---|
|研究内容一|非连续/周期时间语义|半开区间、区间关系、周期表达式|Temporal authorization, TRBAC/GTRBAC|temporal authorization; periodic constraints; multiple intervals|8|最高|第2—4章|
|研究内容一|规范化、唯一表示与编译|区间并集规范化、语义等价、规范形式|Canonical policy representation|interval normalization; canonical form; deterministic serialization|跨领域组合|最高|第3章I*与policyDigest|
|研究内容一|Dyadic覆盖与执行IR|二次幂区间分解、输出敏感复杂度|Range decomposition|dyadic interval; canonical cover; segment tree|算法资料补充|中|第3/4章C(P)消融|
|研究内容二|能力和上下文绑定|Bearer capability、caveat、PoP、域分离|Macaroons, DPoP, blockchain CAC|context-bound capability; replay; audience|6|最高|第5章CAP2|
|研究内容二|Nonce与多Verifier|原子唯一约束、幂等、重复抑制|Distributed replay prevention|atomic nonce; idempotency; multi-verifier|4|最高|第5章共享Nonce|
|研究内容二|许可链与BFT|PBFT、IBFT/QBFT、安全/活性、最终性|Permissioned blockchain consensus|PBFT; IBFT 2.0; QBFT|6|最高|第5章部署和故障模型|
|研究内容二|链上授权系统|ABAC/CAC、智能合约、审计与撤销|Blockchain access control|permissioned blockchain authorization|10|最高|第2/5章竞争工作|
|研究内容二|性能评估|端到端分解、链读、缓存、并发|Private-chain benchmark|BLOCKBENCH; paired benchmark|2+统计|高|第6章|
|研究内容三|混合加密和AEAD|KEM-DEM、CK/DEK、nonce、AAD|Hybrid/envelope encryption|KEM DEM; content key; chunked AEAD|5|最高|第7章|
|研究内容三|HPKE与接收者封装|RFC9180、X25519、HKDF、形式分析|HPKE standard and analysis|HPKE; AAD; context; interoperability|7|最高|第7章RecipientEnvelope|
|研究内容三|版本化Header|JCS、Ed25519、哈希链、回滚|Signed/versioned metadata|canonical JSON; rollback protection|4|最高|第7章VersionedHeaderV1|
|研究内容三|撤销与密钥更新|前瞻/追溯、用户/属性/密钥/密文撤销|Lazy revocation, PRE, SUE|forward revocation; key update|5|最高|第7/8章|
|研究内容三|内容寻址/IPFS|Merkle DAG、不可变对象、可用性边界|Content-addressed storage|CID; immutable object; IPFS availability|3|高|第7章与后续工作|
|研究内容三|链上链下一致性|Saga、UNKNOWN、幂等、租约、CAS|Cross-system transaction recovery|saga; unknown outcome; lease; CAS|6|最高|第8章|
|全部|实验统计|伪重复、运行级配对、层级Bootstrap|Rigorous systems evaluation|paired bootstrap; pseudoreplication|5|最高|第6/9章|
