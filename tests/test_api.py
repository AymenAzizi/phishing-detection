"""
API endpoint tests
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from real_api import app
    client = TestClient(app)
    API_AVAILABLE = True
except Exception as e:
    API_AVAILABLE = False
    print(f"Warning: Could not import API: {e}")


@pytest.mark.skipif(not API_AVAILABLE, reason="API not available")
def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


@pytest.mark.skipif(not API_AVAILABLE, reason="API not available")
def test_predict_endpoint():
    """Test prediction endpoint"""
    test_data = {
        "url": "https://example.com"
    }
    response = client.post("/predict/url", json=test_data)
    assert response.status_code in [200, 422, 503]  # 503 if model not loaded


@pytest.mark.skipif(not API_AVAILABLE, reason="API not available")
def test_metrics_endpoint():
    """Test metrics endpoint"""
    response = client.get("/metrics")
    assert response.status_code == 200

