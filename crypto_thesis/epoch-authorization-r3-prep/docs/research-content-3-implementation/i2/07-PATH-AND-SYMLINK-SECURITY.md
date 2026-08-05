# 路径与符号链接安全

namespace 只允许 1–64 个字母、数字、点、下划线和连字符，且拒绝点路径、斜杠、反斜杠、盘符、URI 分隔符、NUL 与控制字符。digest 仅接受 64 位小写十六进制。

每个目录分量以 lstat 检查，最终对象拒绝符号链接、目录和非常规文件；候选路径经 commonpath 根边界校验。Windows reparse point 与高权限攻击者制造的 TOCTOU 无法由纯 Python 文件 API 完全消除，记录为 `ACCEPTED_PLATFORM_LIMITATION`，不宣称抵抗 root/管理员或磁盘控制者。
