import base64
import hashlib
import os
import secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def _key():
    raw = os.getenv("JOPETS_ENCRYPTION_KEY", "") or os.getenv("DJANGO_SECRET_KEY", "")
    if len(raw) < 32:
        raise RuntimeError("JOPETS_ENCRYPTION_KEY o DJANGO_SECRET_KEY debe tener al menos 32 caracteres")
    return hashlib.sha256(raw.encode("utf-8")).digest()


def encrypt_text(value, aad=b""):
    if value is None:
        raise ValueError("No se puede cifrar None")
    nonce = secrets.token_bytes(12)
    ciphertext = AESGCM(_key()).encrypt(nonce, str(value).encode("utf-8"), aad)
    return base64.urlsafe_b64encode(nonce + ciphertext).decode("ascii")


def decrypt_text(encoded, aad=b""):
    if not encoded:
        raise ValueError("Texto cifrado vacío")
    payload = base64.urlsafe_b64decode(encoded.encode("ascii"))
    if len(payload) <= 12:
        raise ValueError("Texto cifrado inválido")
    return AESGCM(_key()).decrypt(payload[:12], payload[12:], aad).decode("utf-8")
