import re
from uuid import UUID
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Tenant
HEX=re.compile(r"^#[0-9a-fA-F]{6}$")
def valid_branding(t):
    b=t.branding or {}; logo=b.get("logo_url",""); primary=b.get("color_primario",""); secondary=b.get("color_secundario","")
    return isinstance(logo,str) and (not logo or logo.startswith("https://")) and isinstance(primary,str) and (not primary or HEX.fullmatch(primary)) and isinstance(secondary,str) and (not secondary or HEX.fullmatch(secondary))
class BrandingView(APIView):
    permission_classes=[AllowAny]
    def get(self,request):
        try: tenant=Tenant.objects.get(pk=UUID(str(request.query_params.get("tenant_id"))))
        except (Tenant.DoesNotExist,ValueError,TypeError): tenant=None
        if not tenant or not tenant.is_active or not valid_branding(tenant): return Response({"nombre":"Jopets","logo_url":"","color_primario":"#0A2540","color_secundario":"#F97316"})
        b=tenant.branding
        return Response({"nombre":tenant.name,"logo_url":b.get("logo_url",""),"color_primario":b.get("color_primario","#0A2540"),"color_secundario":b.get("color_secundario","#F97316")})
