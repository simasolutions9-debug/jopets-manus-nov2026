import uuid
from django.db import models


class AuditEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor_id = models.CharField(max_length=64, null=True, blank=True)
    tenant_id = models.UUIDField(null=True, blank=True)
    action = models.CharField(max_length=120)
    resource_type = models.CharField(max_length=80)
    resource_id = models.CharField(max_length=180, blank=True)
    outcome = models.CharField(max_length=24, default="success")
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)


class ChatMessage(models.Model):
    sender = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="sent_chat_messages")
    recipient = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="received_chat_messages")
    tenant_id = models.UUIDField()
    parent_tenant_id = models.UUIDField(null=True, blank=True)
    text = models.TextField(max_length=4000)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["tenant_id", "sender", "recipient", "created_at"]),
            models.Index(fields=["recipient", "is_read"]),
        ]
