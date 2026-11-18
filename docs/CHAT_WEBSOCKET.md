# Chat en tiempo real

El chat usa Django Channels sobre ASGI y Redis. La conexión se autentica con el JWT de acceso enviado en el header `Authorization: Bearer <token>` del handshake WebSocket.

## URL

```text
wss://api.example.com/ws/chat/<tenant_uuid>/<provider_user_id>/
```

En desarrollo local:

```text
ws://localhost:8000/ws/chat/<tenant_uuid>/<provider_user_id>/
```

El `tenant_uuid` debe corresponder al contexto permitido para ambos usuarios. El `provider_user_id` es el `id` numérico del usuario proveedor.

## Flutter

El cliente guarda el JWT en `flutter_secure_storage` y abre el chat con:

```bash
flutter run \
  --dart-define=API_BASE_URL=https://api.example.com \
  --dart-define=JOPETS_TENANT_ID=<tenant_uuid> \
  --dart-define=JOPETS_CHAT_PEER_ID=<provider_user_id>
```

La pantalla no conserva mensajes mock. Al conectar, recibe hasta los últimos 50 mensajes persistidos y luego escucha eventos nuevos. Los mensajes enviados se escriben en `ChatMessage` antes de difundirse al grupo.

## Variables y servicios

```env
REDIS_URL=redis://redis:6379/0
```

`infra/docker-compose.yml` incluye Redis sin publicar su puerto. El API se sirve con Daphne mediante `config.asgi:application`. Nginx conserva los headers `Upgrade` y `Connection` requeridos por WebSocket.

Aplicar migraciones antes de iniciar el API:

```bash
python backend/manage.py migrate
```

El WebSocket rechaza sesiones sin JWT, usuarios inactivos, roles no autorizados, tenants fuera del alcance y proveedores que no pertenezcan al tenant solicitado. Al abrir la conversación, los mensajes recibidos pendientes se marcan como leídos.
