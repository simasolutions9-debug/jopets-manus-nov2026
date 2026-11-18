from uuid import UUID

from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tenants.models import Tenant
from .models import AuditEvent


class IsGlobalAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "admin_global")


class GlobalOverviewView(APIView):
    permission_classes = [IsGlobalAdmin]

    def get(self, request):
        return Response({
            "metrics": {
                "mrr": {"value": None, "status": "incomplete"},
                "churn": {"value": None, "status": "incomplete"},
                "ltv": {"value": None, "status": "incomplete"},
                "arpu": {"value": None, "status": "incomplete"},
            },
            "integrations": {
                "payments": {"status": "sandbox"},
                "gps": {"status": "not_connected"},
                "openwa": {"status": "not_configured"},
                "ai": {"status": "not_configured"},
            },
            "scope": "global_read_only",
        })


class GlobalAuditEventListView(APIView):
    permission_classes = [IsGlobalAdmin]

    def get(self, request):
        try:
            limit = min(max(int(request.query_params.get("limit", 50)), 1), 100)
        except (TypeError, ValueError):
            return Response({"detail": "limit inválido"}, status=400)
        queryset = AuditEvent.objects.all().order_by("-created_at")
        if request.query_params.get("action"):
            queryset = queryset.filter(action=request.query_params["action"])
        if request.query_params.get("outcome"):
            queryset = queryset.filter(outcome=request.query_params["outcome"])
        rows = list(queryset.values("id", "actor_id", "tenant_id", "action", "resource_type", "resource_id", "outcome", "metadata", "created_at")[:limit])
        return Response({"count": len(rows), "events": rows, "limit": limit})


class GlobalTenantListCreateView(APIView):
    permission_classes = [IsGlobalAdmin]

    def get(self, request):
        rows = Tenant.objects.order_by("-created_at").values(
            "id", "name", "parent_tenant_id", "plan", "isolation_mode", "is_active", "branding", "created_at"
        )
        return Response(list(rows))

    def post(self, request):
        name = str(request.data.get("name", "")).strip()
        plan = str(request.data.get("plan", "starter"))
        if not name:
            return Response({"detail": "El nombre del distribuidor es obligatorio"}, status=400)
        if plan not in {choice[0] for choice in Tenant.PLAN_CHOICES}:
            return Response({"detail": "Plan inválido"}, status=400)
        tenant = Tenant.objects.create(
            name=name,
            plan=plan,
            parent_tenant_id=request.data.get("parent_tenant_id") or None,
            branding=request.data.get("branding") if isinstance(request.data.get("branding"), dict) else {},
            is_active=False,
        )
        return Response({"id": str(tenant.id), "name": tenant.name, "plan": tenant.plan, "is_active": tenant.is_active}, status=201)


class GlobalTenantStatusView(APIView):
    permission_classes = [IsGlobalAdmin]

    def post(self, request, tenant_id):
        try:
            tenant = Tenant.objects.get(id=tenant_id)
        except (Tenant.DoesNotExist, ValueError):
            return Response({"detail": "Distribuidor no encontrado"}, status=404)
        status_value = str(request.data.get("status", "")).lower()
        if status_value not in {"approved", "rejected"}:
            return Response({"detail": "Estado debe ser approved o rejected"}, status=400)
        tenant.is_active = status_value == "approved"
        tenant.save(update_fields=["is_active"])
        return Response({"id": str(tenant.id), "is_active": tenant.is_active, "status": status_value})
