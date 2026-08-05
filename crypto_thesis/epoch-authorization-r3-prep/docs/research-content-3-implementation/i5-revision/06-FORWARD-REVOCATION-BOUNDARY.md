# 前瞻性撤销边界

授权撤销首先由 AuthorizationState 的 epoch/stateVersion 推进生效；Issuer 随即停止签发旧上下文材料，旧 Header 在新外部状态下 Fail-Closed。

`HEADER_ONLY` 仅阻止尚未取得 CK 的撤销用户从新 Header 获得 Envelope。`BODY_ROTATION` 以新 CK 加密新 Body，使旧 CK 无法解密新版本。

系统不能追回已获得的旧 CK、旧明文、旧密文或用户自行保存的数据。正式表述冻结为 `FORWARD_LOOKING_REVOCATION_ONLY`，不主张追溯撤销。
