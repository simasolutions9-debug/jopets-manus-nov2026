from django.db import connection, transaction
from .context import clear_scope,set_scope
class TenantRoutingMiddleware:
    def __init__(self,get_response): self.get_response=get_response
    def __call__(self,request):
        user=getattr(request,"user",None)
        global_access=bool(user and user.is_authenticated and user.role=="admin_global")
        tokens=set_scope(getattr(user,"tenant_id",None) if user and user.is_authenticated else None,getattr(user,"parent_tenant_id",None) if user and user.is_authenticated else None,global_access=global_access)
        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute("SELECT set_config('jopets.global_access', %s, true)",["on" if global_access else "off"])
                    cursor.execute("SELECT set_config('jopets.tenant_id', %s, true)",[str(getattr(user,"tenant_id","") or "")])
                    cursor.execute("SELECT set_config('jopets.parent_tenant_id', %s, true)",[str(getattr(user,"parent_tenant_id","") or "")])
                    response=self.get_response(request)
            return response
        finally: clear_scope(tokens)
