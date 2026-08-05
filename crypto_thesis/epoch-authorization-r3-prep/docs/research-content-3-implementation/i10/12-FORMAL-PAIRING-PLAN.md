# Formal Pairing Plan

Pairing key: `generatorVersion|semanticClass|inputDigest|seed|configurationDigest`. Shared factors are semantic class, input digest, seed, and environment fingerprint. Varying factors are replica state, fault class, recipient count, and body size. Pairing is only between semantically identical tasks; timing-neighbor pairing is forbidden, and HEADER_ONLY/BODY_ROTATION are never paired as comparable outcomes.
