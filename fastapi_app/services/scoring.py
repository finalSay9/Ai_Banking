import time
from typing import Dict, Any
from ml.preprocess import FeatureEngineer
from ml.predict import FraudPredictor
from core.config import settings
from core.logging import get_logger

logger = get_logger(__name__)

class FraudScoringService:
    """Service for fraud scoring operations."""
    
    def __init__(self):
        self.feature_engineer = FeatureEngineer()
        self.predictor = FraudPredictor()
    
    def score_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score a single transaction for fraud.
        
        Returns complete prediction with risk level and recommendation.
        """
        start_time = time.time()
        
        try:
            # Extract features
            features = self.feature_engineer.extract_features(transaction_data)
            
            # Prepare model input
            model_input = self.feature_engineer.prepare_model_input(features)
            
            # Get prediction
            fraud_score, confidence = self.predictor.predict(model_input)
            
            # Determine risk level
            risk_level = self._determine_risk_level(fraud_score)
            
            # Generate recommendation
            recommendation = self._generate_recommendation(fraud_score, risk_level)
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000
            
            return {
                'fraud_score': round(fraud_score, 4),
                'risk_level': risk_level,
                'confidence': round(confidence, 4),
                'recommendation': recommendation,
                'model_version': settings.MODEL_VERSION,
                'processing_time_ms': round(processing_time, 2)
            }
            
        except Exception as e:
            logger.error(f"Error scoring transaction: {str(e)}")
            raise
    
    def score_transaction_detailed(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score transaction with detailed explanation.
        """
        start_time = time.time()
        
        try:
            # Extract features
            features = self.feature_engineer.extract_features(transaction_data)
            
            # Prepare model input
            model_input = self.feature_engineer.prepare_model_input(features)
            
            # Get prediction with explanation
            result = self.predictor.predict_with_explanation(model_input)
            
            fraud_score = result['fraud_score']
            confidence = result['confidence']
            explanation = result['explanation']
            
            # Determine risk level
            risk_level = self._determine_risk_level(fraud_score)
            
            # Generate recommendation
            recommendation = self._generate_recommendation(fraud_score, risk_level)
            
            # Apply rule-based checks
            triggered_rules = self._apply_rules(transaction_data, features)
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000
            
            return {
                'fraud_score': round(fraud_score, 4),
                'risk_level': risk_level,
                'confidence': round(confidence, 4),
                'recommendation': recommendation,
                'model_version': settings.MODEL_VERSION,
                'processing_time_ms': round(processing_time, 2),
                'explanation': explanation,
                'triggered_rules': triggered_rules
            }
            
        except Exception as e:
            logger.error(f"Error in detailed scoring: {str(e)}")
            raise
    
    def _determine_risk_level(self, fraud_score: float) -> str:
        """Determine risk level from fraud score."""
        if fraud_score >= settings.FRAUD_THRESHOLD_HIGH:
            return "CRITICAL"
        elif fraud_score >= 0.7:
            return "HIGH"
        elif fraud_score >= settings.FRAUD_THRESHOLD_MEDIUM:
            return "MEDIUM"
        return "LOW"
    
    def _generate_recommendation(self, fraud_score: float, risk_level: str) -> str:
        """Generate action recommendation."""
        if risk_level == "CRITICAL":
            return "REJECT"
        elif risk_level == "HIGH":
            return "REVIEW_REQUIRED"
        elif risk_level == "MEDIUM":
            return "FLAG_FOR_MONITORING"
        return "APPROVE"
    
    def _apply_rules(self, transaction_data: Dict[str, Any], features: Dict[str, Any]) -> list:
        """Apply rule-based fraud checks."""
        triggered_rules = []
        
        # Rule 1: High amount
        amount = features.get('amount', 0)
        if amount > settings.MAX_TRANSACTION_AMOUNT:
            triggered_rules.append({
                'rule': 'high_amount',
                'message': f'Amount ${amount:.2f} exceeds maximum limit'
            })
        
        # Rule 2: High velocity
        txn_count_1h = features.get('txn_count_1h', 0)
        if txn_count_1h > 10:
            triggered_rules.append({
                'rule': 'high_velocity',
                'message': f'{txn_count_1h} transactions in last hour'
            })
        
        # Rule 3: Night transaction
        if features.get('is_night', 0) == 1 and amount > 5000:
            triggered_rules.append({
                'rule': 'unusual_time',
                'message': 'Large transaction during night hours'
            })
        
        # Rule 4: Foreign transaction
        if features.get('is_foreign_transaction', 0) == 1:
            triggered_rules.append({
                'rule': 'foreign_location',
                'message': 'Transaction from unusual location'
            })
        
        return triggered_rules
