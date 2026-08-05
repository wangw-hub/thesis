# I4问题跟踪

无开放FATAL、MAJOR或MINOR。

已关闭的实施问题：

- 新集群listen_addresses初值缺少SQL字符串引号：在启动前fail-closed发现，仅修正新集群。
- 密码文件尾换行导致测试角色认证失败：服务器端明确移除CR/LF后重设，仅影响新角色。
- Windows pytest默认临时目录ACL冲突：改用明确隔离的`C:\tmp`测试目录。

这些失败均保留在操作记录中，未影响正式集群或弱化测试门槛。

