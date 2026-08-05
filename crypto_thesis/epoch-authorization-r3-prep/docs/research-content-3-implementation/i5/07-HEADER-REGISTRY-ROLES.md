# HeaderRegistry 角色

- ADMIN_ROLE：授予/撤销角色，不能绕过业务约束。
- HEADER_COMMITTER_ROLE：唯一可提交 Header 的角色。
- 只读查询不要求角色。

测试覆盖未授权、管理员绕过、撤销 committer 后拒绝以及重新授权；均 Fail-Closed。
