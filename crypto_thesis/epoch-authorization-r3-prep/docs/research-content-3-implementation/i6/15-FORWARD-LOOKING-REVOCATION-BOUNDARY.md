# Forward-looking Revocation Boundary

The mechanism is `FORWARD_LOOKING_REVOCATION_ONLY`. It prevents a revoked user from receiving new envelopes and makes an old CK unusable for the new Body. It cannot recover old CK, old plaintext, or downloaded old ciphertext; the test confirms the old CK still opens the old Body.
