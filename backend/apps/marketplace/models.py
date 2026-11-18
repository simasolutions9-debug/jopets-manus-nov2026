import uuid
from django.db import models
from apps.tenants.models import TenantScopedModel
class Product(TenantScopedModel):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    name=models.CharField(max_length=180); price=models.DecimalField(max_digits=12,decimal_places=2); currency=models.CharField(max_length=3,default="USD"); active=models.BooleanField(default=True)
class Order(TenantScopedModel):
    STATES=["pending_payment","paid","preparing","ready","dispatched","delivered","cancelled"]
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    customer_id=models.UUIDField(); state=models.CharField(max_length=24,default="pending_payment")
    def transition(self,new_state):
        if new_state=="cancelled" and self.state not in {"delivered","cancelled"}: self.state=new_state; return
        if self.state not in self.STATES or new_state not in self.STATES or self.STATES.index(new_state)!=self.STATES.index(self.state)+1: raise ValueError("Transición de pedido no permitida")
        self.state=new_state
class OrderLine(TenantScopedModel):
    order=models.ForeignKey(Order,on_delete=models.PROTECT,related_name="lines"); product=models.ForeignKey(Product,on_delete=models.PROTECT); quantity=models.PositiveIntegerField(); unit_price=models.DecimalField(max_digits=12,decimal_places=2)
class LoyaltyAccount(TenantScopedModel):
    customer_id=models.UUIDField(unique=True); points=models.PositiveIntegerField(default=0)
class LoyaltyLedgerEntry(TenantScopedModel):
    account=models.ForeignKey(LoyaltyAccount,on_delete=models.PROTECT,related_name="ledger"); event_key=models.CharField(max_length=180,unique=True); delta=models.IntegerField(); reason=models.CharField(max_length=120)
class Referral(TenantScopedModel):
    code=models.CharField(max_length=32,unique=True); inviter_id=models.UUIDField(); invitee_id=models.UUIDField(null=True,blank=True); credited=models.BooleanField(default=False)
