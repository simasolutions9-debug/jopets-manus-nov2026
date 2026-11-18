import uuid
from django.conf import settings
from django.db import models
from apps.tenants.models import TenantScopedModel
class ClientProfile(TenantScopedModel):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="client_profile")
    city=models.CharField(max_length=120)
class Pet(TenantScopedModel):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    owner=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="pets")
    name=models.CharField(max_length=120)
    species=models.CharField(max_length=80)
    breed=models.CharField(max_length=120,blank=True)
    backup_code_hash=models.CharField(max_length=128)
    health_data=models.JSONField(default=dict,blank=True)
class Vaccine(TenantScopedModel):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    pet=models.ForeignKey(Pet,on_delete=models.CASCADE,related_name="vaccines")
    name=models.CharField(max_length=160)
    administered_at=models.DateField()
    expires_at=models.DateField(null=True,blank=True)
    veterinarian=models.CharField(max_length=160,blank=True)
    notes=models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
class MedicalRecord(TenantScopedModel):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    pet=models.ForeignKey(Pet,on_delete=models.CASCADE,related_name="medical_records")
    event_type=models.CharField(max_length=64)
    title=models.CharField(max_length=160)
    occurred_at=models.DateTimeField()
    details=models.JSONField(default=dict,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
class Booking(TenantScopedModel):
    STATES=[("searched","Buscando"),("paid","Pagada"),("assigned","Buscando"),("en_route","En camino"),("arrived","En camino"),("verified","En camino"),("in_service","En servicio"),("completed","Completado"),("cancelled","Cancelada")]
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    pet=models.ForeignKey(Pet,on_delete=models.PROTECT)
    provider_id=models.CharField(max_length=64,null=True,blank=True)
    state=models.CharField(max_length=24,choices=STATES,default="searched")
    price_snapshot=models.JSONField(default=dict)
    arrived_at=models.DateTimeField(null=True,blank=True)
    verified_at=models.DateTimeField(null=True,blank=True)
    gps_lat=models.DecimalField(max_digits=9,decimal_places=6,null=True,blank=True)
    gps_lng=models.DecimalField(max_digits=9,decimal_places=6,null=True,blank=True)
    gps_risk=models.BooleanField(default=False)
    def transition(self,new_state):
        order=["searched","assigned","en_route","arrived","verified","in_service","completed"]
        if self.state == "paid" and new_state == "assigned": self.state=new_state; return
        if new_state=="cancelled" and self.state not in ("completed","cancelled"): self.state=new_state; return
        if self.state not in order or new_state not in order or order.index(new_state)!=order.index(self.state)+1: raise ValueError("Transición de reserva no permitida")
        self.state=new_state

class VerificationChallenge(TenantScopedModel):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    booking_id=models.UUIDField()
    token_hash=models.CharField(max_length=128)
    expires_at=models.DateTimeField()
    used_at=models.DateTimeField(null=True,blank=True)
    gps_risk=models.BooleanField(default=False)
class Notification(TenantScopedModel):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    recipient=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="notifications")
    title=models.CharField(max_length=180)
    message=models.TextField(blank=True)
    kind=models.CharField(max_length=48,default="general")
    is_read=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
