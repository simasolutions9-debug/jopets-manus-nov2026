# Estado de implementación Jopets

## Implementado en esta primera base

- Monorepo separado en backend, mobile, global-panel, ai-service, infra y docs.
- Modelos base de Tenant, usuario por roles, perfil de cliente, mascota y reserva.
- Configuración JWT/Argon2 declarada y endpoint de health.
- Máquina de estados de Booking con bloqueo de saltos.
- Servicio FastAPI que informa IA no configurada sin simular inferencia.
- Panel React/Vite y portada Flutter con el acceso principal solicitado.
- Docker Compose declara PostgreSQL 16 y API.
- Cifrado autenticado AES-256-GCM para datos sensibles, sin fallback a texto plano.
- Verificación de identidad maestra SIMA y utilidades TOTP preparadas.
- Registro de dueño de mascota sin `tenant_id` ni proveedor obligatorio.
- Endpoint de branding dinámico con validación de URL HTTPS y colores hexadecimales.
- Pruebas unitarias de cifrado y rechazo de saltos de estado.
- Contexto transaccional tenant-aware, middleware de routing y política RLS generable con `USING`/`WITH CHECK`.
- Comandos idempotentes `provision_tenant` y `migrate_tenants`.
- JWT reforzado: cuentas SIMA/Subdueño bloqueadas si no tienen MFA/TOTP válido.
- Núcleo de pagos Sandbox con rutas ambiguas rechazadas, adaptadores y reparto Decimal idempotente.
- Detección de país con precedencia explícita/IP/locale/zona horaria/fallback y huella HMAC de IP.
- QR firmado con propósito, mascota, dueño y tenant, validado en backend.
- Modelos persistentes para transacciones, operaciones idempotentes, asignaciones y webhooks.
- Desafíos de verificación de cinco minutos, hash del token, expiración, reutilización y credencial única QR/código.
- Outbox persistente y comando `process_payment_outbox` para operaciones de autorización, captura y reembolso.
- Marketplace con productos, pedidos, líneas de pedido y máquina de estados protegida.
- Fidelización con regla USD, ledger preparado y conversión de puntos a descuento.
- Referidos con rechazo de autoreferidos, códigos repetidos y créditos indebidos.
- Migraciones iniciales generadas para tenants, cuentas, clientes, pagos y marketplace.
- Endpoints REST protegidos para catálogo, transición de pedidos, vista previa de fidelización y elegibilidad de referidos.
- Endpoints REST para mascotas, QR, reservas, desafío de cinco minutos y transiciones de servicio.
- Campos de proveedor, llegada, verificación y riesgo GPS añadidos a las reservas.
- Cliente HTTP Flutter inicial para branding, mascotas y creación de reservas con `X-Tenant-ID`.
- Cliente Flutter ampliado con generación de QR, solicitud de desafío y transición de reservas.
- Membresías Premium/Elite y beneficios condicionados a pago confirmado.
- Descuentos configurables por categoría y nivel.
- Endpoint de tele-veterinaria en modo demostración explícito.
- Registro de ocho agentes IA en estado `pending_configuration`, sin mutaciones de negocio.
- Modelos de `PriceRule`, `CommissionRegion` y `DetectionLog` para precios publicados versionados y auditoría.
- Servicio de precios que no devuelve importes cuando no existe una regla publicada.
- Endpoint protegido de estado de agentes IA con inferencia `not_configured`.
- Términos de servicio y política de privacidad internacionales redactados para SIMA Solutions Corp.
- Endpoint global SIMA de solo lectura con métricas marcadas como incompletas cuando no hay datos reales.
- Panel global conectado a listado, creación y aprobación/rechazo de distribuidores mediante endpoints protegidos por `admin_global`.
- Chat persistente en tiempo real con Channels, Daphne, Redis, JWT WebSocket, historial y marcado de mensajes leídos.
- Estados explícitos de pagos Sandbox, GPS no conectado, OpenWA no configurado e IA no configurada.
- Rate limit inicial de 100 solicitudes por tenant en 60 segundos en el servicio FastAPI.
- Configuración de seguridad Django para proxy HTTPS, HSTS, cookies seguras, `X-Frame-Options` y `nosniff`.
- Nginx preparado para redirección HTTPS, Certbot y proxy hacia Daphne/ASGI, incluyendo headers de WebSocket.
- Guía VPS con Docker Compose, migraciones, respaldos y recuperación.
- Daphne declarado y usado como servidor ASGI de producción para HTTP y WebSocket.
- Compose sin contraseña PostgreSQL codificada: exige variables de entorno y no publica el puerto 5432.
- API expuesta solo en loopback del host con healthcheck de contenedor.
- Django usa `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST` y `POSTGRES_PORT`.
- Auditoría estructurada para acciones sensibles con actor, tenant, recurso, resultado y metadata.
- Webhook de pagos Sandbox con firma HMAC, timestamp tolerado, rechazo de alteraciones y deduplicación por `event_id`.
- Auditoría conectada a aceptación, duplicación y rechazo de webhooks, además de desafíos y transiciones de reservas.
- Los registros de auditoría excluyen firmas, secretos y payloads completos; conservan solo contexto mínimo operativo.
- Pruebas HTTP añadidas para webhook firmado/idempotente y validación UUID/coincidencia de tenant en clientes.

## Pendiente y bloqueos verificables

- El sandbox no tiene Flutter/Dart ni Docker instalados; no se pudo ejecutar `flutter analyze`, compilación móvil ni `docker compose`.
- Django y PostgreSQL no están instalados/activos en este entorno; no se ejecutaron migraciones ni pruebas RLS reales.
- El enrolamiento TOTP por sesión, políticas RLS ejecutadas en PostgreSQL, worker operativo contra pasarelas, OpenStreetMap, Ollama/ChromaDB y panel conectado requieren implementación posterior y servicios configurados.
- PostgreSQL no está activo en este sandbox; la consistencia de historial de migraciones muestra advertencia de conexión, aunque `makemigrations --check` no detecta cambios pendientes.
- No se ejecutó `flutter analyze` porque Flutter/Dart no están instalados en el entorno actual.
- No se puede reproducir sonido en el dispositivo del usuario desde una pausa del chat; no se activa ninguna alarma remota automáticamente.
- La migración de membresías fue generada, pero su aplicación real requiere PostgreSQL activo.
- La migración de precios fue generada, pero su aplicación real requiere PostgreSQL activo.
- El rate limit actual es local al proceso; para producción debe respaldarse en un almacenamiento compartido como Redis configurado explícitamente.
- No se inició Docker, Nginx, PostgreSQL ni Certbot en este sandbox; la configuración fue validada por contenido y el backend por pruebas estáticas.
- La configuración Compose no se ejecutó porque Docker no está disponible en el sandbox.
- La migración de auditoría fue generada; su aplicación real requiere PostgreSQL activo.
- Las pruebas HTTP usan mocks para no tocar PostgreSQL ni procesar pagos externos en Sandbox.
- Procedimiento documentado para ejecutar pruebas HTTP en VPS/staging real.
- Checklist de liberación con seguridad, lógica de negocio, operación, migraciones y promoción.
- No se activan pagos, mensajería, GPS ni IA reales.

Este documento distingue código inicial de integraciones no verificadas; no declara el producto terminado.
