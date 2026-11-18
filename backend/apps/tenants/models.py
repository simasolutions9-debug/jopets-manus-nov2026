import uuid
from django.db import models
class Tenant(models.Model):
    PLAN_CHOICES=[("starter","Starter"),("premium","Premium"),("enterprise","Enterprise")]
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    name=models.CharField(max_length=160)
    parent_tenant_id=models.UUIDField(null=True,blank=True)
    plan=models.CharField(max_length=16,choices=PLAN_CHOICES,default="starter")
    isolation_mode=models.CharField(max_length=16,default="rls")
    is_active=models.BooleanField(default=True)
    branding=models.JSONField(default=dict,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

class TenantScopedModel(models.Model):
    tenant_id=models.UUIDField()
    parent_tenant_id=models.UUIDField(null=True,blank=True)
    class Meta: abstract=True
