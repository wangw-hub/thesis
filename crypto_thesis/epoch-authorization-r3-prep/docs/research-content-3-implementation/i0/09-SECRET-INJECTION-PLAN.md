# 秘密注入计划

## Ubuntu

优先候选：systemd Credentials。I1前必须以只读命令核验每台目标机systemd版本、`systemd-creds`和`LoadCredentialEncrypted`支持。服务只读取systemd提供的运行时凭据路径，不把值复制到环境变量。

后备：`/etc/epoch-auth-r3/credentials/`下仓库外文件，专用服务账户所有，目录0700、秘密文件0400/0600；unit只传文件路径，路径本身不含秘密。

## Windows开发

可使用用户范围DPAPI或仓库外严格ACL文件；仅用于开发适配，不作为五VM统一安全主张。

## 禁止通道

- 命令行参数、环境变量、`.env`、Git、数据库明文字段；
- systemd unit内联`Environment=`秘密；
- 日志、异常、core dump说明、测试快照；
- RPC长期解锁账户。

启动时缺失、权限过宽、未知key version或读取失败均拒绝启动。轮换通过新版本文件/credential和原子元数据切换，不原地覆盖且不静默回退。
