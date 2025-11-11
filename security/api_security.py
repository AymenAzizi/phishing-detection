#!/usr/bin/env python3
"""
API Security Framework
Advanced security testing and protection for REST APIs
"""

import re
import time
import hashlib
import hmac
import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict, deque
import requests
from urllib.parse import urlparse, parse_qs

class RateLimiter:
    """Advanced rate limiting with multiple strategies"""
    
    def __init__(self, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.minute_requests = defaultdict(deque)
        self.hour_requests = defaultdict(deque)
        self.blocked_ips = set()
        
    def is_allowed(self, client_id: str, ip_address: str = None) -> bool:
        """Check if request is allowed based on rate limits"""
        try:
            current_time = time.time()
            identifier = ip_address or client_id
            
            # Check if IP is blocked
            if identifier in self.blocked_ips:
                return False
            
            # Clean old requests
            self._clean_old_requests(identifier, current_time)
            
            # Check minute limit
            minute_requests = self.minute_requests[identifier]
            if len(minute_requests) >= self.requests_per_minute:
                self.blocked_ips.add(identifier)
                return False
            
            # Check hour limit
            hour_requests = self.hour_requests[identifier]
            if len(hour_requests) >= self.requests_per_hour:
                self.blocked_ips.add(identifier)
                return False
            
            # Add current request
            minute_requests.append(current_time)
            hour_requests.append(current_time)
            
            return True
            
        except Exception as e:
            print(f"❌ Error in rate limiting: {e}")
            return False
    
    def _clean_old_requests(self, identifier: str, current_time: float):
        """Clean old requests from tracking"""
        # Clean minute requests (older than 60 seconds)
        minute_requests = self.minute_requests[identifier]
        while minute_requests and current_time - minute_requests[0] > 60:
            minute_requests.popleft()
        
        # Clean hour requests (older than 3600 seconds)
        hour_requests = self.hour_requests[identifier]
        while hour_requests and current_time - hour_requests[0] > 3600:
            hour_requests.popleft()
    
    def unblock_ip(self, ip_address: str):
        """Unblock an IP address"""
        self.blocked_ips.discard(ip_address)

class InputValidator:
    """Advanced input validation and sanitization"""
    
    def __init__(self):
        self.malicious_patterns = [
            # SQL Injection patterns
            r"('|(\\')|(;)|(--)|(/\*)|(\*/)|(\|)|(\|)|(\|)|(\|))",
            r"(union|select|insert|update|delete|drop|create|alter|exec|execute)",
            r"(script|javascript|vbscript|onload|onerror|onclick)",
            
            # XSS patterns
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"vbscript:",
            r"on\w+\s*=",
            
            # Path traversal patterns
            r"\.\./",
            r"\.\.\\",
            r"\.\.%2f",
            r"\.\.%5c",
            
            # Command injection patterns
            r"[;&|`$]",
            r"(cat|ls|pwd|whoami|id|uname|ps|netstat)",
            
            # LDAP injection patterns
            r"[()=*!&|]",
            
            # NoSQL injection patterns
            r"(\$where|\$ne|\$gt|\$lt|\$regex)",
        ]
        
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.malicious_patterns]
    
    def validate_input(self, input_data: str, input_type: str = "general") -> Dict[str, Any]:
        """Validate input data for security threats"""
        try:
            result = {
                'is_valid': True,
                'threats_detected': [],
                'risk_level': 'low',
                'sanitized_input': input_data
            }
            
            if not input_data or not isinstance(input_data, str):
                return result
            
            # Check for malicious patterns
            for i, pattern in enumerate(self.compiled_patterns):
                if pattern.search(input_data):
                    threat_type = self._get_threat_type(i)
                    result['threats_detected'].append(threat_type)
                    result['is_valid'] = False
            
            # Additional validation based on input type
            if input_type == "url":
                result.update(self._validate_url(input_data))
            elif input_type == "email":
                result.update(self._validate_email(input_data))
            elif input_type == "json":
                result.update(self._validate_json(input_data))
            
            # Determine risk level
            if result['threats_detected']:
                if len(result['threats_detected']) > 2:
                    result['risk_level'] = 'high'
                else:
                    result['risk_level'] = 'medium'
            
            # Sanitize input if threats detected
            if not result['is_valid']:
                result['sanitized_input'] = self._sanitize_input(input_data)
            
            return result
            
        except Exception as e:
            print(f"❌ Error in input validation: {e}")
            return {
                'is_valid': False,
                'threats_detected': ['validation_error'],
                'risk_level': 'high',
                'sanitized_input': ''
            }
    
    def _get_threat_type(self, pattern_index: int) -> str:
        """Get threat type based on pattern index"""
        threat_types = [
            'sql_injection', 'sql_injection', 'xss', 'xss', 'xss', 'xss',
            'path_traversal', 'path_traversal', 'path_traversal', 'path_traversal',
            'command_injection', 'command_injection',
            'ldap_injection', 'nosql_injection'
        ]
        return threat_types[min(pattern_index, len(threat_types) - 1)]
    
    def _validate_url(self, url: str) -> Dict[str, Any]:
        """Validate URL input"""
        try:
            parsed = urlparse(url)
            
            # Check for suspicious schemes
            suspicious_schemes = ['javascript', 'vbscript', 'data', 'file']
            if parsed.scheme.lower() in suspicious_schemes:
                return {
                    'threats_detected': ['suspicious_scheme'],
                    'is_valid': False
                }
            
            # Check for suspicious domains
            suspicious_domains = ['localhost', '127.0.0.1', '0.0.0.0']
            if parsed.hostname in suspicious_domains:
                return {
                    'threats_detected': ['suspicious_domain'],
                    'is_valid': False
                }
            
            return {'is_valid': True}
            
        except Exception:
            return {'is_valid': False, 'threats_detected': ['invalid_url']}
    
    def _validate_email(self, email: str) -> Dict[str, Any]:
        """Validate email input"""
        try:
            # Basic email regex
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                return {'is_valid': False, 'threats_detected': ['invalid_email']}
            
            return {'is_valid': True}
            
        except Exception:
            return {'is_valid': False, 'threats_detected': ['email_validation_error']}
    
    def _validate_json(self, json_str: str) -> Dict[str, Any]:
        """Validate JSON input"""
        try:
            json.loads(json_str)
            return {'is_valid': True}
        except json.JSONDecodeError:
            return {'is_valid': False, 'threats_detected': ['invalid_json']}
    
    def _sanitize_input(self, input_data: str) -> str:
        """Sanitize input data"""
        try:
            # Remove or escape dangerous characters
            sanitized = input_data
            
            # Remove script tags
            sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
            
            # Escape HTML entities
            sanitized = sanitized.replace('<', '&lt;').replace('>', '&gt;')
            sanitized = sanitized.replace('"', '&quot;').replace("'", '&#x27;')
            
            # Remove null bytes
            sanitized = sanitized.replace('\x00', '')
            
            return sanitized
            
        except Exception as e:
            print(f"❌ Error sanitizing input: {e}")
            return ""

class AuthenticationManager:
    """Advanced authentication and authorization"""
    
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or "default_secret_key_change_in_production"
        self.active_tokens = {}
        self.token_expiry = {}
        
    def generate_token(self, user_id: str, expires_in: int = 3600) -> str:
        """Generate secure authentication token"""
        try:
            current_time = int(time.time())
            expiry_time = current_time + expires_in
            
            # Create token payload
            payload = {
                'user_id': user_id,
                'issued_at': current_time,
                'expires_at': expiry_time
            }
            
            # Create token
            token_data = json.dumps(payload, sort_keys=True)
            token = hmac.new(
                self.secret_key.encode(),
                token_data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Store token
            self.active_tokens[token] = user_id
            self.token_expiry[token] = expiry_time
            
            return token
            
        except Exception as e:
            print(f"❌ Error generating token: {e}")
            return ""
    
    def validate_token(self, token: str) -> bool:
        """Validate authentication token"""
        try:
            if not token:
                return False
            
            # Check if token exists
            if token not in self.active_tokens:
                return False
            
            # Check if token is expired
            current_time = int(time.time())
            if token in self.token_expiry and current_time > self.token_expiry[token]:
                # Remove expired token
                del self.active_tokens[token]
                del self.token_expiry[token]
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error validating token: {e}")
            return False
    
    def revoke_token(self, token: str) -> bool:
        """Revoke authentication token"""
        try:
            if token in self.active_tokens:
                del self.active_tokens[token]
                if token in self.token_expiry:
                    del self.token_expiry[token]
                return True
            return False
            
        except Exception as e:
            print(f"❌ Error revoking token: {e}")
            return False

class APISecurityMonitor:
    """Monitor API security metrics and threats"""
    
    def __init__(self):
        self.security_events = []
        self.threat_counts = defaultdict(int)
        self.blocked_ips = set()
        self.rate_limit_violations = defaultdict(int)
        
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security events"""
        try:
            event = {
                'timestamp': datetime.now().isoformat(),
                'event_type': event_type,
                'details': details
            }
            
            self.security_events.append(event)
            self.threat_counts[event_type] += 1
            
            # Keep only last 1000 events
            if len(self.security_events) > 1000:
                self.security_events = self.security_events[-1000:]
            
        except Exception as e:
            print(f"❌ Error logging security event: {e}")
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get security summary report"""
        try:
            current_time = datetime.now()
            last_hour = current_time - timedelta(hours=1)
            
            # Filter recent events
            recent_events = [
                event for event in self.security_events
                if datetime.fromisoformat(event['timestamp']) > last_hour
            ]
            
            summary = {
                'total_events': len(self.security_events),
                'recent_events': len(recent_events),
                'threat_counts': dict(self.threat_counts),
                'blocked_ips': len(self.blocked_ips),
                'top_threats': self._get_top_threats(),
                'security_score': self._calculate_security_score()
            }
            
            return summary
            
        except Exception as e:
            print(f"❌ Error generating security summary: {e}")
            return {}
    
    def _get_top_threats(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top threats by frequency"""
        try:
            threat_freq = defaultdict(int)
            for event in self.security_events:
                threat_freq[event['event_type']] += 1
            
            sorted_threats = sorted(threat_freq.items(), key=lambda x: x[1], reverse=True)
            return [{'threat': threat, 'count': count} for threat, count in sorted_threats[:limit]]
            
        except Exception as e:
            print(f"❌ Error getting top threats: {e}")
            return []
    
    def _calculate_security_score(self) -> float:
        """Calculate security score (0-100)"""
        try:
            if not self.security_events:
                return 100.0
            
            # Penalize different threat types
            threat_penalties = {
                'sql_injection': 20,
                'xss': 15,
                'rate_limit_exceeded': 5,
                'invalid_input': 3,
                'authentication_failed': 10
            }
            
            total_penalty = 0
            for event in self.security_events[-100:]:  # Last 100 events
                event_type = event['event_type']
                penalty = threat_penalties.get(event_type, 1)
                total_penalty += penalty
            
            # Calculate score (max 100, minimum 0)
            score = max(0, 100 - total_penalty)
            return min(100, score)
            
        except Exception as e:
            print(f"❌ Error calculating security score: {e}")
            return 50.0

class SecurityHeaders:
    """Manage security headers for API responses"""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get comprehensive security headers"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'",
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
            'X-Permitted-Cross-Domain-Policies': 'none'
        }

# Command line interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='API Security Testing')
    parser.add_argument('--test-input', type=str, help='Test input validation')
    parser.add_argument('--test-rate-limit', action='store_true', help='Test rate limiting')
    parser.add_argument('--generate-report', action='store_true', help='Generate security report')
    
    args = parser.parse_args()
    
    if args.test_input:
        validator = InputValidator()
        result = validator.validate_input(args.test_input)
        print(f"Input validation result: {result}")
    
    if args.test_rate_limit:
        rate_limiter = RateLimiter(requests_per_minute=5)
        for i in range(10):
            allowed = rate_limiter.is_allowed(f"test_user_{i}")
            print(f"Request {i+1}: {'Allowed' if allowed else 'Blocked'}")
    
    if args.generate_report:
        monitor = APISecurityMonitor()
        # Add some test events
        monitor.log_security_event('test_event', {'test': True})
        summary = monitor.get_security_summary()
        print(f"Security summary: {summary}")
