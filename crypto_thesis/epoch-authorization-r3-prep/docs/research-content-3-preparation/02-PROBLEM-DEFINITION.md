# 问题定义

R3研究“授权状态变化时，如何只更新小型访问控制材料而保持大密文 Body 不变”，并将链上授权状态、链下版本化 Header、持久任务与恢复流程闭合。

单位资源包含一个不可变 Body 版本和一条单调 Header 版本链。Body 由随机 CK/DEK 分块 AEAD 加密；Header绑定 Body、策略、链、合约、epoch和版本，并携带面向当前接收者的封装材料。撤销推进授权状态并停止向撤销用户生成未来访问材料，不追回其既得秘密。

核心可证伪主张是：单个 Header 更新的字节和计算成本基本不随 Body 字节数变化；若影响 `F` 个资源，总成本至少随 `F` 增长。参见 [研究问题](03-RESEARCH-QUESTIONS.md)、[安全边界](04-SECURITY-AND-REVOCATION-BOUNDARY.md)与[实验矩阵](19-EXPERIMENT-MATRIX.md)。
