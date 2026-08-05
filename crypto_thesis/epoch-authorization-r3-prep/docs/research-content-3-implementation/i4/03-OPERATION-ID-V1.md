# OperationIdV1

OperationIdV1为SHA-256，输入是域长度前缀、固定大端整数、20字节合约地址和32字节
事件/资源字段。域为`EPOCH_AUTH_R3_HEADER_UPDATE_OPERATION_V1`。blockHash和
headerVersion只作观察证据，不进入逻辑操作身份。测试确认确定性、字段敏感性和
固定长度；没有字符串拼接、JSON或Python repr。

