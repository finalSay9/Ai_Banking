import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime, timedelta
import redis
from core.config import settings
from core.logging import get_logger

logger = get_logger(__name__)

class FeatureEngineer:
    """Feature engineering for fraud detection."""
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
    
    def extract_features(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and engineer features from transaction data.
        
        Features:
        - Transaction amount features
        - Temporal features
        - Velocity features
        - Behavioral features
        - Location features
        """
        features = {}
        
        # Basic transaction features
        features['amount'] = float(transaction.get('amount', 0))
        features['log_amount'] = np.log1p(features['amount'])
        
        # Amount bins
        features['amount_bin'] = self._categorize_amount(features['amount'])
        
        # Temporal features
        txn_date = transaction.get('transaction_date')
        if isinstance(txn_date, str):
            txn_date = datetime.fromisoformat(txn_date.replace('Z', '+00:00'))
        elif not isinstance(txn_date, datetime):
            txn_date = datetime.now()
        
        features['hour'] = txn_date.hour
        features['day_of_week'] = txn_date.weekday()
        features['is_weekend'] = int(txn_date.weekday() >= 5)
        features['is_night'] = int(txn_date.hour < 6 or txn_date.hour > 22)
        features['day_of_month'] = txn_date.day
        
        # Velocity features (transaction frequency)
        user_id = transaction.get('user_id')
        if user_id:
            velocity_features = self._calculate_velocity_features(user_id)
            features.update(velocity_features)
        
        # Merchant features
        merchant_category = transaction.get('merchant_category', 'unknown')
        features['merchant_category_encoded'] = self._encode_merchant_category(merchant_category)
        features['merchant_risk_score'] = self._get_merchant_risk_score(
            transaction.get('merchant_id', '')
        )
        
        # Location features
        features['country_encoded'] = self._encode_country(transaction.get('country', ''))
        features['is_foreign_transaction'] = self._check_foreign_transaction(
            user_id, transaction.get('country', '')
        )
        
        # Device features
        features['device_risk_score'] = self._get_device_risk_score(
            transaction.get('device_id', '')
        )
        
        # Transaction type encoding
        txn_type = transaction.get('transaction_type', 'payment')
        features['transaction_type_encoded'] = self._encode_transaction_type(txn_type)
        
        return features
    
    def _categorize_amount(self, amount: float) -> int:
        """Categorize transaction amount into bins."""
        if amount < 10:
            return 0
        elif amount < 100:
            return 1
        elif amount < 1000:
            return 2
        elif amount < 10000:
            return 3
        else:
            return 4
    
    def _calculate_velocity_features(self, user_id: str) -> Dict[str, float]:
        """Calculate transaction velocity features."""
        cache_key = f"velocity:{user_id}"
        
        try:
            # Get transaction count from Redis
            txn_count_1h = int(self.redis_client.get(f"{cache_key}:1h") or 0)
            txn_count_24h = int(self.redis_client.get(f"{cache_key}:24h") or 0)
            txn_amount_24h = float(self.redis_client.get(f"{cache_key}:amount:24h") or 0)
            
            # Increment counters
            self.redis_client.incr(f"{cache_key}:1h")
            self.redis_client.expire(f"{cache_key}:1h", 3600)  # 1 hour
            
            self.redis_client.incr(f"{cache_key}:24h")
            self.redis_client.expire(f"{cache_key}:24h", 86400)  # 24 hours
            
            return {
                'txn_count_1h': txn_count_1h,
                'txn_count_24h': txn_count_24h,
                'txn_amount_24h': txn_amount_24h,
                'avg_txn_amount_24h': txn_amount_24h / max(txn_count_24h, 1)
            }
        except Exception as e:
            logger.error(f"Error calculating velocity features: {str(e)}")
            return {
                'txn_count_1h': 0,
                'txn_count_24h': 0,
                'txn_amount_24h': 0,
                'avg_txn_amount_24h': 0
            }
    
    def _encode_merchant_category(self, category: str) -> int:
        """Encode merchant category."""
        category_map = {
            'grocery': 1,
            'retail': 2,
            'restaurant': 3,
            'gas': 4,
            'online': 5,
            'travel': 6,
            'entertainment': 7,
            'healthcare': 8,
            'utilities': 9,
            'unknown': 0
        }
        return category_map.get(category.lower(), 0)
    
    def _get_merchant_risk_score(self, merchant_id: str) -> float:
        """Get risk score for merchant (from cache or database)."""
        if not merchant_id:
            return 0.5
        
        try:
            cache_key = f"merchant_risk:{merchant_id}"
            risk_score = self.redis_client.get(cache_key)
            if risk_score:
                return float(risk_score)
            return 0.5  # Default neutral risk
        except Exception:
            return 0.5
    
    def _encode_country(self, country: str) -> int:
        """Encode country code."""
        # High-risk countries get higher values
        high_risk_countries = ['XX', 'YY', 'ZZ']  # Replace with actual codes
        if country in high_risk_countries:
            return 3
        elif country:
            return 1
        return 0
    
    def _check_foreign_transaction(self, user_id: str, country: str) -> int:
        """Check if transaction is from foreign location."""
        if not user_id or not country:
            return 0
        
        try:
            cache_key = f"user_country:{user_id}"
            home_country = self.redis_client.get(cache_key)
            if home_country:
                return int(home_country.decode() != country)
            # Store current country as home country
            self.redis_client.setex(cache_key, 86400 * 30, country)  # 30 days
            return 0
        except Exception:
            return 0
    
    def _get_device_risk_score(self, device_id: str) -> float:
        """Get risk score for device."""
        if not device_id:
            return 0.5
        
        try:
            cache_key = f"device_risk:{device_id}"
            risk_score = self.redis_client.get(cache_key)
            if risk_score:
                return float(risk_score)
            return 0.3  # New devices get lower risk
        except Exception:
            return 0.5
    
    def _encode_transaction_type(self, txn_type: str) -> int:
        """Encode transaction type."""
        type_map = {
            'payment': 1,
            'transfer': 2,
            'withdrawal': 3,
            'deposit': 4,
            'purchase': 5
        }
        return type_map.get(txn_type.lower(), 0)
    
    def prepare_model_input(self, features: Dict[str, Any]) -> np.ndarray:
        """Prepare features for model input."""
        # Define feature order (must match training)
        feature_order = [
            'amount', 'log_amount', 'amount_bin',
            'hour', 'day_of_week', 'is_weekend', 'is_night', 'day_of_month',
            'txn_count_1h', 'txn_count_24h', 'txn_amount_24h', 'avg_txn_amount_24h',
            'merchant_category_encoded', 'merchant_risk_score',
            'country_encoded', 'is_foreign_transaction',
            'device_risk_score', 'transaction_type_encoded'
        ]
        
        # Extract features in correct order
        feature_vector = [features.get(f, 0) for f in feature_order]
        return np.array(feature_vector).reshape(1, -1)
