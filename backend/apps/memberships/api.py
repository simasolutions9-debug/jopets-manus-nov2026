from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class MembershipBenefitsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({"status": "not_configured", "benefits": [], "detail": "No hay membresía activa configurada para este tenant."})


class TeleVetStatusView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({"status": "not_configured", "available": False, "detail": "Tele-veterinaria requiere proveedor externo configurado."})
