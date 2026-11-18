from contextvars import ContextVar
from uuid import UUID
from django.core.exceptions import PermissionDenied

_current_tenant=ContextVar("jopets_current_tenant",default=None)
_current_parent=ContextVar("jopets_current_parent",default=None)
_global_access=ContextVar("jopets_global_access",default=False)

def set_scope(tenant_id=None,parent_tenant_id=None,*,global_access=False):
    if global_access and (tenant_id is not None or parent_tenant_id is not None): raise PermissionDenied("El acceso global no puede combinarse con un tenant")
    tenant=UUID(str(tenant_id)) if tenant_id else None
    parent=UUID(str(parent_tenant_id)) if parent_tenant_id else None
    return (_current_tenant.set(tenant),_current_parent.set(parent),_global_access.set(bool(global_access)))

def get_scope(): return _current_tenant.get(),_current_parent.get(),_global_access.get()
def clear_scope(tokens):
    t,p,g=tokens; _current_tenant.reset(t); _current_parent.reset(p); _global_access.reset(g)
