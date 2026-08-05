# Formal Provisioning

最小独立 Formal 环境（F1/F2/F4；F3 未部署，RC3_MULTI_NODE_FORMAL_REQUIRED=false）：

- Formal Besu 链：chainId `2026080201`，单节点 QBFT（Besu 26.5.0 二进制复用），RPC `127.0.0.1:18546`，P2P `127.0.0.1:31306`，data 目录 `/var/lib/epoch-auth-r3/formal/besu`，systemd 单元 `epoch-auth-r3-formal-besu.service`（独立 genesis/keys/端口）。
- 合约（独立部署）：AuthorizationState `0x0aa91922c979b5E188FF77c506cF48ebb8c80938`；HeaderRegistryV1 `0xb2D1136a8B27aFcFAf3b405cF5598D3Be26c6b6e`。
- Formal PostgreSQL：独立集群 `16/formal_r3`，`127.0.0.1:55433`，数据库/角色 `epoch_auth_r3_formal`，schema `r3_formal`（迁移 `migrations/r3_formal/0001_formal_schema.sql`）。
- Formal Kubo：IPFS_PATH `/var/lib/epoch-auth-r3/formal/kubo/repo`，API `127.0.0.1:15998`，`--routing=none`，bootstrap/peers=0，systemd 单元 `epoch-auth-r3-formal-kubo.service`。
- 运行时秘密：`/var/lib/epoch-auth-r3/formal/runtime-secrets/`（0700/0600，非 Git）。
- 身份/状态/raw：全部独立 Formal 命名空间，Pilot/RC2 复用=0。
