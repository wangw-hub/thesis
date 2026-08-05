# Attack and Negative Test Matrix

| Attack/fault | Expected result | Result |
|---|---|---|
| Header field/signature tamper | reject | PASS |
| wrong trusted issuer key/keyId | reject | PASS |
| signature truncate/extend/domain swap | reject | PASS |
| recipient deletion/duplicate/reorder | reject | PASS |
| wrong recipient/private key | reject | PASS |
| wrong info/AAD context | HPKE reject | PASS |
| cross chain/contract/resource/epoch/Header version | reject | PASS |
| Body reference/digest mismatch | reject | PASS |
| Header/Body object corruption | storage reject | PASS |
| previous digest mismatch/rollback | reject | PASS |
| CAP2 signature domain used for Header | reject | PASS |
| external service import/access | absent | PASS |

These are correctness and negative-behavior results, not a cryptographic proof or performance evidence.

