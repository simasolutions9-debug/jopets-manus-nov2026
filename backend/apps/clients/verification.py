import base64
import hashlib
import hmac
import json
import secrets
from datetime import timedelta
from django.utils import timezone
from .qr import _secret


def issue_challenge():
    raw = secrets.token_urlsafe(32)
    digest = hashlib.sha256(raw.encode()).hexdigest()
    return raw, digest, timezone.now() + timedelta(minutes=5)


def verify_identity(*, challenge_raw, challenge_hash, expires_at, used_at, qr_payload, pet_id, owner_id, tenant_id, backup_code_valid=False):
    if used_at is not None or timezone.now() >= expires_at:
        raise PermissionError("Desafío expirado o utilizado")
    if not hmac.compare_digest(hashlib.sha256(str(challenge_raw).encode()).hexdigest(), challenge_hash) and not backup_code_valid:
        raise PermissionError("Desafío inválido")
    if backup_code_valid:
        return True
    try:
        decoded = json.loads(base64.urlsafe_b64decode(str(qr_payload).encode()).decode())
        payload = decoded["payload"]
        supplied = decoded["signature"]
        body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise PermissionError("QR inválido") from exc
    expected = hmac.new(_secret(), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, supplied):
        raise PermissionError("Firma QR inválida")
    if int(payload.get("expires_at", 0)) < int(timezone.now().timestamp()):
        raise PermissionError("QR expirado")
    if str(payload.get("pet_id")) != str(pet_id) or str(payload.get("owner_id")) != str(owner_id) or str(payload.get("tenant_id")) != str(tenant_id):
        raise PermissionError("QR no corresponde a la reserva")
    return True
