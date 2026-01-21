from rest_framework.exceptions import APIException
from rest_framework import status

class MLServiceUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'ML scoring service is temporarily unavailable'
    default_code = 'ml_service_unavailable'

class FraudDetectionError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Error occurred during fraud detection'
    default_code = 'fraud_detection_error'

class InvalidTransactionData(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid transaction data provided'
    default_code = 'invalid_transaction_data'

class InsufficientPermissions(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You do not have permission to perform this action'
    default_code = 'insufficient_permissions'
