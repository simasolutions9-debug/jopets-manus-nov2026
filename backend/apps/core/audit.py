import hashlib
import hmac
import json
import time
from .models import AuditEvent


def record_event(*, action, resource_type, resource_id=None, actor_id=None, tenant_id=None, outcome="success", metadata=None):
    return AuditEvent.objects.create(actor_id=actor_id, tenant_id=tenant_id, action=action, resource_type=resource_type, resource_id=str(resource_id or ""), outcome=outcome, metadata=metadata or {})


def verify_webhook(payload, secret, timestamp, signature, tolerance_seconds=300):
    if not secret or not timestamp or not signature:
        return False
    try:
        timestamp_int = int(timestamp)
    except (TypeError, ValueError):
        return False
    if abs(int(time.time()) - timestamp_int) > tolerance_seconds:
        return False
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    expected = hmac.new(secret.encode("utf-8"), f"{timestamp}.{canonical}".encode("utf-8"), hashlib.sha256).hexdigest()
    supplied = signature.removeprefix("sha256=")
    return hmac.compare_digest(expected, supplied)
