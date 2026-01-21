from rest_framework import permissions
from common.constants import UserRole

class IsAdminUser(permissions.BasePermission):
    """Allow access only to admin users."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == UserRole.ADMIN

class IsFraudAnalyst(permissions.BasePermission):
    """Allow access to fraud analysts and admins."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               request.user.role in [UserRole.ADMIN, UserRole.FRAUD_ANALYST]

class IsRiskManager(permissions.BasePermission):
    """Allow access to risk managers and admins."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               request.user.role in [UserRole.ADMIN, UserRole.RISK_MANAGER]

class IsAuditor(permissions.BasePermission):
    """Allow access to auditors and admins."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               request.user.role in [UserRole.ADMIN, UserRole.AUDITOR]

class CanManageFraudCases(permissions.BasePermission):
    """Permission to manage fraud cases."""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user and request.user.role in [
            UserRole.ADMIN, UserRole.FRAUD_ANALYST
        ]
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role in [UserRole.ADMIN, UserRole.FRAUD_ANALYST]
