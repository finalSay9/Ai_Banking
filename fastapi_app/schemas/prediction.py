from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, List, Optional
from datetime import datetime

class PredictionResponse(BaseModel):
    """Response schema for fraud prediction."""
    
    fraud_score: float = Field(..., ge=0, le=1, description="Fraud probability score (0-1)")
    risk_level: str = Field(..., description="Risk level: LOW, MEDIUM, HIGH, CRITICAL")
    confidence: float = Field(..., ge=0, le=1, description="Model confidence")
    recommendation: str = Field(..., description="Recommended action")
    
    model_version: str = Field(..., description="Model version used")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    timestamp: datetime = Field(default_factory=datetime.now, description="Prediction timestamp")
    
   

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "fraud_score": 0.85,
                "risk_level": "HIGH",
                "confidence": 0.92,
                "recommendation": "REJECT",
                "model_version": "1.0",
                "processing_time_ms": 45.2,
                "timestamp": "2026-01-21T16:00:00Z"
            }
        },
        protected_namespaces=()
    )

class DetailedPredictionResponse(PredictionResponse):
    """Extended response with feature explanations."""
    
    explanation: Dict[str, Any] = Field(..., description="Feature importance and explanation")
    triggered_rules: List[Dict[str, str]] = Field(default_factory=list, description="Triggered fraud rules")
    
    class Config:
        json_schema_extra = {
            "example": {
                "fraud_score": 0.85,
                "risk_level": "HIGH",
                "confidence": 0.92,
                "recommendation": "REJECT",
                "model_version": "1.0",
                "processing_time_ms": 45.2,
                "timestamp": "2026-01-21T16:00:00Z",
                "explanation": {
                    "top_features": [
                        {"feature": "amount", "importance": 0.35},
                        {"feature": "txn_count_1h", "importance": 0.22}
                    ]
                },
                "triggered_rules": [
                    {"rule": "high_amount", "message": "Transaction exceeds normal amount"}
                ]
            }
        }

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    model_loaded: bool
    timestamp: datetime = Field(default_factory=datetime.now)
