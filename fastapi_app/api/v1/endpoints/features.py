from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any
from schemas.transaction import TransactionInput
from ml.preprocess import FeatureEngineer
from core.security import verify_api_key
from core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

feature_engineer = FeatureEngineer()

@router.post(
    "/extract",
    summary="Extract features",
    description="Extract engineered features from transaction data"
)
async def extract_features(
    transaction: TransactionInput,
    api_key: str = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    Extract and return engineered features.
    
    Useful for debugging and understanding feature engineering.
    """
    try:
        features = feature_engineer.extract_features(transaction.dict())
        return {
            'user_id': transaction.user_id,
            'amount': transaction.amount,
            'features': features
        }
    except Exception as e:
        logger.error(f"Error extracting features: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Feature extraction failed: {str(e)}"
        )

@router.get(
    "/info",
    summary="Feature information",
    description="Get information about available features"
)
async def feature_info():
    """
    Return information about features used by the model.
    """
    return {
        'feature_groups': {
            'transaction_features': [
                'amount', 'log_amount', 'amount_bin'
            ],
            'temporal_features': [
                'hour', 'day_of_week', 'is_weekend', 'is_night', 'day_of_month'
            ],
            'velocity_features': [
                'txn_count_1h', 'txn_count_24h', 'txn_amount_24h', 'avg_txn_amount_24h'
            ],
            'merchant_features': [
                'merchant_category_encoded', 'merchant_risk_score'
            ],
            'location_features': [
                'country_encoded', 'is_foreign_transaction'
            ],
            'device_features': [
                'device_risk_score'
            ],
            'type_features': [
                'transaction_type_encoded'
            ]
        },
        'total_features': 18
    }
