from django.utils import timezone
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from apps.core.security import decrypt_text
from .security import requires_totp, verify_totp


class JopetsTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        try:
            data = super().validate(attrs)
        except AuthenticationFailed:
            raise
        user = self.user
        if not user.is_active:
            raise AuthenticationFailed("Cuenta inactiva")
        if user.locked_until and user.locked_until > timezone.now():
            raise AuthenticationFailed("Cuenta temporalmente bloqueada")
        if requires_totp(user.role):
            if not user.mfa_enabled or not user.totp_secret_ciphertext:
                raise AuthenticationFailed("MFA obligatorio no configurado")
            code = self.initial_data.get("totp_code", "")
            try:
                secret = decrypt_text(user.totp_secret_ciphertext, aad=b"jopets-totp")
            except Exception as exc:
                raise AuthenticationFailed("MFA no disponible") from exc
            if not verify_totp(secret, str(code)):
                raise AuthenticationFailed("Código TOTP inválido")
        data["role"] = user.role
        data["user_id"] = str(user.pk)
        data["tenant_id"] = str(user.tenant_id) if user.tenant_id else None
        return data
