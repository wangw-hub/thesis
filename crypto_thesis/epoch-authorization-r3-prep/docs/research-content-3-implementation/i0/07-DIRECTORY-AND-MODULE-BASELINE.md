# 目录与模块基线

## 未来代码目录（本轮不创建）

```text
src/epoch_auth_r3/
  crypto/
  header/
  storage/
  database/
  blockchain/
  revocation/
  recovery/
  audit/
```

- `crypto`只包装标准库API和格式，不实现原语；
- `header`负责Schema/JCS/签名域；
- `storage`先LocalObjectStore，后IPFS；
- `database`只访问`r3_control`；
- `blockchain`组合冻结AuthorizationState和新HeaderRegistry；
- `revocation/recovery`维护幂等任务与对账；
- `audit`只接受非秘密结构化字段。

## 秘密目录候选（本轮不创建）

- Windows：`D:\Research\crypto_thesis\secrets\research-content-3\`
- Ubuntu：`/etc/epoch-auth-r3/credentials/`

这些路径必须位于Git工作树之外。未来权限：专用服务账户、目录最小遍历权、文件仅所有者可读；不得把真实路径内容、目录清单或备份位置写入仓库。
