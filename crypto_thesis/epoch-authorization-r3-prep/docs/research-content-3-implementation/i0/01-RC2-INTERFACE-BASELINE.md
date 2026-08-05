# RC2接口基线

| 项目 | 冻结值 |
|---|---|
| 主仓库当前HEAD | `b39e8a57bf9cf9f688ff5ff09b8b8ae067aa37aa` |
| 审计源码HEAD | `26ef5bc8dc7b09e683aae8c7d7012f779f6847ed` |
| V13代码/预注册HEAD | `8a3d795e22e5d9373c3053245e3b4040cd062dd5` |
| interface manifest SHA | `15e958a87e4e6b77711556f2554100d4b614763170890f96c8d6311ea8349898` |
| chainId | `2026072901` |
| AuthorizationState | `0x9ef44cf538d0df457ba77c556d8785e48bfc436d` |
| Besu/PostgreSQL | `26.5.0` / `16.14` |
| CAP2 | version 2，Ed25519，冻结canonical bytes |
| Gateway | 同块资源/用户读取；GatewayUnavailable；无stale fallback |
| Nonce | PostgreSQL原子消费；数据库故障fail-closed |
| RC3数据库 | 仅独立`r3_control` |

集成必须使用部署artifact ABI；`contracts/interfaces/IAuthorizationState.sol`为`SUPERSEDED_NON_AUTHORITATIVE_STUB`。RC3契约测试必须固定CAP2字段、拒绝顺序、chainId和旧合约地址。
