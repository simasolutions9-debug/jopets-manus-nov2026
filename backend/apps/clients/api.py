from uuid import UUID
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Booking, MedicalRecord, Notification, Pet, Vaccine, VerificationChallenge
from .qr import issue_pet_qr
from .verification import issue_challenge, verify_identity
from apps.core.audit import record_event


class IsPetOwner(BasePermission):
    message = "Solo un dueño de mascota puede acceder a este recurso."
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "dueno_mascota")


class IsProvider(BasePermission):
    message = "Solo un proveedor puede acceder a la agenda."
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "proveedor")


def tenant_from_request(request):
    raw = request.headers.get("X-Tenant-ID")
    if not raw:
        raise PermissionError("Selecciona un proveedor válido")
    try:
        tenant = UUID(raw)
    except (ValueError, AttributeError) as exc:
        raise PermissionError("Tenant inválido") from exc
    if request.user.role != "admin_global" and request.user.tenant_id != tenant:
        raise PermissionError("Tenant no autorizado")
    return tenant


def tenant_error(exc):
    return Response({"detail": str(exc)}, status=403)


class PetListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsPetOwner]
    def get(self, request):
        try:
            tenant = tenant_from_request(request)
        except PermissionError as exc:
            return tenant_error(exc)
        pets = Pet.objects.filter(owner=request.user, tenant_id=tenant).values("id", "name", "species", "breed", "health_data")
        return Response(list(pets))
    def post(self, request):
        try:
            tenant = tenant_from_request(request)
        except PermissionError as exc:
            return tenant_error(exc)
        if not request.data.get("name") or not request.data.get("species"):
            return Response({"detail": "name y species son obligatorios"}, status=400)
        pet = Pet.objects.create(owner=request.user, tenant_id=tenant, parent_tenant_id=request.user.parent_tenant_id, name=request.data["name"], species=request.data["species"], breed=request.data.get("breed", ""), backup_code_hash="pending")
        return Response({"id": str(pet.id), "name": pet.name, "species": pet.species}, status=201)


class PetDetailView(APIView):
    permission_classes = [IsAuthenticated, IsPetOwner]
    def _pet(self, request, pet_id):
        tenant = tenant_from_request(request)
        return tenant, Pet.objects.get(id=pet_id, owner=request.user, tenant_id=tenant)
    def patch(self, request, pet_id):
        try:
            tenant, pet = self._pet(request, pet_id)
        except PermissionError as exc:
            return tenant_error(exc)
        except Pet.DoesNotExist:
            return Response({"detail": "Mascota no encontrada"}, status=404)
        fields = [field for field in ("name", "species", "breed", "health_data") if field in request.data]
        for field in fields:
            if field in request.data:
                setattr(pet, field, request.data[field])
        if fields:
            pet.save(update_fields=fields)
        return Response({"id": str(pet.id), "name": pet.name, "species": pet.species, "breed": pet.breed, "health_data": pet.health_data})


class PetQrView(APIView):
    permission_classes = [IsAuthenticated, IsPetOwner]
    def get(self, request, pet_id):
        try:
            tenant = tenant_from_request(request)
            pet = Pet.objects.get(id=pet_id, owner=request.user, tenant_id=tenant)
        except PermissionError as exc:
            return tenant_error(exc)
        except Pet.DoesNotExist:
            return Response({"detail": "Mascota no encontrada"}, status=404)
        return Response({"pet_qr": issue_pet_qr(pet.id, request.user.id, pet.tenant_id)})


class MedicalHistoryView(APIView):
    permission_classes = [IsAuthenticated, IsPetOwner]
    def get(self, request, pet_id):
        try:
            tenant = tenant_from_request(request)
            pet = Pet.objects.get(id=pet_id, owner=request.user, tenant_id=tenant)
        except PermissionError as exc:
            return tenant_error(exc)
        except Pet.DoesNotExist:
            return Response({"detail": "Mascota no encontrada"}, status=404)
        vaccines = list(Vaccine.objects.filter(pet=pet, tenant_id=tenant).values("id", "name", "administered_at", "expires_at", "veterinarian", "notes"))
        records = list(MedicalRecord.objects.filter(pet=pet, tenant_id=tenant).values("id", "event_type", "title", "occurred_at", "details"))
        return Response({"pet_id": str(pet.id), "health_data": pet.health_data, "vaccines": vaccines, "records": records})
    def post(self, request, pet_id):
        try:
            tenant = tenant_from_request(request)
            pet = Pet.objects.get(id=pet_id, owner=request.user, tenant_id=tenant)
        except PermissionError as exc:
            return tenant_error(exc)
        except Pet.DoesNotExist:
            return Response({"detail": "Mascota no encontrada"}, status=404)
        required = ("event_type", "title", "occurred_at")
        if any(not request.data.get(key) for key in required):
            return Response({"detail": "event_type, title y occurred_at son obligatorios"}, status=400)
        record = MedicalRecord.objects.create(pet=pet, tenant_id=tenant, parent_tenant_id=pet.parent_tenant_id, event_type=request.data["event_type"], title=request.data["title"], occurred_at=request.data["occurred_at"], details=request.data.get("details", {}))
        return Response({"id": str(record.id), "title": record.title}, status=201)


class VaccineListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsPetOwner]
    def get(self, request, pet_id):
        try:
            tenant = tenant_from_request(request)
            pet = Pet.objects.get(id=pet_id, owner=request.user, tenant_id=tenant)
        except PermissionError as exc:
            return tenant_error(exc)
        except Pet.DoesNotExist:
            return Response({"detail": "Mascota no encontrada"}, status=404)
        return Response(list(Vaccine.objects.filter(pet=pet, tenant_id=tenant).values("id", "name", "administered_at", "expires_at", "veterinarian", "notes")))
    def post(self, request, pet_id):
        try:
            tenant = tenant_from_request(request)
            pet = Pet.objects.get(id=pet_id, owner=request.user, tenant_id=tenant)
        except PermissionError as exc:
            return tenant_error(exc)
        except Pet.DoesNotExist:
            return Response({"detail": "Mascota no encontrada"}, status=404)
        if not request.data.get("name") or not request.data.get("administered_at"):
            return Response({"detail": "name y administered_at son obligatorios"}, status=400)
        vaccine = Vaccine.objects.create(pet=pet, tenant_id=tenant, parent_tenant_id=pet.parent_tenant_id, name=request.data["name"], administered_at=request.data["administered_at"], expires_at=request.data.get("expires_at"), veterinarian=request.data.get("veterinarian", ""), notes=request.data.get("notes", ""))
        return Response({"id": str(vaccine.id), "name": vaccine.name}, status=201)


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated, IsPetOwner]
    def get(self, request):
        try:
            tenant = tenant_from_request(request)
        except PermissionError as exc:
            return tenant_error(exc)
        rows = Notification.objects.filter(recipient=request.user, tenant_id=tenant).values("id", "title", "message", "kind", "is_read", "created_at").order_by("-created_at")
        return Response(list(rows))


class BookingListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsPetOwner]
    def get(self, request):
        try:
            tenant = tenant_from_request(request)
        except PermissionError as exc:
            return tenant_error(exc)
        rows = Booking.objects.filter(pet__owner=request.user, tenant_id=tenant).values("id", "pet_id", "provider_id", "state", "price_snapshot")
        return Response(list(rows))
    def post(self, request):
        try:
            tenant = tenant_from_request(request)
            pet = Pet.objects.get(id=request.data.get("pet_id"), owner=request.user, tenant_id=tenant)
        except PermissionError as exc:
            return tenant_error(exc)
        except Pet.DoesNotExist:
            return Response({"detail": "Mascota no encontrada en el tenant seleccionado"}, status=404)
        booking = Booking.objects.create(pet=pet, tenant_id=tenant, parent_tenant_id=pet.parent_tenant_id, provider_id=str(request.data.get("provider_id")) if request.data.get("provider_id") else None, price_snapshot=request.data.get("price_snapshot", {}))
        return Response({"id": str(booking.id), "state": booking.state}, status=201)


class ProviderAgendaView(APIView):
    permission_classes = [IsAuthenticated, IsProvider]
    def get(self, request):
        try:
            tenant = tenant_from_request(request)
        except PermissionError as exc:
            return tenant_error(exc)
        rows = Booking.objects.filter(provider_id=str(request.user.pk), tenant_id=tenant).values("id", "pet_id", "state", "price_snapshot", "arrived_at", "gps_lat", "gps_lng")
        return Response(list(rows))


class BookingChallengeView(APIView):
    permission_classes = [IsAuthenticated, IsPetOwner]
    def post(self, request, booking_id):
        try:
            tenant = tenant_from_request(request)
            booking = Booking.objects.get(id=booking_id, pet__owner=request.user, tenant_id=tenant)
        except PermissionError as exc:
            return tenant_error(exc)
        except Booking.DoesNotExist:
            return Response({"detail": "Reserva no encontrada"}, status=404)
        if booking.state != "arrived" or not booking.provider_id:
            return Response({"detail": "La reserva debe tener proveedor y llegada registrados"}, status=409)
        raw, digest, expires = issue_challenge()
        VerificationChallenge.objects.create(booking_id=booking.id, tenant_id=tenant, parent_tenant_id=booking.parent_tenant_id, token_hash=digest, expires_at=expires)
        record_event(action="booking.challenge_issued", resource_type="booking", resource_id=booking.id, actor_id=request.user.id, tenant_id=tenant)
        return Response({"challenge": raw, "expires_at": expires})


class BookingTransitionView(APIView):
    permission_classes = [IsAuthenticated, IsPetOwner]
    def post(self, request, booking_id):
        try:
            tenant = tenant_from_request(request)
            booking = Booking.objects.get(id=booking_id, pet__owner=request.user, tenant_id=tenant)
        except PermissionError as exc:
            return tenant_error(exc)
        except Booking.DoesNotExist:
            return Response({"detail": "Reserva no encontrada"}, status=404)
        new_state = request.data.get("state")
        if new_state == "arrived":
            booking.arrived_at = timezone.now()
        if new_state == "verified":
            challenge = VerificationChallenge.objects.filter(booking_id=booking.id, tenant_id=tenant, used_at__isnull=True).order_by("-expires_at").first()
            try:
                if not challenge: raise PermissionError("Desafío no disponible")
                verify_identity(challenge_raw=request.data.get("challenge", ""), challenge_hash=challenge.token_hash, expires_at=challenge.expires_at, used_at=challenge.used_at, qr_payload=request.data.get("pet_qr"), pet_id=booking.pet_id, owner_id=request.user.id, tenant_id=tenant, backup_code_valid=bool(request.data.get("backup_code")))
            except Exception as exc:
                booking.gps_risk = bool(request.data.get("gps_risk")); booking.save(update_fields=["gps_risk"])
                record_event(action="booking.transition", resource_type="booking", resource_id=booking.id, outcome="rejected", actor_id=request.user.id, tenant_id=tenant, metadata={"state": new_state, "gps_risk": booking.gps_risk})
                return Response({"detail": str(exc)}, status=403)
            challenge.used_at = timezone.now(); challenge.save(update_fields=["used_at"]); booking.verified_at = timezone.now()
        try:
            booking.transition(new_state)
        except ValueError as exc:
            record_event(action="booking.transition", resource_type="booking", resource_id=booking.id, outcome="rejected", actor_id=request.user.id, tenant_id=tenant, metadata={"state": new_state})
            return Response({"detail": str(exc)}, status=409)
        booking.save()
        record_event(action="booking.transition", resource_type="booking", resource_id=booking.id, actor_id=request.user.id, tenant_id=tenant, metadata={"state": booking.state, "gps_risk": booking.gps_risk})
        return Response({"id": str(booking.id), "state": booking.state, "gps_risk": booking.gps_risk})
