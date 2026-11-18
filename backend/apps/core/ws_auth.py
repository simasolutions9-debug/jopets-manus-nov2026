from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.authentication import JWTAuthentication


User = get_user_model()


class JWTWebSocketMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        scope = dict(scope)
        headers = {key.lower(): value for key, value in scope.get("headers", [])}
        authorization = headers.get(b"authorization", b"").decode()
        token = ""
        if authorization.lower().startswith("bearer "):
            token = authorization[7:].strip()
        if not token:
            query = parse_qs(scope.get("query_string", b"").decode())
            token = query.get("token", [""])[0]
        scope["user"] = await self._user_from_token(token)
        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def _user_from_token(self, raw_token):
        if not raw_token:
            return User.get_anonymous() if hasattr(User, "get_anonymous") else None
        try:
            validated = AccessToken(raw_token)
            return JWTAuthentication().get_user(validated)
        except (TokenError, User.DoesNotExist, KeyError, ValueError):
            return None
