from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import ITRiskAssessment
from common.permissions import IsRiskManager

class ITRiskAssessmentViewSet(viewsets.ModelViewSet):
    queryset = ITRiskAssessment.objects.all()
    permission_classes = [IsAuthenticated, IsRiskManager]
    
    # Add serializers and methods as needed
