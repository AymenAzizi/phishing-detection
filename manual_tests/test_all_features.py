#!/usr/bin/env python3
"""
Test script to verify both OLD and NEW features work together
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_old_phishing_detection():
    """Test OLD phishing detection feature"""
    print_section("🤖 TESTING OLD FEATURE: ML-Based Phishing Detection")
    
    try:
        # Test URL prediction
        response = requests.post(
            f"{BASE_URL}/api/v1/predict",
            json={"url": "https://www.google.com", "include_features": False},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ OLD FEATURE WORKS: Phishing Detection")
            print(f"   URL: {data.get('url', 'N/A')}")
            print(f"   Is Phishing: {data.get('is_phishing', 'N/A')}")
            print(f"   Confidence: {data.get('confidence', 0):.2%}")
            print(f"   Threat Level: {data.get('threat_level', 'N/A')}")
            return True
        else:
            print(f"❌ OLD FEATURE FAILED: Status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ OLD FEATURE ERROR: {e}")
        return False

def test_old_email_detection():
    """Test OLD email phishing detection"""
    print_section("📧 TESTING OLD FEATURE: Email Phishing Detection")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/email",
            json={
                "email_content": "Click here to verify your account",
                "sender": "noreply@example.com",
                "subject": "Urgent: Verify your account"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ OLD FEATURE WORKS: Email Detection")
            print(f"   Is Phishing: {data.get('is_phishing', 'N/A')}")
            print(f"   Confidence: {data.get('confidence', 0):.2%}")
            return True
        else:
            print(f"❌ OLD FEATURE FAILED: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ OLD FEATURE ERROR: {e}")
        return False

def test_new_comprehensive_scan():
    """Test NEW comprehensive security scan"""
    print_section("🔒 TESTING NEW FEATURE: Comprehensive Security Scan")
    
    try:
        print("⏳ Running comprehensive scan (this may take 10-15 seconds)...")
        response = requests.post(
            f"{BASE_URL}/api/v1/scan/comprehensive",
            json={"url": "https://www.google.com"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ NEW FEATURE WORKS: Comprehensive Scan")
            print(f"   Overall Score: {data.get('overall_score', 0)}/100")
            print(f"   Grade: {data.get('grade', 'N/A')}")
            print(f"   Security Level: {data.get('security_level', 'N/A')}")
            print(f"   Total Issues: {data.get('total_issues', 0)}")
            
            issues = data.get('issues_by_severity', {})
            print(f"   Issues by Severity:")
            print(f"     - Critical: {issues.get('critical', 0)}")
            print(f"     - High: {issues.get('high', 0)}")
            print(f"     - Medium: {issues.get('medium', 0)}")
            print(f"     - Low: {issues.get('low', 0)}")
            
            scores = data.get('scanner_scores', {})
            print(f"   Scanner Scores:")
            for scanner, score in scores.items():
                print(f"     - {scanner.upper()}: {score}/100")
            
            return True
        else:
            print(f"❌ NEW FEATURE FAILED: Status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ NEW FEATURE ERROR: {e}")
        return False

def test_new_quick_scan():
    """Test NEW quick scan"""
    print_section("⚡ TESTING NEW FEATURE: Quick Scan (SSL + Headers)")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/scan/quick",
            json={"url": "https://www.google.com"},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ NEW FEATURE WORKS: Quick Scan")
            print(f"   Overall Score: {data.get('overall_score', 0)}/100")
            print(f"   Grade: {data.get('grade', 'N/A')}")
            return True
        else:
            print(f"❌ NEW FEATURE FAILED: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ NEW FEATURE ERROR: {e}")
        return False

def test_new_ssl_scan():
    """Test NEW SSL/TLS scan"""
    print_section("🔐 TESTING NEW FEATURE: SSL/TLS Security Scan")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/scan/ssl",
            json={"url": "https://www.google.com"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', {})
            print(f"✅ NEW FEATURE WORKS: SSL/TLS Scan")
            print(f"   Score: {results.get('score', 0)}/100")
            print(f"   Grade: {results.get('grade', 'N/A')}")
            print(f"   Issues: {len(results.get('issues', []))}")
            return True
        else:
            print(f"❌ NEW FEATURE FAILED: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ NEW FEATURE ERROR: {e}")
        return False

def test_health_check():
    """Test health check endpoint"""
    print_section("🏥 TESTING: Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ HEALTH CHECK PASSED")
            print(f"   Status: {data.get('status', 'N/A')}")
            print(f"   Model Loaded: {data.get('model_loaded', False)}")
            return True
        else:
            print(f"❌ HEALTH CHECK FAILED: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ HEALTH CHECK ERROR: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("  🔒 DevSecScan - Feature Verification Test")
    print("  Testing OLD phishing detection + NEW security scanning features")
    print("="*70)
    
    # Wait for API to be ready
    print("\n⏳ Waiting for API to be ready...")
    for i in range(10):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print("✅ API is ready!")
                break
        except:
            pass
        time.sleep(1)
        print(f"   Attempt {i+1}/10...")
    else:
        print("❌ API not responding. Please start it with: python real_api.py")
        return
    
    results = {}
    
    # Test OLD features
    results['health_check'] = test_health_check()
    results['old_phishing'] = test_old_phishing_detection()
    results['old_email'] = test_old_email_detection()
    
    # Test NEW features
    results['new_ssl'] = test_new_ssl_scan()
    results['new_quick'] = test_new_quick_scan()
    results['new_comprehensive'] = test_new_comprehensive_scan()
    
    # Summary
    print_section("📊 FINAL SUMMARY")
    
    print("\n🤖 OLD FEATURES (Phishing Detection):")
    print(f"   ✅ Health Check: {'PASS' if results['health_check'] else 'FAIL'}")
    print(f"   ✅ URL Phishing Detection: {'PASS' if results['old_phishing'] else 'FAIL'}")
    print(f"   ✅ Email Phishing Detection: {'PASS' if results['old_email'] else 'FAIL'}")
    
    print("\n🔒 NEW FEATURES (Security Scanning):")
    print(f"   ✅ SSL/TLS Scanner: {'PASS' if results['new_ssl'] else 'FAIL'}")
    print(f"   ✅ Quick Scan: {'PASS' if results['new_quick'] else 'FAIL'}")
    print(f"   ✅ Comprehensive Scan: {'PASS' if results['new_comprehensive'] else 'FAIL'}")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    print(f"\n📈 OVERALL RESULTS: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 SUCCESS! All OLD and NEW features are working together!")
        print("   ✅ Your project has BOTH phishing detection AND security scanning!")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Check the errors above.")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()

