# 交易 Nonce 并发管理报告

## 方案

优先以组织独立发送账户减少冲突；同组织多客户端由 PostgreSQL `ethereum_nonce_state` 行锁协调。分配值取数据库 `next_nonce` 与 RPC `pending` nonce 的较大值，并保存 reservation_id 和 RESERVED/BROADCAST/CONFIRMED/FAILED 状态。

## 风险

仅调用 `get_transaction_count(...,"pending")` 无法保证并发唯一。预留后未广播会形成 nonce 间隙；回执超时不能直接判定交易失败；进程重启必须从数据库和链上共同恢复。

## 验收状态

表结构和原子预留实现已建立，但广播状态机、间隙恢复以及真实多客户端并发、RPC 重试、交易替换和进程重启尚未完成。因此交易 Nonce 管理未通过正式准入。
