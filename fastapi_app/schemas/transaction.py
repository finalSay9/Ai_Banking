from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime

class TransactionInput(BaseModel):
    """Input schema for transaction fraud scoring."""
    
    user_id: str = Field(..., description="User/customer ID")
    account_number: Optional[str] = Field(None, description="Account number")
    amount: float = Field(..., gt=0, description="Transaction amount")
    currency: str = Field(default="USD", description="Currency code")
    
    transaction_type: str = Field(..., description="Type of transaction")
    merchant_id: Optional[str] = Field(None, description="Merchant ID")
    merchant_name: Optional[str] = Field(None, description="Merchant name")
    merchant_category: Optional[str] = Field(None, description="Merchant category")
    
    ip_address: Optional[str] = Field(None, description="IP address")
    country: Optional[str] = Field(None, description="Country code")
    city: Optional[str] = Field(None, description="City")
    device_id: Optional[str] = Field(None, description="Device ID")
    
    transaction_date: Optional[datetime] = Field(None, description="Transaction timestamp")
    ml_features: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional ML features")
    
    @validator('transaction_date', pre=True, always=True)
    def set_transaction_date(cls, v):
        return v or datetime.now()
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "USER123456",
                "account_number": "ACC789012",
                "amount": 1500.50,
                "currency": "USD",
                "transaction_type": "payment",
                "merchant_id": "MERCH001",
                "merchant_name": "Online Store XYZ",
                "merchant_category": "online",
                "ip_address": "192.168.1.1",
                "country": "US",
                "city": "New York",
                "device_id": "DEVICE_ABC123",
                "transaction_date": "2026-01-21T16:00:00Z"
            }
        }

class BulkTransactionInput(BaseModel):
    """Schema for bulk transaction processing."""
    transactions: list[TransactionInput] = Field(..., min_length=1, max_length=100)
