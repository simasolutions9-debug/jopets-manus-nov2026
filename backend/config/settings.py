import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
BASE_DIR=Path(__file__).resolve().parent.parent
DEBUG=os.getenv("DJANGO_DEBUG", "False").lower()=="true"
SECRET_KEY=os.getenv("DJANGO_SECRET_KEY", "")
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY="unsafe-dev-only"
    else:
        raise ImproperlyConfigured("DJANGO_SECRET_KEY es obligatorio cuando DJANGO_DEBUG=false")
ALLOWED_HOSTS=[x for x in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if x]
INSTALLED_APPS=["daphne","django.contrib.auth","django.contrib.contenttypes","django.contrib.sessions","django.contrib.messages","django.contrib.staticfiles","channels","rest_framework","apps.core","apps.tenants","apps.accounts","apps.clients","apps.payments","apps.marketplace","apps.memberships","apps.pricing"]
MIDDLEWARE=["django.middleware.security.SecurityMiddleware","django.contrib.sessions.middleware.SessionMiddleware","django.middleware.common.CommonMiddleware","django.middleware.csrf.CsrfViewMiddleware","django.contrib.auth.middleware.AuthenticationMiddleware","apps.tenants.middleware.TenantRoutingMiddleware","django.contrib.messages.middleware.MessageMiddleware","django.middleware.clickjacking.XFrameOptionsMiddleware"]
ROOT_URLCONF="config.urls"
TEMPLATES=[{"BACKEND":"django.template.backends.django.DjangoTemplates","DIRS":[],"APP_DIRS":True,"OPTIONS":{"context_processors":["django.template.context_processors.request","django.contrib.auth.context_processors.auth","django.contrib.messages.context_processors.messages"]}}]
WSGI_APPLICATION="config.wsgi.application"
ASGI_APPLICATION="config.asgi.application"
DATABASES={"default":{"ENGINE":"django.db.backends.postgresql","NAME":os.getenv("POSTGRES_DB","jopets"),"USER":os.getenv("POSTGRES_USER","jopets"),"PASSWORD":os.getenv("POSTGRES_PASSWORD",""),"HOST":os.getenv("POSTGRES_HOST","localhost"),"PORT":os.getenv("POSTGRES_PORT","5432")}}
AUTH_USER_MODEL="accounts.User"
PASSWORD_HASHERS=["django.contrib.auth.hashers.Argon2PasswordHasher"]
REST_FRAMEWORK={"DEFAULT_AUTHENTICATION_CLASSES":["rest_framework_simplejwt.authentication.JWTAuthentication"],"DEFAULT_PERMISSION_CLASSES":["rest_framework.permissions.IsAuthenticated"]}
CHANNEL_LAYERS={"default":{"BACKEND":"channels_redis.core.RedisChannelLayer","CONFIG":{"hosts":[os.getenv("REDIS_URL","redis://localhost:6379/0")]}}}
LANGUAGE_CODE="es"
TIME_ZONE="UTC"
USE_I18N=True
USE_TZ=True
STATIC_URL="static/"
DEFAULT_AUTO_FIELD="django.db.models.BigAutoField"
SIMA_MASTER_EMAIL="simasolutions9@gmail.com"
SECURE_SSL_REDIRECT=not DEBUG
SESSION_COOKIE_SECURE=not DEBUG
CSRF_COOKIE_SECURE=not DEBUG
SECURE_PROXY_SSL_HEADER=("HTTP_X_FORWARDED_PROTO","https")
SECURE_HSTS_SECONDS=31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS=not DEBUG
SECURE_HSTS_PRELOAD=not DEBUG
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS="DENY"
CSRF_TRUSTED_ORIGINS=[x for x in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if x]
