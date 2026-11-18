from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .security import validate_sima_identity
User=get_user_model()
class ClientRegisterView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        data=request.data
        email=str(data.get("email","")).strip().lower(); password=str(data.get("password","")); name=str(data.get("name","")).strip(); city=str(data.get("city","")).strip()
        if len(password)<12 or not email or not name or not city: return Response({"detail":"name, email, city y contraseña de mínimo 12 caracteres son obligatorios"},status=400)
        if User.objects.filter(username=email).exists(): return Response({"detail":"El correo ya está registrado"},status=409)
        user=User.objects.create(username=email,email=email,first_name=name,role="dueno_mascota",password=make_password(password),tenant_id=None)
        return Response({"id":user.pk,"role":user.role,"tenant_id":None},status=status.HTTP_201_CREATED)
class SimaIdentityCheckView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        try: validate_sima_identity(str(request.data.get("email","")))
        except Exception: return Response({"detail":"Identidad SIMA no autorizada"},status=403)
        return Response({"authorized":True,"mfa_required":True})
