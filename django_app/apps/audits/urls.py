from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import ForensicInvestigation
from common.permissions import IsAuditor

class ForensicInvestigationViewSet(viewsets.ModelViewSet):
    queryset = ForensicInvestigation.objects.all()
    permission_classes = [IsAuthenticated, IsAuditor]
    
    # Add serializers and methods as needed
