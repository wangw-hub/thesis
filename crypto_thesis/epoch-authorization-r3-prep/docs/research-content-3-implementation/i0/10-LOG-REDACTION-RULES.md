# 日志脱敏规则

## 永不记录

用户私钥、CK、ROOT_KEK、CAP2/Header签名私钥、交易私钥、HPKE明文、数据库密码、完整连接字符串、credential内容、AEAD解包结果、测试向量私钥字段。

## 允许记录

keyId、keyVersion、recipientKeyId、Header/Body摘要、operationId、transactionHash、blockNumber/blockHash、resourceId链上摘要、拒绝码、重试次数、非秘密依赖版本。

## 执行规则

- 结构化日志字段allowlist优先，不依赖事后正则；
- 秘密对象禁止`repr`/JSON；异常映射为固定错误码；
- URL只保留scheme/host/port，删除userinfo/query；
- 审计记录保存动作、版本、主体和结果，不保存输入bytes；
- 提交与每阶段门运行秘密模式扫描，候选必须逐项分类；
- `TRUE_SECRET>0`或`UNCLASSIFIED>0`立即停止。
