import json
from uuid import UUID

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.tenants.models import Tenant
from .models import ChatMessage


User = get_user_model()


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")
        kwargs = self.scope.get("url_route", {}).get("kwargs", {})
        try:
            self.tenant_id = UUID(str(kwargs["tenant_id"]))
            self.peer_id = int(kwargs["peer_id"])
        except (KeyError, TypeError, ValueError):
            await self.close(code=4400)
            return
        if not await self._can_chat():
            await self.close(code=4403)
            return
        self.group_name = await self._group_name()
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self._mark_received_read()
        for message in await self._history():
            await self.send_json({"type": "message", **message})

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        text = str(content.get("text", "")).strip()
        if not text or len(text) > 4000:
            await self.send_json({"type": "error", "detail": "El mensaje debe tener entre 1 y 4000 caracteres."})
            return
        message = await self._create_message(text)
        await self.channel_layer.group_send(self.group_name, {"type": "chat.message", "message": message})

    async def chat_message(self, event):
        await self.send_json({"type": "message", **event["message"]})

    @database_sync_to_async
    def _can_chat(self):
        if not getattr(self.user, "is_authenticated", False):
            return False
        if self.user.role not in {"dueno_mascota", "proveedor", "sub_dueno", "admin_global"}:
            return False
        try:
            peer = User.objects.get(pk=self.peer_id, is_active=True)
            tenant = Tenant.objects.get(pk=self.tenant_id, is_active=True)
        except (User.DoesNotExist, Tenant.DoesNotExist):
            return False
        if self.user.role != "admin_global":
            user_tenant = self.user.tenant_id
            allowed_scope = user_tenant == self.tenant_id or self.user.parent_tenant_id == self.tenant_id
            if not allowed_scope and user_tenant:
                allowed_scope = tenant.parent_tenant_id == user_tenant
            if not allowed_scope:
                return False
        return peer.tenant_id == self.tenant_id or peer.parent_tenant_id == self.tenant_id

    @database_sync_to_async
    def _group_name(self):
        ids = sorted([str(self.user.pk), str(self.peer_id)])
        return f"chat_{self.tenant_id}_{ids[0]}_{ids[1]}"

    @database_sync_to_async
    def _history(self):
        rows = ChatMessage.objects.filter(tenant_id=self.tenant_id, sender_id__in=[self.user.pk, self.peer_id], recipient_id__in=[self.user.pk, self.peer_id]).order_by("-created_at")[:50]
        return [self._serialize(row) for row in reversed(list(rows))]

    @database_sync_to_async
    def _mark_received_read(self):
        ChatMessage.objects.filter(tenant_id=self.tenant_id, sender_id=self.peer_id, recipient_id=self.user.pk, is_read=False).update(is_read=True)

    @database_sync_to_async
    def _create_message(self, text):
        message = ChatMessage.objects.create(sender_id=self.user.pk, recipient_id=self.peer_id, tenant_id=self.tenant_id, text=text, parent_tenant_id=self.user.parent_tenant_id)
        return self._serialize(message)

    @staticmethod
    def _serialize(message):
        return {"id": str(message.id), "sender_id": str(message.sender_id), "recipient_id": str(message.recipient_id), "text": message.text, "created_at": message.created_at.isoformat(), "is_read": message.is_read}
