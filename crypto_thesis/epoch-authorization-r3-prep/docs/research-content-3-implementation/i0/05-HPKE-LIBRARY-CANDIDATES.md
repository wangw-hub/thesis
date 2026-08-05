# HPKE库候选

| 候选 | RFC9180/Base/X25519/HKDF-SHA256/AES-128-GCM | 向量/成熟度 | 决定 |
|---|---|---|---|
| pyca cryptography 49.0.0 | 官方API明确支持全部目标项；single-shot `Suite` | 49.0.0新增，项目成熟稳定；I1必须跑RFC A.1 | **SELECTED_CANDIDATE_NOT_INSTALLED** |
| hpke.py | 声明支持全部目标项 | 独立实现、Apache-2.0 | FALLBACK_ONLY |
| PyHPKE | 声明支持官方向量但未正式审计 | 独立实现 | FALLBACK_ONLY |
| rfc9180-py | 支持目标suite，但标为Alpha且带自定义wire helper | 成熟度不足 | REJECTED_FOR_PRIMARY |
| 手拼X25519+HKDF+AEAD | 组件可得但非经验证HPKE API | 容易遗漏label/domain/sequence语义 | PROHIBITED |

选择cryptography 49.0.0，因为它提供RFC 9180原生API、目标suite、`info`上下文和enc长度接口，可与Body/签名组件共享受维护后端。当前46.0.3不能冒充满足条件。

I1硬门：安装物hash和许可证归档；RFC 9180 Appendix A.1 Base向量、错误私钥/info/AAD/enc/ciphertext全部通过。未运行前状态保持`REQUIRES_MINIMAL_PROTOTYPE`。

来源：[cryptography 49 HPKE](https://cryptography.io/en/49.0.0/hazmat/primitives/hpke/)、[RFC 9180](https://www.rfc-editor.org/rfc/rfc9180.html)。
