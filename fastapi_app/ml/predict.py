import joblib
import numpy as np
from typing import Dict, Any, Tuple
from pathlib import Path
from core.config import settings
from core.logging import get_logger
from sklearn.preprocessing import StandardScaler

logger = get_logger(__name__)

class FraudPredictor:
    """ML model for fraud prediction."""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.model_loaded = False
        self._load_model()
    
    def _load_model(self):
        """Load trained model and scaler."""
        try:
            model_path = Path(settings.MODEL_PATH)
            scaler_path = Path(settings.SCALER_PATH)
            
            if model_path.exists():
                self.model = joblib.load(model_path)
                logger.info(f"Model loaded from {model_path}")
            else:
                logger.warning(f"Model file not found: {model_path}")
                self._create_dummy_model()
            
            if scaler_path.exists():
                self.scaler = joblib.load(scaler_path)
                logger.info(f"Scaler loaded from {scaler_path}")
            else:
                logger.warning(f"Scaler file not found: {scaler_path}")
                self._create_dummy_scaler()
            
            self.model_loaded = True
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            self._create_dummy_model()
            self._create_dummy_scaler()
    
    def _create_dummy_model(self):
        """Create dummy model for testing (replace with actual trained model)."""
        from sklearn.ensemble import RandomForestClassifier
        
        logger.warning("Using dummy model - train and save a real model for production!")
        self.model = RandomForestClassifier(n_estimators=10, random_state=42)
        
        # Create dummy training data
        X_dummy = np.random.rand(100, 18)
        y_dummy = np.random.randint(0, 2, 100)
        self.model.fit(X_dummy, y_dummy)
    
    def _create_dummy_scaler(self):
        """Create dummy scaler for testing."""
        
        
        logger.warning("Using dummy scaler - train and save a real scaler for production!")
        self.scaler = StandardScaler()
        
        # Fit on dummy data
        X_dummy = np.random.rand(100, 18)
        self.scaler.fit(X_dummy)
    
    def predict(self, features: np.ndarray) -> Tuple[float, float]:
        """
        Predict fraud probability.
        
        Returns:
            Tuple of (fraud_score, confidence)
        """
        if not self.model_loaded:
            raise RuntimeError("Model not loaded")
        
        try:
            # Scale features
            if self.scaler:
                features_scaled = self.scaler.transform(features)
            else:
                features_scaled = features
            
            # Get prediction probability
            fraud_proba = self.model.predict_proba(features_scaled)[0]
            fraud_score = float(fraud_proba[1])  # Probability of fraud class
            
            # Calculate confidence (distance from decision boundary)
            confidence = abs(fraud_score - 0.5) * 2
            
            return fraud_score, confidence
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            raise
    
    def predict_with_explanation(self, features: np.ndarray) -> Dict[str, Any]:
        """
        Predict with feature importance explanation.
        """
        fraud_score, confidence = self.predict(features)
        
        # Get feature importances
        if hasattr(self.model, 'feature_importances_'):
            feature_names = [
                'amount', 'log_amount', 'amount_bin',
                'hour', 'day_of_week', 'is_weekend', 'is_night', 'day_of_month',
                'txn_count_1h', 'txn_count_24h', 'txn_amount_24h', 'avg_txn_amount_24h',
                'merchant_category', 'merchant_risk', 'country', 'is_foreign',
                'device_risk', 'transaction_type'
            ]
            
            importances = self.model.feature_importances_
            top_features = sorted(
                zip(feature_names, importances),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            explanation = {
                'top_features': [
                    {'feature': name, 'importance': float(imp)}
                    for name, imp in top_features
                ]
            }
        else:
            explanation = {'top_features': []}
        
        return {
            'fraud_score': fraud_score,
            'confidence': confidence,
            'explanation': explanation
        }
