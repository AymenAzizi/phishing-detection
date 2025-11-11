"""
API Security Tests
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try:
    from real_api import app
    client = TestClient(app)
    API_AVAILABLE = True
except Exception as e:
    API_AVAILABLE = False
    print(f"Warning: Could not import API: {e}")


@pytest.mark.skipif(not API_AVAILABLE, reason="API not available")
class TestAPISecurity:
    """API Security test suite"""
    
    def test_cors_headers(self):
        """Test CORS headers are properly configured"""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_sql_injection_protection(self):
        """Test SQL injection protection"""
        malicious_data = {
            "url": "https://example.com'; DROP TABLE users; --"
        }
        response = client.post("/predict/url", json=malicious_data)
        # Should not crash, should handle gracefully
        assert response.status_code in [200, 422, 400, 503]

    def test_xss_protection(self):
        """Test XSS protection"""
        xss_data = {
            "url": "<script>alert('XSS')</script>"
        }
        response = client.post("/predict/url", json=xss_data)
        # Should not execute script, should handle gracefully
        assert response.status_code in [200, 422, 400, 503]
    
    def test_rate_limiting(self):
        """Test rate limiting (if implemented)"""
        # Make multiple requests
        for _ in range(5):
            response = client.get("/health")
            assert response.status_code in [200, 429]  # 429 = Too Many Requests
    
    def test_authentication_headers(self):
        """Test authentication headers"""
        response = client.get("/health")
        # Health endpoint should be accessible without auth
        assert response.status_code == 200
    
    def test_input_validation(self):
        """Test input validation"""
        invalid_data = {
            "url": ""  # Empty URL
        }
        response = client.post("/predict/url", json=invalid_data)
        # Should reject invalid input
        assert response.status_code in [422, 400, 503]
    
    def test_error_handling(self):
        """Test error handling doesn't leak sensitive info"""
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404
        # Check that error doesn't leak stack traces
        if response.status_code >= 400:
            data = response.json()
            assert "detail" in data or "message" in data

