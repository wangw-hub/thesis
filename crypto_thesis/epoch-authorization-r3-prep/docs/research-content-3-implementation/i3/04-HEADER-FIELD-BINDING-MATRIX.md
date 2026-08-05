# Header Field Binding Matrix

| Field group | Core digest/signature | HPKE info | HPKE AAD | External validation |
|---|---:|---:|---:|---:|
| chainId/contracts/resourceId | yes | yes | yes | yes |
| bodyVersion/policyDigest/epoch/stateVersion | yes | yes | yes | yes |
| headerVersion/keyVersion | yes | yes | yes | yes |
| recipientKeyId/userVersion | envelope in core | yes | yes | recipient lookup |
| bodyReference/bodyDigest | yes | bodyDigest excluded | bodyDigest yes | equality and trusted reference |
| previousHeaderDigest | yes | no | no | yes/version chain |
| recipient ciphertext/enc | yes | n/a | n/a | signature then HPKE |

The CK payload redundantly binds resourceId, bodyVersion, keyVersion, bodyDigest, policyDigest and epoch. This redundancy is checked after authenticated decryption.

