from decimal import Decimal
from uuid import UUID
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Order, Product
from .services import discount_from_points, points_for_order, validate_referral


def scoped_tenant(request):
    raw = request.headers.get("X-Tenant-ID")
    if not raw:
        raise PermissionError("Selecciona un proveedor válido")
    try:
        tenant = UUID(raw)
    except ValueError as exc:
        raise PermissionError("Tenant inválido") from exc
    if request.user.role != "admin_global" and request.user.tenant_id != tenant:
        raise PermissionError("Tenant no autorizado")
    return tenant


class ProductListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            tenant = scoped_tenant(request)
        except PermissionError as exc:
            return Response({"detail": str(exc)}, status=403)
        products = Product.objects.filter(tenant_id=tenant, active=True).values("id", "name", "price", "currency")
        return Response(list(products))


class OrderTransitionView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, order_id):
        try:
            tenant = scoped_tenant(request)
            order = Order.objects.get(id=order_id, tenant_id=tenant)
            order.transition(str(request.data.get("state", "")))
            order.save(update_fields=["state"])
        except Order.DoesNotExist:
            return Response({"detail": "Pedido no encontrado"}, status=404)
        except (PermissionError, ValueError) as exc:
            return Response({"detail": str(exc)}, status=403 if isinstance(exc, PermissionError) else 409)
        return Response({"id": str(order.id), "state": order.state})


class LoyaltyPreviewView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        points = points_for_order(request.data.get("total", "0"), request.data.get("currency", ""), request.data.get("status", ""))
        return Response({"points": points, "discount_for_points": str(discount_from_points(int(request.data.get("points", 0))))})


class ReferralEligibilityView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            credit = validate_referral(request.user.pk, request.data.get("invitee_id"), request.data.get("code"), bool(request.data.get("already_used")))
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)
        return Response({"eligible": True, "credit": str(credit)})
