from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .exceptions import CryptoValidationError, IntegrityError
from .key_material import require_length


def aes256_gcm_encrypt(key: bytes, nonce: bytes, plaintext: bytes, aad: bytes) -> bytes:
    require_length(key, 32, "AES-256 key")
    require_length(nonce, 12, "AES-GCM nonce")
    return AESGCM(key).encrypt(nonce, plaintext, aad)


def aes256_gcm_decrypt(key: bytes, nonce: bytes, ciphertext: bytes, aad: bytes) -> bytes:
    require_length(key, 32, "AES-256 key")
    require_length(nonce, 12, "AES-GCM nonce")
    if len(ciphertext) < 16:
        raise CryptoValidationError("ciphertext is shorter than the GCM tag")
    try:
        return AESGCM(key).decrypt(nonce, ciphertext, aad)
    except Exception as exc:
        raise IntegrityError("AES_GCM_AUTHENTICATION_FAILED") from exc

