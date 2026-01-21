"""
Basic API tests (expand as needed).
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "version" in response.json()

def test_health_check():
    """Test health endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] in ["healthy", "degraded", "unhealthy"]

def test_score_transaction():
    """Test transaction scoring."""
    transaction_data = {
        "user_id": "USER123",
        "amount": 1500.50,
        "currency": "USD",
        "transaction_type": "payment",
        "merchant_category": "online",
        "country": "US"
    }
    
    response = client.post("/api/v1/score", json=transaction_data)
    assert response.status_code == 200
    assert "fraud_score" in response.json()
    assert 0 <= response.json()["fraud_score"] <= 1

def test_feature_extraction():
    """Test feature extraction."""
    transaction_data = {
        "user_id": "USER123",
        "amount": 1500.50,
        "currency": "USD",
        "transaction_type": "payment"
    }
    
    response = client.post("/api/v1/features/extract", json=transaction_data)
    assert response.status_code == 200
    assert "features" in response.json()
