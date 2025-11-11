#!/usr/bin/env python3
"""
Comprehensive Test Suite for Phishing Detection Project
Tests all functionality: API, Dashboard, Extension, Monitoring, ML Model
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
API_BASE = "http://localhost:8000"
DASHBOARD_BASE = "http://localhost:3000"

# Test URLs
TEST_URLS = {
    "safe": [
        "https://www.google.com",
        "https://www.paypal.com",
        "https://www.amazon.com",
        "https://www.github.com",
        "https://www.wikipedia.org"
    ],
    "suspicious": [
        "http://paypal-verify.tk",
        "http://amazon-login.xyz",
        "http://google-account-verify.com",
        "http://verify-account-now.tk",
        "http://secure-login-verify.xyz"
    ]
}

TEST_EMAILS = {
    "safe": [
        {"sender": "support@paypal.com", "subject": "Your Account", "email_content": "Hello, your account is secure"},
        {"sender": "noreply@amazon.com", "subject": "Order Confirmation", "email_content": "Your order has been confirmed"}
    ],
    "phishing": [
        {"sender": "paypal@verify.com", "subject": "Verify Your Account", "email_content": "Click here to verify your account immediately"},
        {"sender": "amazon@secure.tk", "subject": "Urgent: Confirm Your Identity", "email_content": "Your account has been compromised. Click here to verify"}
    ]
}

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

def print_test(name, status, details=""):
    status_str = f"{Colors.GREEN}✅ PASS{Colors.RESET}" if status else f"{Colors.RED}❌ FAIL{Colors.RESET}"
    print(f"  {status_str} | {name}")
    if details:
        print(f"       └─ {details}")

def test_api_health():
    """Test 1: Backend API Health Check"""
    print_header("TEST 1: BACKEND API HEALTH CHECK")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_test(True, "API Health Check", f"Status: {data.get('status')}")
            print_test(True, "Model Loaded", f"Model: {data.get('model_loaded')}")
            print_test(True, "Feature Extractor", f"Ready: {data.get('feature_extractor_ready')}")
            return True
        else:
            print_test(False, "API Health Check", f"Status Code: {response.status_code}")
            return False
    except Exception as e:
        print_test(False, "API Health Check", str(e))
        return False

def test_url_predictions():
    """Test 2: URL Prediction Endpoint"""
    print_header("TEST 2: URL PREDICTION ENDPOINT")
    results = {"safe": 0, "suspicious": 0}
    
    print(f"{Colors.YELLOW}Testing Safe URLs:{Colors.RESET}")
    for url in TEST_URLS["safe"]:
        try:
            response = requests.post(
                f"{API_BASE}/predict/url",
                json={"url": url},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                is_phishing = data.get("is_phishing", False)
                confidence = data.get("confidence", 0)
                status = "✅ Safe" if not is_phishing else "⚠️ Flagged"
                print(f"    {status} | {url} (Confidence: {confidence:.2%})")
                if not is_phishing:
                    results["safe"] += 1
        except Exception as e:
            print(f"    ❌ Error | {url} - {str(e)}")
    
    print(f"\n{Colors.YELLOW}Testing Suspicious URLs:{Colors.RESET}")
    for url in TEST_URLS["suspicious"]:
        try:
            response = requests.post(
                f"{API_BASE}/predict/url",
                json={"url": url},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                is_phishing = data.get("is_phishing", False)
                confidence = data.get("confidence", 0)
                status = "🚨 Phishing" if is_phishing else "⚠️ Missed"
                print(f"    {status} | {url} (Confidence: {confidence:.2%})")
                if is_phishing:
                    results["suspicious"] += 1
        except Exception as e:
            print(f"    ❌ Error | {url} - {str(e)}")
    
    safe_accuracy = results["safe"] / len(TEST_URLS["safe"]) * 100
    phishing_accuracy = results["suspicious"] / len(TEST_URLS["suspicious"]) * 100
    print(f"\n  Safe URL Detection: {safe_accuracy:.0f}% ({results['safe']}/{len(TEST_URLS['safe'])})")
    print(f"  Phishing Detection: {phishing_accuracy:.0f}% ({results['suspicious']}/{len(TEST_URLS['suspicious'])})")
    
    return safe_accuracy >= 80 and phishing_accuracy >= 80

def test_email_predictions():
    """Test 3: Email Prediction Endpoint"""
    print_header("TEST 3: EMAIL PREDICTION ENDPOINT")
    results = {"safe": 0, "phishing": 0}
    
    print(f"{Colors.YELLOW}Testing Safe Emails:{Colors.RESET}")
    for email in TEST_EMAILS["safe"]:
        try:
            response = requests.post(
                f"{API_BASE}/predict/email",
                json=email,
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                is_phishing = data.get("is_phishing", False)
                confidence = data.get("confidence", 0)
                status = "✅ Safe" if not is_phishing else "⚠️ Flagged"
                print(f"    {status} | From: {email['sender']} (Confidence: {confidence:.2%})")
                if not is_phishing:
                    results["safe"] += 1
        except Exception as e:
            print(f"    ❌ Error | {email['sender']} - {str(e)}")
    
    print(f"\n{Colors.YELLOW}Testing Phishing Emails:{Colors.RESET}")
    for email in TEST_EMAILS["phishing"]:
        try:
            response = requests.post(
                f"{API_BASE}/predict/email",
                json=email,
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                is_phishing = data.get("is_phishing", False)
                confidence = data.get("confidence", 0)
                status = "🚨 Phishing" if is_phishing else "⚠️ Missed"
                print(f"    {status} | From: {email['sender']} (Confidence: {confidence:.2%})")
                if is_phishing:
                    results["phishing"] += 1
        except Exception as e:
            print(f"    ❌ Error | {email['sender']} - {str(e)}")
    
    safe_accuracy = results["safe"] / len(TEST_EMAILS["safe"]) * 100
    phishing_accuracy = results["phishing"] / len(TEST_EMAILS["phishing"]) * 100
    print(f"\n  Safe Email Detection: {safe_accuracy:.0f}% ({results['safe']}/{len(TEST_EMAILS['safe'])})")
    print(f"  Phishing Email Detection: {phishing_accuracy:.0f}% ({results['phishing']}/{len(TEST_EMAILS['phishing'])})")
    
    return safe_accuracy >= 80 and phishing_accuracy >= 80

def test_dashboard_endpoints():
    """Test 4: Dashboard Server Endpoints"""
    print_header("TEST 4: DASHBOARD SERVER ENDPOINTS")
    
    endpoints = [
        ("/", "Dashboard Home"),
        ("/api/system-status", "System Status"),
        ("/api/metrics", "Metrics"),
        ("/api/recent-predictions", "Recent Predictions"),
        ("/api/statistics", "Statistics"),
        ("/api/monitoring/status", "Monitoring Status"),
        ("/api/monitoring/events", "Monitoring Events"),
        ("/api/monitoring/summary", "Monitoring Summary")
    ]
    
    passed = 0
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{DASHBOARD_BASE}{endpoint}", timeout=5)
            if response.status_code == 200:
                print_test(True, f"GET {endpoint}", name)
                passed += 1
            else:
                print_test(False, f"GET {endpoint}", f"Status: {response.status_code}")
        except Exception as e:
            print_test(False, f"GET {endpoint}", str(e))
    
    print(f"\n  Dashboard Endpoints: {passed}/{len(endpoints)} passed")
    return passed == len(endpoints)

def test_monitoring_system():
    """Test 5: Real-Time Monitoring System"""
    print_header("TEST 5: REAL-TIME MONITORING SYSTEM")
    
    try:
        # Test monitoring status
        response = requests.get(f"{DASHBOARD_BASE}/api/monitoring/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_test(True, "Get Monitoring Status", f"Status: {data.get('status')}")
        
        # Test start monitoring
        response = requests.post(f"{DASHBOARD_BASE}/api/monitoring/start", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_test(True, "Start Monitoring", data.get('message', 'Started'))
            time.sleep(2)
        
        # Test get events
        response = requests.get(f"{DASHBOARD_BASE}/api/monitoring/events", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_test(True, "Get Monitoring Events", f"Events: {data.get('count', 0)}")
        
        # Test stop monitoring
        response = requests.post(f"{DASHBOARD_BASE}/api/monitoring/stop", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_test(True, "Stop Monitoring", data.get('message', 'Stopped'))
        
        return True
    except Exception as e:
        print_test(False, "Monitoring System", str(e))
        return False

def test_model_info():
    """Test 6: Model Information Endpoint"""
    print_header("TEST 6: MODEL INFORMATION")
    
    try:
        response = requests.get(f"{API_BASE}/model/info", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_test(True, "Get Model Info", f"Model Type: {data.get('model_type')}")
            print_test(True, "Feature Count", f"Features: {data.get('feature_count')}")
            print_test(True, "Model Status", f"Status: {data.get('status')}")
            return True
        else:
            print_test(False, "Get Model Info", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test(False, "Get Model Info", str(e))
        return False

def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "COMPREHENSIVE PROJECT FUNCTIONALITY TEST".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    print(f"{Colors.RESET}\n")
    
    print(f"{Colors.YELLOW}Starting tests at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}\n")
    
    results = {
        "API Health": test_api_health(),
        "URL Predictions": test_url_predictions(),
        "Email Predictions": test_email_predictions(),
        "Dashboard Endpoints": test_dashboard_endpoints(),
        "Monitoring System": test_monitoring_system(),
        "Model Info": test_model_info()
    }
    
    print_header("TEST SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{Colors.GREEN}✅ PASS{Colors.RESET}" if result else f"{Colors.RED}❌ FAIL{Colors.RESET}"
        print(f"  {status} | {test_name}")
    
    print(f"\n{Colors.BOLD}Overall: {passed}/{total} tests passed ({passed/total*100:.0f}%){Colors.RESET}\n")
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! 🎉{Colors.RESET}\n")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}⚠️ SOME TESTS FAILED{Colors.RESET}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())

