from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ITRiskAssessmentViewSet

router = DefaultRouter()
router.register('assessments', ITRiskAssessmentViewSet, basename='risk-assessment')

urlpatterns = [
    path('', include(router.urls)),
]
