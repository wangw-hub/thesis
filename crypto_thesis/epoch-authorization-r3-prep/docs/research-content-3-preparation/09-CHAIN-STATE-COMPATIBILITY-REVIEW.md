# 链状态兼容审查

现有 `AuthorizationState.ResourceRecord`仅有 owner、policyDigest、epoch、status、policyVersion、stateVersion和updatedAtBlock。它足以让 CAP2绑定授权状态，却不能唯一锚定链下 Header。

推荐新部署 `AuthorizationStateV2`，不修改冻结合约与地址。V2以旧合约为授权事实来源/迁移输入，并新增 `headerVersion/keyVersion/headerDigest/headerReferenceDigest/commitStatus/pendingOperation`。引用本身可留链下，链上仅存固定长度摘要。V2事件必须携带 resourceId、epoch、stateVersion、headerVersion、headerDigest与operationId。

迁移采用显式注册：读取旧记录、验证 owner/policy/epoch/stateVersion，提交初始 Header锚点；CAP2继续验证旧合约语义，R3客户端额外验证V2 Header锚点。不能把V2新地址冒充旧 contractAddress。详见 [提交协议](11-ENCRYPT-AUTHORIZE-REVOKE-UPDATE-DECRYPT.md)和 [开放决策](25-OPEN-DECISIONS.md)。
