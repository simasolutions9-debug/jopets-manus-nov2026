# Auditoría de interconexiones de Jopets

Fecha: 2026-11-01

## Mapa lógico

```text
Flutter
  ├─ HTTP/JWT ───────────────> Django REST API ──> PostgreSQL
  ├─ X-Tenant-ID ────────────> aislamiento por tenant y permisos
  ├─ WebSocket + JWT header ─> ASGI/Daphne ─> Channels/Redis ─> ChatMessage/PostgreSQL
  └─ SharedPreferences/SecureStorage ─> onboarding y sesión

Panel Next.js
  └─ /backend-api rewrite ──> Django /api ─> JWT admin_global

Nginx
  ├─ HTTPS/headers proxy ───> Daphne
  └─ Upgrade/Connection ────> WebSocket

AI FastAPI (opcional)
  └─ estado independiente; se anuncia como no configurado hasta disponer de Ollama/ChromaDB
```

## Contratos verificados

- Login Flutter y panel usan `/api/auth/token`; el serializer devuelve `access`, `refresh`, `role`, `user_id` y `tenant_id`.
- Registro usa `/api/auth/register` y exige contraseña de al menos 12 caracteres.
- Marketplace consume `/api/marketplace/products` con JWT y `X-Tenant-ID`.
- Reservas consumen `/api/client/pets`, `/api/client/bookings`, QR y transiciones de verificación.
- Chat usa `/ws/chat/<tenant_uuid>/<peer_id>/`, autentica por `Authorization: Bearer` y persiste `ChatMessage`.
- Panel global consume overview, auditoría y gestión de tenants con el rol `admin_global`.
- Nginx conserva `Upgrade`, `Connection` y `X-Forwarded-Proto`.

## Correcciones aplicadas en esta auditoría

1. El healthcheck de Compose ahora envía `X-Forwarded-Proto: https`, por lo que no queda atrapado por `SECURE_SSL_REDIRECT` en producción.
2. El panel global dejó de mostrar la gestión de tenants como pendiente: ahora lista, crea distribuidores en estado pendiente y permite aprobar/rechazar.
3. Django expone:
   - `GET/POST /api/global/tenants`
   - `POST /api/global/tenants/<uuid>/status`
4. Se alineó la documentación de despliegue con `POSTGRES_*` y `REDIS_URL`.

## Límites intencionales

- Stripe/pagos reales no están activos; el webhook solo valida y registra eventos idempotentes mientras el producto permanece en Sandbox.
- GPS, OpenWA, Ollama, ChromaDB e inferencia IA se anuncian como `not_configured` hasta que existan credenciales, red y autorización.
- El propietario recién registrado no recibe tenant automáticamente; debe ser asignado/provisionado antes de consultar recursos tenant-scoped.
- La aplicación depende de PostgreSQL y Redis en ejecución para validar completamente el runtime; el Sandbox solo permite comprobaciones estáticas.

## Verificación recomendada en VPS

```bash
docker compose -f infra/docker-compose.yml up -d --build
python backend/manage.py migrate
curl -fsS https://api.example.com/api/healthz
```

Después de iniciar sesión como `admin_global`, validar el flujo: listar tenants, crear uno, aprobarlo, asignar usuarios y consultar catálogo/reservas. Para el chat, abrir dos sesiones con usuarios del mismo tenant y verificar recepción, persistencia e indicador de lectura.
