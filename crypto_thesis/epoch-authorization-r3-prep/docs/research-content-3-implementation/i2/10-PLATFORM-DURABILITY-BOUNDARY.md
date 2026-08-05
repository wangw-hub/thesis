# 平台持久性边界

本次环境为 Windows 11、Python 3.13.11。验证了同文件系统原子可见性、文件 flush/fsync、最终重读和并发正确性。卷文件系统类型的只读查询在当前受限会话中不可用，记为 `UNVERIFIED_ENVIRONMENT_ATTRIBUTE`。

Windows 不提供本实现可移植调用的目录 fsync，因此不宣称与 POSIX 目录 fsync 相同的断电持久性。纯本地测试证明原子可见和检测边界，不证明存储硬件在突然断电后的绝对持久性。
