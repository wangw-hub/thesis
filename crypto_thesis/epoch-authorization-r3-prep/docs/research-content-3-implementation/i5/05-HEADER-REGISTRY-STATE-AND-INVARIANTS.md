# HeaderRegistry 状态与不变量

- INITIAL：1/1/1，previous=0。
- HEADER_ONLY：header+1，body/key/Body 摘要不变。
- BODY_ROTATION：header/body/key+1，Body 摘要改变。
- operationId 一次性；历史锚点只写一次。
- policyDigest、epoch、stateVersion 必须等于 AuthorizationState 当前值。
- 非 HEADER_COMMITTER、撤销角色、管理员绕过、版本跳跃、错误 previous、零摘要均拒绝。

链上不变量违反数：0。
