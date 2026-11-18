import os
import time
from collections import defaultdict, deque
from fastapi import FastAPI, Header, HTTPException

app = FastAPI(title="Jopets AI Service", version="0.1.0")
_windows = defaultdict(deque)


def _allow(tenant: str) -> bool:
    now = time.monotonic()
    window = _windows[tenant]
    while window and now - window[0] >= 60:
        window.popleft()
    if len(window) >= 100:
        return False
    window.append(now)
    return True


@app.get("/health")
def health():
    configured = bool(os.getenv("OLLAMA_BASE_URL") and os.getenv("CHROMA_URL"))
    return {"status": "ok", "inference": "available" if configured else "not_configured", "message": None if configured else "Configura Ollama y ChromaDB para activar IA real"}


@app.get("/agents/status")
def agent_status(x_tenant_id: str = Header(default="")):
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-ID es obligatorio")
    if not _allow(x_tenant_id):
        raise HTTPException(status_code=429, detail="Límite de 100 solicitudes por tenant en 60 segundos")
    return {"tenant_id": x_tenant_id, "inference": "not_configured", "mutations_enabled": False}
