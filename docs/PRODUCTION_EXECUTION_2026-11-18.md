# Ejecución técnica de salida a producción

Fecha: 2026-11-18

## Trabajo ejecutado en este entorno

Se restauraron los componentes backend que impedían el arranque real de Django: `manage.py`, entrada WSGI, seguridad criptográfica AES-GCM, auditoría persistente, verificación HMAC de webhooks, seguridad TOTP, QR firmado, verificación de identidad, servicios del marketplace y los endpoints explícitos de membresías/tele-veterinaria no configurados.

También se creó el paquete de `apps.memberships`, se añadieron los paquetes Python faltantes y se restauró la cadena de migraciones iniciales de core, clientes, pagos, marketplace y pricing. Se generaron las migraciones derivadas detectadas por Django y se corrigió el tipo de `AuditEvent.actor_id` para que sea compatible con la clave primaria entera del usuario Django.

En Flutter se eliminaron referencias a imágenes que no existen en el checkout restaurado. El arranque y login usan ahora componentes nativos de Flutter, sin depender de un AssetBundle inexistente y sin introducir datos de negocio falsos.

## Validaciones ejecutadas

- `python -m compileall backend ai-service`: correcto.
- `python backend/manage.py check`: correcto, 0 problemas.
- `python backend/manage.py check --deploy`: correcto, 0 advertencias.
- `python backend/manage.py makemigrations --check --dry-run`: `No changes detected`.
- Importación de `config.urls` y `config.asgi`: correcta.
- Búsqueda de `mock`, `dummy`, `fake`, `demo`, `simulat` y `próximamente` en código de aplicación: sin coincidencias.

## Validaciones todavía imposibles en este entorno

- PostgreSQL no está ejecutándose en el Sandbox; no se ejecutaron migraciones reales ni pruebas RLS.
- Redis no está ejecutándose; no se probó Channels/WebSocket en runtime.
- Docker no está instalado; no se ejecutó Compose ni el contenedor de producción.
- Flutter/Dart/Android SDK no están instalados; no se ejecutó `flutter analyze` ni se generó APK/AAB en esta sesión.
- No hay credenciales GitHub disponibles y el checkout restaurado no contiene `.git`; no se pudo hacer push.
- No se configuraron credenciales de pasarela ni webhooks externos.

## Checklist que requiere trabajo externo

- [ ] Recuperar o habilitar el repositorio Git y subir el estado actual a GitHub.
- [ ] Crear el VPS y configurar Docker, PostgreSQL, Redis, Nginx, HTTPS y Certbot.
- [ ] Crear el `.env` de producción fuera de Git.
- [ ] Ejecutar `docker compose -f infra/docker-compose.yml up -d --build`.
- [ ] Ejecutar `python manage.py migrate` contra PostgreSQL real.
- [ ] Instalar y verificar las políticas RLS en PostgreSQL.
- [ ] Probar aislamiento entre dos tenants reales.
- [ ] Probar WebSocket con Redis y dos usuarios reales.
- [ ] Elegir una pasarela de pagos y configurar sus credenciales de staging.
- [ ] Probar firma, idempotencia y transición de reservas mediante webhook.
- [ ] Instalar Flutter/Android SDK en el entorno de compilación o usar CI/CD.
- [ ] Crear keystore Android de producción y conservarlo en un almacén seguro.
- [ ] Ejecutar `flutter analyze`, pruebas en dispositivo y generar el AAB firmado.
- [ ] Configurar el dominio real de la API en `API_BASE_URL`.
- [ ] Ejecutar piloto controlado antes de activar producción.

## Estado honesto

El backend ya pasa sus verificaciones estructurales y de configuración en este Sandbox, pero la aplicación todavía no debe declararse lista para producción hasta ejecutar las validaciones externas indicadas arriba contra PostgreSQL, Redis, HTTPS, un dispositivo Android y una pasarela de pagos de staging.
