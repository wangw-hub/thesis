# 03 算法审计（ALGORITHM AUDIT）

- 算法总数：8（编号 1–8 连续）
- ALGORITHM_LOGIC_ERROR = 0；ALGORITHM_NUMBERING_ERROR = 0；ALGORITHM_INTERFACE_ERROR = 0

| 算法 | 名称 | 本轮动作 | 真实实现依据 |
|---|---|---|---|
| 1 | Normalize | 保持（M7 已修复空 cur 缺陷） | time-policy `normalize.py` |
| 2 | Cover | 完全形式化 | time-policy `cover.py`：pos=0 时 size=2^⌊log2 remaining⌋；pos>0 时 size=pos & −pos 并收缩至 ≤ remaining；U 仅校验端点 |
| 3 | PolicyCompile | 保持（接口已统一） | compiler.py |
| 4 | Issue | 双读语义修正 | `src/epoch_auth/issuer.py`：两次读取均取各自时刻最新确认块，状态不一致则拒绝 |
| 5 | Verify | 保持 | CAP2 验证实现 |
| 6 | HeaderOnlyUpdate | 补充合法接收者集合重建 | I6 证据：revokedRecipientAbsent=true、legalRecipientRetained=true、bodyDigestUnchanged=true；headerVersion+1、body/key 不变 |
| 7 | BodyRotation | 保持 | 新 CK/新 Body/版本全 +1 |
| 8 | RecoveryCoordinator | 输出 RecoveryDisposition | `src/epoch_auth_r3/recovery/models.py` + reconciler.py |

## 本轮关键修正细节

### 算法2 最大对齐块定义（消除“最大 2 的幂”未定义问题）

```
remaining ← r − pos
if pos = 0: size ← 不大于 remaining 的最大 2 的幂
else:       size ← 可整除 pos 的最大 2 的幂（pos & −pos）
            while size > remaining: size ≫= 1
```

`ALGORITHM_2_UNDEFINED_MAXIMUM = 0`；U 仅作端点合法性校验（`ALGORITHM_2_UNUSED_PARAMETER = 0`，因为 U 参与 interval.right ≤ U 与 node.end ≤ U 校验）。

### 算法4 双读语义（与真实 Issuer 一致）

- 第 1 步与第 9 步均为“读取最新确认区块上的资源状态与用户状态”；
- 若两次读取返回的状态（资源/用户状态、epoch、版本）不一致，则拒绝签发；
- 删除“同一确认区块”表述——两次读取分别固定到各自时刻的最新确认块，因此能捕获两次读取之间发生的已确认状态变迁。

### 算法6 接收者集合重建（撤销场景核心动作）

新增步骤：根据当前授权状态确定合法接收者集合（被撤销/暂停用户不再进入新密文头部），复用当前内容密钥与密文主体，对每个合法接收者以 HPKE 重新生成封装记录；headerVersion+1，bodyVersion/keyVersion 不变；登记三个摘要。

### 算法8 恢复判定（不再压扁为“关闭状态”）

输出：一致对象或恢复判定（RecoveryDisposition）。区分：候选缺失（FAIL_CLOSED_MISSING_OBJECT）、摘要/结构不合法（FAIL_CLOSED_CORRUPT_OBJECT）、存在已验证可信备份（自动恢复→CONSISTENT）、无可信备份（IRRECOVERABLE_CONTENT_LOSS）或需人工核对（MANUAL_RECONCILIATION_REQUIRED）。
