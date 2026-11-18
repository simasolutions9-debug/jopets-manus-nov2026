from django.db import models
from apps.tenants.models import TenantScopedModel
class PriceRule(models.Model):
    country=models.CharField(max_length=2); category=models.CharField(max_length=64); currency=models.CharField(max_length=3); base_price=models.DecimalField(max_digits=12,decimal_places=2); ppp_factor=models.DecimalField(max_digits=8,decimal_places=4,default=1); version=models.PositiveIntegerField(default=1); published=models.BooleanField(default=False); valid_from=models.DateTimeField(); valid_to=models.DateTimeField(null=True,blank=True)
class CommissionRegion(models.Model):
    country=models.CharField(max_length=2); category=models.CharField(max_length=64); commercial_level=models.PositiveSmallIntegerField(); provider_percent=models.DecimalField(max_digits=7,decimal_places=4); subowner_percent=models.DecimalField(max_digits=7,decimal_places=4); version=models.PositiveIntegerField(default=1); published=models.BooleanField(default=False)
class DetectionLog(TenantScopedModel):
    country=models.CharField(max_length=2); method=models.CharField(max_length=16); geoip_version=models.CharField(max_length=64,blank=True); created_at=models.DateTimeField(auto_now_add=True)
