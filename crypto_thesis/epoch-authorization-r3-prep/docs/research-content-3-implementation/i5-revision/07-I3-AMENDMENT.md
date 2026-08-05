# I3 增量修订

修订标识：`I3_AMENDMENT_KEY_VERSION_AUTHORITY`。

- HeaderCoreV1 强制 `keyVersion == bodyVersion`。
- INITIAL 强制 header/body/key 均为 1。
- HeaderVerificationContextV1 新增外部 `expected_body_version`；body/key 预期值均来自 HeaderRegistry。
- policyDigest、epoch、stateVersion 继续来自 AuthorizationState。
- 版本链显式区分 INITIAL、HEADER_ONLY、BODY_ROTATION。
- CKEnvelopePayloadV1 继续绑定 resourceId、bodyVersion、keyVersion。

原 48 项测试未删除；新增 6 项修订测试，I3 合计 54/54。
