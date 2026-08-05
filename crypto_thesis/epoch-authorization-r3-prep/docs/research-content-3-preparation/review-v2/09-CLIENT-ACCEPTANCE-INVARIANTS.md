# 客户端接受不变量

对确认区块`b`，客户端只有在以下条件全部成立时才释放CK或明文：

```
CAP2.signatureValid
∧ CAP2.operation = READ
∧ CAP2.chainBinding.chainId = Header.chainId
∧ CAP2.chainBinding.contractAddress = Header.authorizationContract
∧ AuthorizationState.resource.status = ACTIVE
∧ AuthorizationState.user.status = ACTIVE
∧ CAP2.resourceId/policyDigest/epoch/stateVersion/userKeyId/userVersion
  = state@b
∧ HeaderRegistry.authorizationContract = Header.authorizationContract
∧ HeaderRegistry.anchor@b.status = COMMITTED
∧ HeaderRegistry(resourceId).epoch/stateVersion/policyDigest
  = AuthorizationState(resourceId)@b
∧ Header.headerRegistry/resourceId/epoch/stateVersion/policyDigest/
  headerVersion/keyVersion/previousHeaderDigest/headerDigest
  = committed anchor@b
∧ SHA-256(JCS(unsigned Header)) = anchor.headerDigest
∧ Ed25519Verify(issuerKey, domain || headerDigest, issuerSignature)
∧ recipientEnvelope.recipientKeyId/userVersion = current user@b
∧ HPKEOpen(info, envelope) succeeds
∧ SHA-256(BodyBytes) = Header.bodyDigest
∧ every Body chunk index/AAD/tag succeeds
```

两个合约必须以同一确认区块标识读取；任一RPC、解析、签名、摘要、存储、版本或状态不确定均fail-closed。客户端不得因新Header尚不可用而回退旧Header。`createdAt`不决定授权时间；区块号也不被描述为绝对可信时间。
