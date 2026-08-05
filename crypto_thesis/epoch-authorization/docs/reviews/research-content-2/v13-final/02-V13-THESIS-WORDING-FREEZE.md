# V13 Thesis Wording Freeze

## Allowed core claim

在真实五节点 Besu QBFT 许可联盟链上，实现并验证一种由链上授权状态锚定、与
chainId、合约实例、资源状态、策略摘要和用户密钥版本完整绑定的授权执行机制。
通过 PostgreSQL 原子共享 Nonce、多 Verifier 一致性控制和依赖故障下的
Fail-Closed 策略，实现可审计的重放拒绝、状态竞争控制和跨实例授权隔离。

This wording is supported for the tested implementation and fault model. It is
not a formal proof and does not claim resistance to arbitrary validator
collusion or capability sharing by an already authorized user.

## Allowed performance statements

1. Per-request live-chain reads account for about 98.66%-98.80% of end-to-end
   latency in V13.
2. Chain-state access is the main measured performance cost.
3. Concurrency is the main observed factor for end-to-end latency.
4. Fragmentation increases local match work, while its end-to-end effect is
   masked by chain-read cost.
5. Hotspot workloads increase cache-hit rate but do not stably reduce
   end-to-end latency.
6. B1 and C1 show no stable engineering-significant cache benefit.
7. C(P) shows no performance or protocol advantage unavailable to Baseline-I.
8. C(P) is frozen as an optional derived IR and ablation/falsification object.

## Prohibited wording

- C(P) is significantly superior to I*.
- Caching significantly improves overall authorization efficiency.
- Chain-read cost is negligible.
- Arbitrary fragmented policies have logarithmic complexity.
- Testing proves absolute security or completely eliminates replay.
- QBFT produces absolutely trustworthy state.
- A five-node experiment establishes performance at arbitrary scale.

## Evidence qualification

The first formal run is explicitly invalidated due to protocol deviation. All
chapter performance numbers and figures must use V13 run-level paired analysis.
Negative results are part of the frozen evidence and must not be omitted.
