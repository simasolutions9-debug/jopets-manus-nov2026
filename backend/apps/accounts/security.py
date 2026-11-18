import os
import pyotp
from django.conf import settings
from apps.core.security import decrypt_text


def requires_totp(role):
    return role in {"admin_global", "sub_dueno"}


def verify_totp(secret, code):
    return bool(secret and code and pyotp.TOTP(secret).verify(str(code), valid_window=1))


def validate_sima_identity(email):
    expected = getattr(settings, "SIMA_MASTER_EMAIL", "") or os.getenv("SIMA_MASTER_EMAIL", "")
    if str(email).strip().lower() != expected.strip().lower():
        raise PermissionError("Identidad SIMA no autorizada")
    return True
