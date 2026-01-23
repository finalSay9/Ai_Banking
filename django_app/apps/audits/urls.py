from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ForensicInvestigationViewSet

router = DefaultRouter()
router.register('investigations', ForensicInvestigationViewSet, basename='forensic-investigation')

urlpatterns = [
    path('', include(router.urls)),
]
