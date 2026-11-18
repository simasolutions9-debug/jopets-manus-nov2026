from django.urls import path
from django.http import JsonResponse
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.views import TokenObtainPairView
from apps.accounts.api import ClientRegisterView, SimaIdentityCheckView
from apps.accounts.token import JopetsTokenObtainPairSerializer
from apps.tenants.api import BrandingView
from apps.marketplace.api import ProductListView, OrderTransitionView, LoyaltyPreviewView, ReferralEligibilityView
from apps.clients.api import PetListCreateView, PetDetailView, PetQrView, MedicalHistoryView, VaccineListCreateView, NotificationListView, BookingListCreateView, ProviderAgendaView, BookingChallengeView, BookingTransitionView
from apps.memberships.api import MembershipBenefitsView, TeleVetStatusView
from apps.ai.api import AgentStatusView
from apps.core.global_api import GlobalOverviewView, GlobalAuditEventListView, GlobalTenantListCreateView, GlobalTenantStatusView
from apps.payments.api import PaymentWebhookView, ProviderWalletView


class JopetsTokenObtainPairView(TokenObtainPairView):
    serializer_class = JopetsTokenObtainPairSerializer


def health(request):
    return JsonResponse({
        "status": "ok",
        "service": "jopets-api",
        "integrations": {"payments": "sandbox", "ai": "not_configured", "gps": "not_configured"},
    })


urlpatterns = [
    path("api/healthz", health),
    path("api/auth/token", JopetsTokenObtainPairView.as_view()),
    path("api/auth/token/refresh", TokenRefreshView.as_view()),
    path("api/auth/register", ClientRegisterView.as_view()),
    path("api/auth/sima/check", SimaIdentityCheckView.as_view()),
    path("api/tenant/branding/", BrandingView.as_view()),
    path("api/marketplace/products", ProductListView.as_view()),
    path("api/marketplace/orders/<uuid:order_id>/transition", OrderTransitionView.as_view()),
    path("api/marketplace/loyalty/preview", LoyaltyPreviewView.as_view()),
    path("api/marketplace/referrals/eligibility", ReferralEligibilityView.as_view()),
    path("api/client/pets", PetListCreateView.as_view()),
    path("api/client/pets/<uuid:pet_id>", PetDetailView.as_view()),
    path("api/client/pets/<uuid:pet_id>/qr", PetQrView.as_view()),
    path("api/client/pets/<uuid:pet_id>/medical-history", MedicalHistoryView.as_view()),
    path("api/client/pets/<uuid:pet_id>/vaccines", VaccineListCreateView.as_view()),
    path("api/client/notifications", NotificationListView.as_view()),
    path("api/client/bookings", BookingListCreateView.as_view()),
    path("api/provider/bookings", ProviderAgendaView.as_view()),
    path("api/client/bookings/<uuid:booking_id>/challenge", BookingChallengeView.as_view()),
    path("api/client/bookings/<uuid:booking_id>/transition", BookingTransitionView.as_view()),
    path("api/client/memberships/benefits", MembershipBenefitsView.as_view()),
    path("api/client/tele-vet/status", TeleVetStatusView.as_view()),
    path("api/ai/agents/status", AgentStatusView.as_view()),
    path("api/global/overview", GlobalOverviewView.as_view()),
    path("api/global/audit-events", GlobalAuditEventListView.as_view()),
    path("api/global/tenants", GlobalTenantListCreateView.as_view()),
    path("api/global/tenants/<uuid:tenant_id>/status", GlobalTenantStatusView.as_view()),
    path("api/payments/webhook", PaymentWebhookView.as_view()),
    path("api/provider/wallet", ProviderWalletView.as_view()),
]
