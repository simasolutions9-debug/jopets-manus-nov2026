import json
import os
from django.db import transaction
from django.utils import timezone
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.clients.models import Booking
from apps.core.audit import record_event, verify_webhook
from .models import ProviderWallet, WebhookEvent


class ProviderWalletView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != "proveedor":
            return Response({"detail": "Solo un proveedor puede consultar su billetera"}, status=403)
        raw_tenant = request.headers.get("X-Tenant-ID")
        if not raw_tenant or str(request.user.tenant_id) != raw_tenant:
            return Response({"detail": "Tenant no autorizado"}, status=403)
        wallet, _ = ProviderWallet.objects.get_or_create(provider_id=str(request.user.pk), tenant_id=request.user.tenant_id, parent_tenant_id=request.user.parent_tenant_id)
        transactions = list(wallet.transactions.order_by("-created_at").values("id", "external_id", "description", "amount", "status", "created_at")[:100])
        return Response({"provider_id": str(request.user.pk), "balance": wallet.available_balance, "pending_balance": wallet.pending_balance, "currency": wallet.currency, "transactions": transactions})


class PaymentWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        secret = os.getenv("PAYMENT_WEBHOOK_SECRET", "")
        timestamp = request.headers.get("X-Webhook-Timestamp", "")
        signature = request.headers.get("X-Webhook-Signature", "")
        if not secret:
            record_event(action="payment.webhook", resource_type="webhook", outcome="rejected", metadata={"reason": "not_configured"})
            return Response({"detail": "Webhook no configurado"}, status=503)
        try:
            payload = json.loads(request.body or b"{}")
        except json.JSONDecodeError:
            record_event(action="payment.webhook", resource_type="webhook", outcome="rejected", metadata={"reason": "invalid_json"})
            return Response({"detail": "JSON inválido"}, status=400)
        if not verify_webhook(payload, secret, timestamp, signature):
            record_event(action="payment.webhook", resource_type="webhook", outcome="rejected", metadata={"reason": "invalid_signature"})
            return Response({"detail": "Firma inválida o vencida"}, status=400)
        event_id = str(payload.get("id", ""))
        provider = str(payload.get("provider", "sandbox"))
        if not event_id:
            record_event(action="payment.webhook", resource_type="webhook", outcome="rejected", metadata={"reason": "missing_event_id"})
            return Response({"detail": "id de evento obligatorio"}, status=400)
        booking_id = payload.get("booking_id")
        payment_status = str(payload.get("status", "")).lower()
        booking_updated = False
        with transaction.atomic():
            event, created = WebhookEvent.objects.get_or_create(event_id=event_id, defaults={"provider": provider, "payload": payload})
            if not created:
                record_event(action="payment.webhook", resource_type="webhook", outcome="duplicate", resource_id=event_id, metadata={"provider": provider})
                return Response({"accepted": True, "duplicate": True})
            if booking_id and payment_status in {"paid", "captured", "succeeded", "approved"}:
                try:
                    booking = Booking.objects.select_for_update().get(id=booking_id)
                except Booking.DoesNotExist:
                    return Response({"detail": "Reserva asociada no encontrada"}, status=404)
                booking.state = "paid"
                booking.save(update_fields=["state"])
                booking_updated = True
                record_event(action="booking.payment_confirmed", resource_type="booking", resource_id=booking.id, tenant_id=booking.tenant_id, metadata={"provider": provider, "event_id": event_id})
            event.processed_at = timezone.now()
            event.save(update_fields=["processed_at"])
        record_event(action="payment.webhook", resource_type="webhook", resource_id=event_id, metadata={"provider": provider, "booking_id": str(booking_id) if booking_id else None})
        return Response({"accepted": True, "duplicate": False, "booking_updated": booking_updated}, status=202)
