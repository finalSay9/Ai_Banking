import logging
from typing import Dict, Any
from decimal import Decimal
from datetime import datetime, timedelta
from django.core.cache import cache

logger = logging.getLogger(__name__)

def calculate_fraud_score_locally(transaction_data: Dict[str, Any]) -> float:
    """
    Fallback local fraud scoring when ML service is unavailable.
    Uses rule-based heuristics.
    """
    score = 0.0
    
    amount = Decimal(str(transaction_data.get('amount', 0)))
    if amount > 50000:
        score += 0.3
    elif amount > 10000:
        score += 0.2
    
    # Check transaction frequency
    user_id = transaction_data.get('user_id')
    if user_id:
        cache_key = f'txn_count_{user_id}'
        txn_count = cache.get(cache_key, 0)
        if txn_count > 10:
            score += 0.3
        cache.set(cache_key, txn_count + 1, timeout=3600)
    
    # Time-based checks
    hour = datetime.now().hour
    if hour < 6 or hour > 23:
        score += 0.2
    
    return min(score, 1.0)

def get_risk_level_from_score(score: float) -> str:
    """Convert fraud score to risk level."""
    from common.constants import RiskLevel
    
    if score >= 0.8:
        return RiskLevel.CRITICAL
    elif score >= 0.5:
        return RiskLevel.HIGH
    elif score >= 0.3:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW

def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """Mask sensitive data like card numbers."""
    if len(data) <= visible_chars:
        return '*' * len(data)
    return '*' * (len(data) - visible_chars) + data[-visible_chars:]

def generate_transaction_reference() -> str:
    """Generate unique transaction reference."""
    from uuid import uuid4
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return f'TXN{timestamp}{str(uuid4())[:8].upper()}'
