# R5-B 最终秘密扫描报告

扫描覆盖工作树、Git 索引、全部可达历史、引用、暂存区、差异和活动对象库。候选值只记录路径、分类理由及文件 SHA-256，不记录秘密正文。

- 可提交表面 `TRUE_SECRET`：0
- Git 索引 `TRUE_SECRET`：0
- 可达历史 `TRUE_SECRET`：0
- 活动对象库 `TRUE_SECRET`：0
- `UNCLASSIFIED`：0
- 旧不安全 `prepare.ps1` 可达历史条目：0
- 安全版 `prepare.ps1` PowerShell 语法错误：0
- 安全版硬编码 32 字节密钥：0

当前链必需秘密单独分类为 `CURRENT_REQUIRED_SECRET`，均位于被忽略私密目录，不属于可提交表面。
