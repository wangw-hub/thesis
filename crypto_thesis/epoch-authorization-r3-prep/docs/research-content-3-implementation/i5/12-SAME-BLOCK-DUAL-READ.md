# 同块高双合约读取

固定块 834 的读取结果：AuthorizationState epoch/stateVersion=1/1；HeaderRegistry header/body/key=3/2/2。两个调用使用同一 `block_identifier=834`，未混入 latest。

该向量构成外部验证上下文；任一合约失败整体 Fail-Closed。
