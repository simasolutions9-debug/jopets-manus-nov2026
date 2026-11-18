import base64
import hashlib
import hmac
import json
import os
import time


def _secret():
    value = os.getenv("JOPETS_QR_SECRET", "") or os.getenv("DJANGO_SECRET_KEY", "")
    if len(value) < 32:
        raise RuntimeError("JOPETS_QR_SECRET o DJANGO_SECRET_KEY debe tener al menos 32 caracteres")
    return value.encode("utf-8")


def issue_pet_qr(pet_id, owner_id, tenant_id, ttl_seconds=900):
    payload = {"pet_id": str(pet_id), "owner_id": str(owner_id), "tenant_id": str(tenant_id), "expires_at": int(time.time()) + ttl_seconds}
    body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    signature = hmac.new(_secret(), body, hashlib.sha256).hexdigest()
    return base64.urlsafe_b64encode(json.dumps({"payload": payload, "signature": signature}, separators=(",", ":")).encode()).decode()
