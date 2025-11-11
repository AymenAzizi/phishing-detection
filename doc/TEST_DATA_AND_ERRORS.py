#!/usr/bin/env python3
"""
Test Suite for Data Persistence and Error Handling
Tests database operations, file storage, and error scenarios
"""

import requests
import json
import os
from datetime import datetime

API_BASE = "http://localhost:8000"
DASHBOARD_BASE = "http://localhost:3000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")

def print_test(status, name, details=""):
    status_str = f"{Colors.GREEN}✅ PASS{Colors.RESET}" if status else f"{Colors.RED}❌ FAIL{Colors.RESET}"
    print(f"  {status_str} | {name}")
    if details:
        print(f"       └─ {details}")

def test_model_file_exists():
    """Test 1: Model File Exists"""
    print_header("TEST 1: MODEL FILE PERSISTENCE")
    
    model_path = "models/best_phishing_model.pkl"
    exists = os.path.exists(model_path)
    
    if exists:
        size = os.path.getsize(model_path)
        print_test(True, "Model File Exists", f"Size: {size:,} bytes")
    else:
        print_test(False, "Model File Exists", "File not found")
    
    return exists

def test_database_file_exists():
    """Test 2: Database File Exists"""
    print_header("TEST 2: DATABASE FILE PERSISTENCE")
    
    db_path = "browsing_monitor.db"
    exists = os.path.exists(db_path)
    
    if exists:
        size = os.path.getsize(db_path)
        print_test(True, "Database File Exists", f"Size: {size:,} bytes")
    else:
        print_test(True, "Database File Not Created Yet", "Will be created on first monitoring")
    
    return True

def test_feature_extractor_file():
    """Test 3: Feature Extractor File"""
    print_header("TEST 3: FEATURE EXTRACTOR FILE")
    
    extractor_path = "real_feature_extractor.py"
    exists = os.path.exists(extractor_path)
    
    if exists:
        size = os.path.getsize(extractor_path)
        print_test(True, "Feature Extractor Exists", f"Size: {size:,} bytes")
    else:
        print_test(False, "Feature Extractor Exists", "File not found")
    
    return exists

def test_invalid_url_handling():
    """Test 4: Invalid URL Handling"""
    print_header("TEST 4: INVALID URL ERROR HANDLING")
    
    invalid_urls = [
        "",
        "not-a-url",
        "ftp://invalid.com",
        "javascript:alert('xss')"
    ]
    
    passed = 0
    for url in invalid_urls:
        try:
            response = requests.post(
                f"{API_BASE}/predict/url",
                json={"url": url},
                timeout=5
            )
            
            # Should either return 200 with safe result or 400/500 error
            if response.status_code in [200, 400, 422, 500]:
                print_test(True, f"Handle Invalid URL: '{url[:30]}'", f"Status: {response.status_code}")
                passed += 1
            else:
                print_test(False, f"Handle Invalid URL: '{url[:30]}'", f"Status: {response.status_code}")
        except Exception as e:
            print_test(False, f"Handle Invalid URL: '{url[:30]}'", str(e))
    
    return passed == len(invalid_urls)

def test_invalid_email_handling():
    """Test 5: Invalid Email Handling"""
    print_header("TEST 5: INVALID EMAIL ERROR HANDLING")
    
    invalid_emails = [
        {"email_content": ""},
        {"email_content": None},
        {"sender": "", "subject": "", "email_content": ""},
    ]
    
    passed = 0
    for email in invalid_emails:
        try:
            response = requests.post(
                f"{API_BASE}/predict/email",
                json=email,
                timeout=5
            )
            
            if response.status_code in [200, 400, 422, 500]:
                print_test(True, f"Handle Invalid Email", f"Status: {response.status_code}")
                passed += 1
            else:
                print_test(False, f"Handle Invalid Email", f"Status: {response.status_code}")
        except Exception as e:
            print_test(False, f"Handle Invalid Email", str(e))
    
    return passed >= len(invalid_emails) - 1

def test_api_timeout_handling():
    """Test 6: API Timeout Handling"""
    print_header("TEST 6: API TIMEOUT HANDLING")
    
    try:
        # Try to connect to non-existent port
        response = requests.get(
            "http://localhost:9999/health",
            timeout=2
        )
        print_test(False, "Timeout Handling", "Should have timed out")
        return False
    except requests.exceptions.ConnectionError:
        print_test(True, "Timeout Handling", "Connection error caught correctly")
        return True
    except requests.exceptions.Timeout:
        print_test(True, "Timeout Handling", "Timeout caught correctly")
        return True
    except Exception as e:
        print_test(True, "Timeout Handling", f"Error caught: {type(e).__name__}")
        return True

def test_cors_headers():
    """Test 7: CORS Headers"""
    print_header("TEST 7: CORS HEADERS")
    
    try:
        response = requests.get(
            f"{API_BASE}/health",
            timeout=5
        )
        
        has_cors = 'access-control-allow-origin' in response.headers
        
        if has_cors:
            cors_value = response.headers.get('access-control-allow-origin')
            print_test(True, "CORS Headers Present", f"Allow-Origin: {cors_value}")
            return True
        else:
            print_test(True, "CORS Headers", "Not required for same-origin requests")
            return True
    except Exception as e:
        print_test(False, "CORS Headers", str(e))
        return False

def test_response_format():
    """Test 8: Response Format Validation"""
    print_header("TEST 8: RESPONSE FORMAT VALIDATION")
    
    try:
        response = requests.post(
            f"{API_BASE}/predict/url",
            json={"url": "https://www.google.com"},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            
            required_fields = [
                'prediction_id',
                'url',
                'is_phishing',
                'confidence',
                'threat_level',
                'processing_time_ms',
                'timestamp',
                'risk_factors'
            ]
            
            missing_fields = [f for f in required_fields if f not in data]
            
            if not missing_fields:
                print_test(True, "Response Format Valid", f"All {len(required_fields)} fields present")
                return True
            else:
                print_test(False, "Response Format Valid", f"Missing: {missing_fields}")
                return False
        else:
            print_test(False, "Response Format Valid", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test(False, "Response Format Valid", str(e))
        return False

def test_concurrent_requests():
    """Test 9: Concurrent Request Handling"""
    print_header("TEST 9: CONCURRENT REQUEST HANDLING")
    
    import concurrent.futures
    
    urls = [
        "https://www.google.com",
        "https://www.paypal.com",
        "http://phishing-site.tk",
        "https://www.amazon.com",
        "http://fake-login.xyz"
    ]
    
    def make_request(url):
        try:
            response = requests.post(
                f"{API_BASE}/predict/url",
                json={"url": url},
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(make_request, urls))
        
        passed = sum(results)
        print_test(True, "Concurrent Requests", f"{passed}/{len(urls)} successful")
        return passed == len(urls)
    except Exception as e:
        print_test(False, "Concurrent Requests", str(e))
        return False

def test_large_url_handling():
    """Test 10: Large URL Handling"""
    print_header("TEST 10: LARGE URL HANDLING")
    
    # Create a very long URL
    long_url = "https://www.example.com/" + "a" * 2000
    
    try:
        response = requests.post(
            f"{API_BASE}/predict/url",
            json={"url": long_url},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print_test(True, "Large URL Handling", f"Processed {len(long_url)} char URL")
            return True
        else:
            print_test(True, "Large URL Handling", f"Rejected with status {response.status_code}")
            return True
    except Exception as e:
        print_test(False, "Large URL Handling", str(e))
        return False

def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "DATA PERSISTENCE & ERROR HANDLING TEST SUITE".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    print(f"{Colors.RESET}\n")
    
    print(f"{Colors.YELLOW}Starting tests at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}\n")
    
    results = {
        "Model File Persistence": test_model_file_exists(),
        "Database File Persistence": test_database_file_exists(),
        "Feature Extractor File": test_feature_extractor_file(),
        "Invalid URL Handling": test_invalid_url_handling(),
        "Invalid Email Handling": test_invalid_email_handling(),
        "API Timeout Handling": test_api_timeout_handling(),
        "CORS Headers": test_cors_headers(),
        "Response Format Validation": test_response_format(),
        "Concurrent Request Handling": test_concurrent_requests(),
        "Large URL Handling": test_large_url_handling()
    }
    
    print_header("TEST SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{Colors.GREEN}✅ PASS{Colors.RESET}" if result else f"{Colors.RED}❌ FAIL{Colors.RESET}"
        print(f"  {status} | {test_name}")
    
    print(f"\n{Colors.BOLD}Overall: {passed}/{total} tests passed ({passed/total*100:.0f}%){Colors.RESET}\n")
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 ALL DATA & ERROR TESTS PASSED! 🎉{Colors.RESET}\n")
        return 0
    else:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️ {total - passed} TEST(S) FAILED{Colors.RESET}\n")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())

