from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TransactionViewSet,
    FraudCaseViewSet,
    AlertViewSet,
    FraudPatternViewSet,
    FraudStatisticsViewSet
)

router = DefaultRouter()
router.register('transactions', TransactionViewSet, basename='transaction')
router.register('cases', FraudCaseViewSet, basename='fraud-case')
router.register('alerts', AlertViewSet, basename='alert')
router.register('patterns', FraudPatternViewSet, basename='fraud-pattern')
router.register('statistics', FraudStatisticsViewSet, basename='statistics')

urlpatterns = [
    path('', include(router.urls)),
]
