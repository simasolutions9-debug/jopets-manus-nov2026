# Despliegue de Jopets en Ubuntu

## Requisitos

Ubuntu actualizado, Docker Engine, Docker Compose plugin, un dominio para la API y un volumen privado para PostgreSQL. Traccar, Ollama, ChromaDB, OpenWA, Flutter y el panel web se despliegan por separado y no forman parte del Compose base.

## Configuración

1. Copie `.env.example` a `.env`.
2. Genere `DJANGO_SECRET_KEY`, `AES256_GCM_KEY_B64` e `IP_HASH_SECRET` con un gestor seguro.
3. Configure `DJANGO_ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` y `DATABASE_URL`.
4. Mantenga `PAYMENTS_ALLOW_LIVE=False`, `SIMA_OTP_TEST_MODE=False` y la simulación de pedidos desactivada salvo pruebas controladas.
5. No guarde `.env` en Git ni lo incluya en APK, logs o imágenes públicas.

## Arranque

```bash
docker compose -f infra/docker-compose.yml build
docker compose -f infra/docker-compose.yml up -d db
docker compose -f infra/docker-compose.yml run --rm api python backend/manage.py migrate_tenants
docker compose -f infra/docker-compose.yml up -d api
```

Verifique `GET /api/healthz` antes de habilitar tráfico. La salida debe indicar qué integraciones están en Sandbox o no configuradas. El healthcheck interno envía `X-Forwarded-Proto: https` porque Django mantiene activa la redirección HTTPS en producción.

## HTTPS

Instale Nginx y Certbot en el host. Use `infra/nginx.conf` como base, sustituya el dominio autorizado y emita el certificado con Certbot. PostgreSQL debe permanecer en una red privada y no publicar el puerto 5432.

## Copias de seguridad

Realice respaldos cifrados de PostgreSQL, pruebe restauraciones en un entorno separado y conserve las claves de cifrado fuera de la base de datos. Una copia no probada no se considera recuperable.

```bash
pg_dump --format=custom --file=/secure-backups/jopets-$(date +%F).dump jopets
pg_restore --list /secure-backups/jopets-YYYY-MM-DD.dump
```

## Integraciones externas

No instale ni active pagos reales, Traccar, Ollama, ChromaDB u OpenWA hasta disponer de sus credenciales, red, políticas de acceso, monitoreo y autorización operativa. La aplicación debe mostrar estado pendiente cuando no estén configurados.
