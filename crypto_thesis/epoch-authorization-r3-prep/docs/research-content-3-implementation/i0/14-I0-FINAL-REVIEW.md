# I0严格审稿

## 七视角

1. **密码工程**：cryptography 49.0.0是具备原生RFC9180 API的合理候选；当前46.0.3不足。MAJOR：I1向量未运行。
2. **依赖供应链**：版本和许可证可定位，但候选wheel尚未下载，无法冻结平台wheel SHA。MAJOR：I1安装前完成hash锁定。
3. **Linux服务安全**：Ubuntu版本有冻结证据，但systemd精确版本因SSH无凭据未核验。MAJOR：I1前核验或正式采用权限文件后备。
4. **软件工程**：模块、schema和秘密目录分离闭合；不得提前创建实现。MINOR：未来包边界需契约测试。
5. **可复现性**：候选清单、来源和状态明确。MINOR：Windows产品名与OSVersion不一致时保留原始证据，不美化。
6. **学位论文盲审**：软件KeyStore限制表述准确，不声称生产/HSM安全。MINOR 2：需在论文集中说明联合泄露和不可追回边界。
7. **反方审稿**：依赖升级、KeyStore可用性单点和自定义格式仍可能失败。MINOR 2、EDITORIAL 3；均已有I1/I3/I7证伪门。

## 汇总

- FATAL：0
- MAJOR：3
- MINOR：6
- EDITORIAL：3

所有MAJOR有明确关闭门：RFC向量与负向测试、wheel hash/LICENSE归档、systemd或后备注入方式确认。没有MAJOR被伪装成已验证结果。

裁决：`I0_COMPLETED_AWAITING_I1_APPROVAL`。I1未启动。
