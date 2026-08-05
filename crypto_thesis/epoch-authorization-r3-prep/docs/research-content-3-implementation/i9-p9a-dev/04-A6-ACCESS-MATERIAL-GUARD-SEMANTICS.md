# A6 材料释放语义

`AUTHORIZATION_AHEAD_OF_HEADER` 必须 Fail-Closed：`materialRelease=DENIED`，`reasonCode=HEADER_UPDATE_PENDING`。旧 Header 不可用于释放材料。其他非 `CONSISTENT` 分类同样不放行；未放宽任何释放条件。
