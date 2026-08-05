# AtomicWriteProtocolV1

协议顺序：验证输入与 expected digest；在根内 `tmp` 创建独占随机临时文件；完成写入、flush、文件 fsync；重读验证长度与 SHA-256；使用同文件系统硬链接原子创建最终名称（不覆盖）；移除临时名；POSIX 可用时 fsync 父目录；最终重读验证后返回。

若目标竞争产生 `FileExistsError`，验证胜出对象后幂等返回。调用方在 F1–F5 失败时看不到正式对象；F6/F7 失败可能留下完整正式对象但不会错误返回成功，重试幂等。
