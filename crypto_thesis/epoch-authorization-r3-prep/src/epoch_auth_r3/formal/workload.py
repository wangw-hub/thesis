from __future__ import annotations

import hashlib
import hmac


class FormalWorkloadGeneratorV1:
    DOMAIN = b"EPOCH_AUTH_R3_FORMAL_WORKLOAD_V1"

    @classmethod
    def generate(cls, seed: int, size: int) -> bytes:
        if type(seed) is not int or seed < 0 or type(size) is not int or size < 0:
            raise ValueError("INVALID_WORKLOAD_PARAMETERS")
        out = bytearray()
        counter = 0
        key = seed.to_bytes(32, "big")
        while len(out) < size:
            out.extend(
                hmac.new(key, cls.DOMAIN + counter.to_bytes(8, "big"), hashlib.sha256).digest()
            )
            counter += 1
        return bytes(out[:size])

    @classmethod
    def manifest(cls, seed: int, size: int) -> dict:
        value = cls.generate(seed, size)
        return {"domain": cls.DOMAIN.decode(), "seed": seed, "sizeBytes": size,
                "plaintextSha256": hashlib.sha256(value).hexdigest()}
