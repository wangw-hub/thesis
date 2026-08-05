# 阶段1 Besu安装自动化报告

## 执行结论

阶段1通过。五台冻结拓扑主机均安装 Hyperledger Besu 26.5.0，安装包哈希、软件版本、Java版本、目录布局、属主和权限符合验收要求。未创建Genesis、节点密钥、systemd服务或链数据，未启动Besu进程，未修改防火墙或开放RPC。

## 执行环境与版本

| 项目 | 值 |
|---|---|
| 执行时间（UTC） | 2026-07-28T10:19:44Z 至 2026-07-28T10:20:32Z |
| 本地Git提交 | `015973261556b614c47adc17a57b266ed6933920` |
| 工作区 | dirty，阶段材料尚未提交 |
| Besu版本 | `besu/v26.5.0/linux-x86_64/openjdk-java-21` |
| Java版本 | OpenJDK 21.0.11 |
| 控制脚本 | `scripts/powershell/01-install-besu.ps1` |
| 远程脚本 | `scripts/remote/install-besu-26.5.0.sh` |

## 安装包来源与完整性

官方发布页为 `https://github.com/besu-eth/besu/releases/tag/26.5.0`，原始下载URL为 `https://github.com/besu-eth/besu/releases/download/26.5.0/besu-26.5.0.zip`。

| 属性 | 值 |
|---|---|
| 文件名 | `besu-26.5.0.zip` |
| 文件大小 | 200,010,413字节 |
| 官方发布页SHA-256 | `9ddbe9e94662459898ff7b3ff4439821eeeee3bc2ff961378604202fa7da09e6` |
| Windows控制端SHA-256 | `9ddbe9e94662459898ff7b3ff4439821eeeee3bc2ff961378604202fa7da09e6` |
| 五台远端SHA-256 | 全部与官方值及控制端值一致 |

本次复用了控制端此前从该官方发布来源获得且已通过官方校验值核验的单一ZIP副本，没有让五台主机分别下载。元数据见 `evidence/installation/download-metadata.json`，逐机哈希见 `evidence/installation/hash-verification.json`。

## 五台主机远程变更

以下变更在五台主机上一致执行：

- 创建系统用户和组 `besu`，登录Shell为 `/usr/sbin/nologin`；
- 安装软件至 `/opt/besu-26.5.0`；
- 创建符号链接 `/opt/besu -> /opt/besu-26.5.0`；
- 创建 `/etc/besu`、`/var/lib/besu`、`/var/log/besu`；
- 完成哈希核验后删除远端临时文件 `/tmp/besu-26.5.0.zip`。

未生成配置、Genesis或私钥；未创建或启动systemd服务；未运行常驻Besu进程。

## 验收结果

| 主机 | 退出码 | Besu | Java | 远端包哈希 | 进程/服务 |
|---|---:|---|---|---|---|
| besu-validator-1 | 0 | 26.5.0 | 21.0.11 | 一致 | 无/无 |
| besu-validator-2 | 0 | 26.5.0 | 21.0.11 | 一致 | 无/无 |
| besu-validator-3 | 0 | 26.5.0 | 21.0.11 | 一致 | 无/无 |
| besu-validator-4 | 0 | 26.5.0 | 21.0.11 | 一致 | 无/无 |
| experiment-client | 0 | 26.5.0 | 21.0.11 | 一致 | 无/无 |

五台目录权限一致：

```text
755 root:root /opt/besu-26.5.0
750 root:besu /etc/besu
750 besu:besu /var/lib/besu
750 besu:besu /var/log/besu
```

验收命令包括：

```bash
java -version
/opt/besu/bin/besu --version
readlink -f /opt/besu
id besu
stat -c '%a %U:%G %n' /opt/besu-26.5.0 /etc/besu /var/lib/besu /var/log/besu
pgrep -af '[b]esu' || true
systemctl list-unit-files --type=service --no-legend --no-pager | awk '$1 ~ /^besu/'
```

## 原始证据

| 主机 | 证据文件SHA-256 |
|---|---|
| besu-validator-1 | `57b75c15be9b1bde3c60b69840bbbf69aceb723382f45c38ccb6d9f7971cd5fc` |
| besu-validator-2 | `7d444be4370ba32136604ec30869b84677c94fa893f7961d10016f90eb1bdd04` |
| besu-validator-3 | `0631795527b74b997b9305a3e957e561633596079a14e21323621ab2f0927200` |
| besu-validator-4 | `99eea7ce46477f9c260f839043805faef60ded94fec47561c2855a0089b24a4e` |
| experiment-client | `4876d1e8eb5e1ad8c97bf6a9712fbd4cf9c64044aaa2bff433e89657a7322e42` |

逐机原始标准输出和标准错误位于 `evidence/installation/<hostname>.txt`。

## 问题、限制与后续准入

阶段1没有安装失败或验收偏差。工作区仍为dirty，且Git状态检查因当前Windows用户无法读取全局Git ignore文件而输出警告；该警告不影响仓库状态或远程安装。

阶段1已达到阶段2的基础软件准入条件。阶段2尚未开始；在获得明确授权前，不生成QBFT Genesis或Validator密钥。

