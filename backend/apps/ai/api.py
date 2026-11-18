from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.memberships.agents import agent_status
class AgentStatusView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request): return Response({'agents':agent_status(),'inference':'not_configured'})
