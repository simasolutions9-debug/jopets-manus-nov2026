from django.contrib.auth.models import AbstractUser
from django.db import models
class User(AbstractUser):
    ROLE_CHOICES=[("admin_global","Admin Global"),("sub_dueno","Subdueño"),("proveedor","Proveedor"),("dueno_mascota","Dueño de mascota")]
    role=models.CharField(max_length=32,choices=ROLE_CHOICES,default="dueno_mascota")
    tenant_id=models.UUIDField(null=True,blank=True)
    parent_tenant_id=models.UUIDField(null=True,blank=True)
    mfa_enabled=models.BooleanField(default=False)
    totp_secret_ciphertext=models.TextField(blank=True)
    failed_login_attempts=models.PositiveIntegerField(default=0)
    locked_until=models.DateTimeField(null=True,blank=True)
