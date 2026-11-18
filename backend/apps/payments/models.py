import uuid
from django.db import models
from apps.tenants.models import TenantScopedModel
class Transaccion(TenantScopedModel):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    external_id=models.CharField(max_length=180,blank=True)
    amount=models.DecimalField(max_digits=14,decimal_places=2)
    currency=models.CharField(max_length=3)
    status=models.CharField(max_length=32,default="pending")
    gateway=models.CharField(max_length=32)
    price_snapshot=models.JSONField(default=dict)
    created_at=models.DateTimeField(auto_now_add=True)
class PaymentOperation(TenantScopedModel):
    idempotency_key=models.CharField(max_length=180,unique=True)
    transaction=models.ForeignKey(Transaccion,on_delete=models.PROTECT,related_name="operations")
    kind=models.CharField(max_length=32)
    status=models.CharField(max_length=32,default="pending")
    payload=models.JSONField(default=dict)
    created_at=models.DateTimeField(auto_now_add=True)
class Allocation(TenantScopedModel):
    transaction=models.ForeignKey(Transaccion,on_delete=models.PROTECT,related_name="allocations")
    recipient_role=models.CharField(max_length=32)
    percentage=models.DecimalField(max_digits=7,decimal_places=4)
    amount=models.DecimalField(max_digits=14,decimal_places=2)
class WebhookEvent(models.Model):
    provider=models.CharField(max_length=32)
    event_id=models.CharField(max_length=180,unique=True)
    payload=models.JSONField(default=dict)
    processed_at=models.DateTimeField(null=True,blank=True)

class PaymentOutbox(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    event_type=models.CharField(max_length=80)
    aggregate_id=models.UUIDField()
    idempotency_key=models.CharField(max_length=180,unique=True)
    payload=models.JSONField(default=dict)
    status=models.CharField(max_length=24,default="pending")
    attempts=models.PositiveIntegerField(default=0)
    processed_at=models.DateTimeField(null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
class ProviderWallet(TenantScopedModel):
    provider_id=models.CharField(max_length=64,unique=True)
    currency=models.CharField(max_length=3,default="USD")
    available_balance=models.DecimalField(max_digits=14,decimal_places=2,default=0)
    pending_balance=models.DecimalField(max_digits=14,decimal_places=2,default=0)
    updated_at=models.DateTimeField(auto_now=True)
class WalletTransaction(TenantScopedModel):
    wallet=models.ForeignKey(ProviderWallet,on_delete=models.CASCADE,related_name="transactions")
    external_id=models.CharField(max_length=180,blank=True)
    description=models.CharField(max_length=180)
    amount=models.DecimalField(max_digits=14,decimal_places=2)
    status=models.CharField(max_length=32,default="pending")
    created_at=models.DateTimeField(auto_now_add=True)
