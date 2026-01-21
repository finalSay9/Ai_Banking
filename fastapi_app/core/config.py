from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application configuration."""
    
    # App settings
    APP_NAME: str = "Fraud Detection ML Service"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Model settings
    MODEL_PATH: str = "ml/models/fraud_model.pkl"
    SCALER_PATH: str = "ml/models/scaler.pkl"
    MODEL_VERSION: str = "1.0"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # Thresholds
    FRAUD_THRESHOLD_HIGH: float = 0.8
    FRAUD_THRESHOLD_MEDIUM: float = 0.5
    
    # Feature engineering
    VELOCITY_WINDOW_HOURS: int = 24
    MAX_TRANSACTION_AMOUNT: float = 1000000.0
    
    # Security
    API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
