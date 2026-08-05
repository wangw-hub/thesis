# CK Envelope Payload V1

The encrypted payload contains exactly: payloadVersion, 32-byte CK, resourceId, bodyVersion, keyVersion, bodyDigest, policyDigest and epoch.

It is strict JCS, rejects unknown/missing/duplicate fields and invalid base64url, and is never a public Header field. Only an authorized client receiving an externally validated Header may open it. Payload context is rechecked before returning the CK.

