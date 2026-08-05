# CAP1 Format

CAP1与NTP1独立版本管理：NTP1编码策略语义，CAP1编码一次授权上下文。
所有整数为无符号大端序，字符串为`uint16长度 || UTF-8`，签名覆盖完整载荷。

| 顺序 | 字段 | 编码 |
|---:|---|---|
| 1 | magic | 4字节`CAP1` |
| 2 | schema | uint8，固定1 |
| 3 | flags | uint8，bit0表示层次扩展 |
| 4 | issuer | uint16长度+UTF-8 |
| 5 | resource_id | uint16长度+UTF-8 |
| 6 | policy_digest | 32字节 |
| 7 | epoch | uint64 |
| 8 | user_key_id | 32字节SHA-256指纹 |
| 9 | operation | uint8 |
| 10 | not_before | uint64 Unix秒 |
| 11 | expires_at | uint64 Unix秒 |
| 12 | nonce | 16字节 |
| 13 | issued_at | uint64 Unix秒 |
| 14 | matched_start | 可选uint64 |
| 15 | matched_size | 可选uint64 |
| 16 | cover_version | 可选32字节 |

解码器拒绝未知版本、未知标志、非法UTF-8、截断输入、尾随字节和再次编码
后不一致的输入。`expires_at`不得超过当前规范允许区间的终点。令牌不包含
AS私钥、用户私钥或系统根秘密。
