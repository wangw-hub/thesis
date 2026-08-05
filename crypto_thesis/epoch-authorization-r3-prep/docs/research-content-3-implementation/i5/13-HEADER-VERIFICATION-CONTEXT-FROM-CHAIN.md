# 链上 HeaderVerificationContext

policyDigest、epoch、stateVersion 来自 AuthorizationState；bodyVersion、keyVersion、headerVersion 和对象摘要来自 HeaderRegistry。Header 自身字段不得作为预期值。

V1 强制 bodyVersion=keyVersion；旧 Header 在授权 epoch/stateVersion 推进后拒绝。
