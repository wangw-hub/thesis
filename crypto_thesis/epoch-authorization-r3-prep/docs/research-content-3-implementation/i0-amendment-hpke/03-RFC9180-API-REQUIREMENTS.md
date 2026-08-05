# RFC 9180 API 门槛

主提供者必须以公开 API 支持 Base / X25519 / HKDF-SHA256 / AES-128-GCM、独立 info/AAD、测试专用确定性临时密钥、sender/recipient context 和 exporter，并精确匹配权威向量。生产 `seal_base` 不接受确定性临时密钥；确定性入口仅隔离在测试适配路径。
