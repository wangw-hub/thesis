# CompositeStateReadResultV2

V2 保留固定块、两侧已解码状态和明确 consistencyClass：`CONSISTENT`、`AUTHORIZATION_AHEAD_OF_HEADER`、`HEADER_AHEAD_OF_AUTHORIZATION`、单侧存在、双方缺失、摘要冲突、版本冲突与非法状态。A6 被分类为 `AUTHORIZATION_AHEAD_OF_HEADER`，不再误报缺失。
