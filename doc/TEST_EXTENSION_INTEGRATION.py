#!/usr/bin/env python3
"""
Test Suite for Browser Extension Integration
Tests extension event submission, dashboard integration, and real-time monitoring
"""

import requests
import json
import time
from datetime import datetime

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

def test_extension_event_submission():
    """Test 1: Extension Event Submission"""
    print_header("TEST 1: EXTENSION EVENT SUBMISSION")
    
    # Simulate extension sending an event
    event = {
        "timestamp": datetime.now().isoformat(),
        "url": "https://www.google.com",
        "domain": "google.com",
        "is_phishing": False,
        "confidence": 0.95,
        "threat_level": "Low",
        "risk_factors": [],
        "browser": "extension",
        "processing_time": 100
    }
    
    try:
        response = requests.post(
            f"{DASHBOARD_BASE}/api/extension/event",
            json=event,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print_test(True, "Submit Safe URL Event", data.get('message'))
            return True
        else:
            print_test(False, "Submit Safe URL Event", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test(False, "Submit Safe URL Event", str(e))
        return False

def test_phishing_event_submission():
    """Test 2: Phishing Event Submission"""
    print_header("TEST 2: PHISHING EVENT SUBMISSION")
    
    # Simulate extension detecting phishing
    event = {
        "timestamp": datetime.now().isoformat(),
        "url": "http://paypal-verify.tk",
        "domain": "paypal-verify.tk",
        "is_phishing": True,
        "confidence": 0.99,
        "threat_level": "Critical",
        "risk_factors": ["Suspicious domain", "TinyURL detected"],
        "browser": "extension",
        "processing_time": 150
    }
    
    try:
        response = requests.post(
            f"{DASHBOARD_BASE}/api/extension/event",
            json=event,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print_test(True, "Submit Phishing Event", data.get('message'))
            return True
        else:
            print_test(False, "Submit Phishing Event", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test(False, "Submit Phishing Event", str(e))
        return False

def test_get_extension_events():
    """Test 3: Get Extension Events"""
    print_header("TEST 3: GET EXTENSION EVENTS")
    
    try:
        response = requests.get(
            f"{DASHBOARD_BASE}/api/extension/events",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            event_count = len(data.get('events', []))
            print_test(True, "Get Extension Events", f"Retrieved {event_count} events")
            
            # Print recent events
            if event_count > 0:
                print(f"\n  {Colors.YELLOW}Recent Events:{Colors.RESET}")
                for event in data.get('events', [])[:3]:
                    status = "🚨 Phishing" if event.get('is_phishing') else "✅ Safe"
                    confidence = event.get('confidence', 0)
                    try:
                        if isinstance(confidence, str):
                            # Remove % if present
                            confidence = confidence.rstrip('%')
                            confidence = float(confidence) / 100
                        else:
                            confidence = float(confidence)
                        conf_str = f"{confidence:.0%}"
                    except:
                        conf_str = str(confidence)
                    print(f"    {status} | {event.get('url')} ({conf_str})")
            
            return True
        else:
            print_test(False, "Get Extension Events", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test(False, "Get Extension Events", str(e))
        return False

def test_clear_history():
    """Test 4: Clear History"""
    print_header("TEST 4: CLEAR HISTORY")
    
    try:
        response = requests.post(
            f"{DASHBOARD_BASE}/api/clear-history",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print_test(True, "Clear History", data.get('message'))
            return True
        else:
            print_test(False, "Clear History", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test(False, "Clear History", str(e))
        return False

def test_monitoring_start_stop():
    """Test 5: Monitoring Start/Stop"""
    print_header("TEST 5: MONITORING START/STOP")
    
    try:
        # Start monitoring
        response = requests.post(
            f"{DASHBOARD_BASE}/api/monitoring/start",
            timeout=5
        )
        
        if response.status_code == 200:
            print_test(True, "Start Monitoring", response.json().get('message'))
        else:
            print_test(False, "Start Monitoring", f"Status: {response.status_code}")
            return False
        
        time.sleep(1)
        
        # Check status
        response = requests.get(
            f"{DASHBOARD_BASE}/api/monitoring/status",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print_test(True, "Check Monitoring Status", f"Status: {data.get('status')}")
        else:
            print_test(False, "Check Monitoring Status", f"Status: {response.status_code}")
            return False
        
        # Stop monitoring
        response = requests.post(
            f"{DASHBOARD_BASE}/api/monitoring/stop",
            timeout=5
        )
        
        if response.status_code == 200:
            print_test(True, "Stop Monitoring", response.json().get('message'))
            return True
        else:
            print_test(False, "Stop Monitoring", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test(False, "Monitoring Start/Stop", str(e))
        return False

def test_monitoring_events():
    """Test 6: Get Monitoring Events"""
    print_header("TEST 6: GET MONITORING EVENTS")
    
    try:
        response = requests.get(
            f"{DASHBOARD_BASE}/api/monitoring/events",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            event_count = data.get('count', 0)
            print_test(True, "Get Monitoring Events", f"Retrieved {event_count} events")
            return True
        else:
            print_test(False, "Get Monitoring Events", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test(False, "Get Monitoring Events", str(e))
        return False

def test_monitoring_summary():
    """Test 7: Get Monitoring Summary"""
    print_header("TEST 7: GET MONITORING SUMMARY")
    
    try:
        response = requests.get(
            f"{DASHBOARD_BASE}/api/monitoring/summary",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print_test(True, "Get Monitoring Summary", "Summary retrieved")
            
            # Print summary stats
            print(f"\n  {Colors.YELLOW}Threat Summary:{Colors.RESET}")
            print(f"    Total Events: {data.get('total_events', 0)}")
            print(f"    Phishing Detected: {data.get('phishing_detected', 0)}")
            print(f"    Safe Sites: {data.get('safe_sites', 0)}")
            print(f"    Avg Confidence: {data.get('avg_confidence', 0):.2%}")
            
            return True
        else:
            print_test(False, "Get Monitoring Summary", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test(False, "Get Monitoring Summary", str(e))
        return False

def test_dashboard_loading():
    """Test 8: Dashboard Page Loading"""
    print_header("TEST 8: DASHBOARD PAGE LOADING")
    
    try:
        response = requests.get(
            f"{DASHBOARD_BASE}/",
            timeout=5
        )
        
        if response.status_code == 200:
            # Check if HTML contains key elements
            html = response.text.lower()
            checks = {
                "Dashboard Title": "phishing" in html or "detection" in html,
                "System Status Section": "system" in html or "status" in html,
                "Real-time Monitoring": "monitoring" in html or "real" in html,
                "Test Prediction": "test" in html or "prediction" in html
            }
            
            all_passed = True
            for check_name, result in checks.items():
                print_test(result, f"Dashboard - {check_name}")
                all_passed = all_passed and result
            
            return all_passed
        else:
            print_test(False, "Dashboard Loading", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test(False, "Dashboard Loading", str(e))
        return False

def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "EXTENSION & INTEGRATION TEST SUITE".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    print(f"{Colors.RESET}\n")
    
    print(f"{Colors.YELLOW}Starting tests at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}\n")
    
    results = {
        "Extension Event Submission": test_extension_event_submission(),
        "Phishing Event Submission": test_phishing_event_submission(),
        "Get Extension Events": test_get_extension_events(),
        "Clear History": test_clear_history(),
        "Monitoring Start/Stop": test_monitoring_start_stop(),
        "Monitoring Events": test_monitoring_events(),
        "Monitoring Summary": test_monitoring_summary(),
        "Dashboard Loading": test_dashboard_loading()
    }
    
    print_header("TEST SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{Colors.GREEN}✅ PASS{Colors.RESET}" if result else f"{Colors.RED}❌ FAIL{Colors.RESET}"
        print(f"  {status} | {test_name}")
    
    print(f"\n{Colors.BOLD}Overall: {passed}/{total} tests passed ({passed/total*100:.0f}%){Colors.RESET}\n")
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 ALL EXTENSION TESTS PASSED! 🎉{Colors.RESET}\n")
        return 0
    else:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️ {total - passed} TEST(S) FAILED{Colors.RESET}\n")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())

