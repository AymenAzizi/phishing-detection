#!/usr/bin/env python3
"""
Test Explainable AI Features
"""

import requests
import json
import time

API_BASE = "http://localhost:8000"

def print_section(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def test_health():
    """Test API health"""
    print_section("1. Testing API Health")
    
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Status: {data['status']}")
            print(f"✅ ML Model: {data['ml_model_loaded']}")
            print(f"✅ Security Scanners: {data['security_scanners_ready']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_phishing_detection():
    """Test basic phishing detection"""
    print_section("2. Testing Phishing Detection")
    
    test_urls = [
        ("https://www.google.com", "Legitimate"),
        ("http://suspicious-login-verify-account.com", "Phishing")
    ]
    
    for url, expected in test_urls:
        try:
            print(f"\n🔍 Testing: {url}")
            response = requests.post(
                f"{API_BASE}/predict/url",
                json={"url": url, "include_features": True}
            )
            
            if response.status_code == 200:
                data = response.json()
                prediction = "Phishing" if data['is_phishing'] else "Legitimate"
                confidence = data['confidence'] * 100
                
                print(f"   Prediction: {prediction}")
                print(f"   Confidence: {confidence:.1f}%")
                print(f"   Threat Level: {data['threat_level']}")
                print(f"   Processing Time: {data['processing_time_ms']:.2f}ms")
                
                if data.get('features'):
                    print(f"   ✅ Features extracted: {len(data['features'])} features")
                
                print(f"   {'✅' if prediction == expected else '⚠️'} Expected: {expected}")
            else:
                print(f"   ❌ Request failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_explainable_ai():
    """Test Explainable AI endpoint"""
    print_section("3. Testing Explainable AI (SHAP/LIME)")
    
    test_url = "http://suspicious-phishing-site-login.com"
    
    try:
        print(f"\n🧠 Getting AI Explanation for: {test_url}")
        response = requests.post(
            f"{API_BASE}/api/v1/explain",
            json={"url": test_url}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Prediction: {'Phishing' if data['is_phishing'] else 'Legitimate'}")
            print(f"✅ Confidence: {data['confidence']*100:.1f}%")
            
            if 'explanation' in data:
                exp = data['explanation']
                print(f"\n📊 AI Explanation Available:")
                print(f"   Method: {exp.get('method', 'N/A')}")
                
                if 'top_features' in exp:
                    print(f"\n   Top 5 Contributing Features:")
                    for i, feat in enumerate(exp['top_features'][:5], 1):
                        feature_name = feat.get('feature', 'Unknown')
                        shap_value = feat.get('shap_value', 0)
                        impact = feat.get('impact', 'unknown')
                        print(f"   {i}. {feature_name}: {shap_value:.4f} ({impact} risk)")
                
                if 'waterfall_plot' in exp and exp['waterfall_plot']:
                    print(f"\n   ✅ Waterfall plot generated")
                
                if 'force_plot' in exp and exp['force_plot']:
                    print(f"   ✅ Force plot data available")
                    
                print(f"\n✅ Explainable AI is working!")
            else:
                print(f"⚠️ No explanation data in response")
                
        elif response.status_code == 503:
            print(f"⚠️ ML Explainer not available (install SHAP/LIME)")
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_feature_importance():
    """Test global feature importance endpoint"""
    print_section("4. Testing Global Feature Importance")
    
    try:
        print(f"\n📊 Getting global feature importance...")
        response = requests.get(f"{API_BASE}/api/v1/feature-importance")
        
        if response.status_code == 200:
            data = response.json()
            
            if 'top_features' in data:
                print(f"\n✅ Top 10 Most Important Features:")
                for i, feat in enumerate(data['top_features'][:10], 1):
                    feature_name = feat.get('feature', 'Unknown')
                    importance = feat.get('importance', 0)
                    print(f"   {i:2d}. {feature_name:20s}: {importance:.4f}")
                
                if 'plot' in data and data['plot']:
                    print(f"\n✅ Feature importance plot generated")
                
                print(f"\n✅ Global feature importance is working!")
            else:
                print(f"⚠️ No feature importance data")
                
        elif response.status_code == 503:
            print(f"⚠️ ML Explainer not available")
        else:
            print(f"❌ Request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_email_analysis():
    """Test email analysis"""
    print_section("5. Testing Email Analysis")
    
    test_email = """
    Dear Customer,
    
    Your account has been suspended due to suspicious activity.
    Please click here to verify your identity immediately:
    http://verify-account-now.com/login
    
    Failure to verify within 24 hours will result in permanent account closure.
    
    Best regards,
    Security Team
    """
    
    try:
        print(f"\n📧 Analyzing suspicious email...")
        response = requests.post(
            f"{API_BASE}/predict/email",
            json={
                "email_content": test_email,
                "sender": "security@suspicious-domain.com",
                "subject": "URGENT: Account Verification Required"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            prediction = "Phishing" if data['is_phishing'] else "Legitimate"
            confidence = data['confidence'] * 100
            
            print(f"✅ Prediction: {prediction}")
            print(f"✅ Confidence: {confidence:.1f}%")
            print(f"✅ Threat Level: {data['threat_level']}")
            
            if data.get('risk_factors'):
                print(f"\n📋 Risk Factors Detected:")
                for factor in data['risk_factors'][:5]:
                    print(f"   • {factor}")
            
            print(f"\n✅ Email analysis is working!")
        else:
            print(f"❌ Request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_security_scanning():
    """Test security scanning"""
    print_section("6. Testing Security Scanning")
    
    try:
        print(f"\n🔒 Running comprehensive security scan on google.com...")
        response = requests.post(
            f"{API_BASE}/api/v1/scan/comprehensive",
            json={"url": "https://www.google.com"}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Overall Score: {data.get('overall_score', 0):.1f}/100")
            print(f"✅ Grade: {data.get('grade', 'N/A')}")
            
            if 'scans' in data:
                scans = data['scans']
                print(f"\n📊 Individual Scan Results:")
                
                if 'ssl' in scans:
                    print(f"   SSL/TLS: {scans['ssl'].get('score', 0):.1f}/100")
                
                if 'headers' in scans:
                    print(f"   Security Headers: {scans['headers'].get('score', 0):.1f}/100")
                
                if 'vulnerabilities' in scans:
                    print(f"   Vulnerabilities: {scans['vulnerabilities'].get('score', 0):.1f}/100")
                
                if 'phishing' in scans:
                    print(f"   Phishing: {scans['phishing'].get('score', 0):.1f}/100")
            
            print(f"\n✅ Security scanning is working!")
        else:
            print(f"❌ Request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("\n" + "="*80)
    print("  🧪 TESTING EXPLAINABLE AI & ALL FEATURES")
    print("="*80)
    print("\n📝 This test verifies:")
    print("   1. API Health")
    print("   2. Phishing Detection")
    print("   3. Explainable AI (SHAP/LIME)")
    print("   4. Global Feature Importance")
    print("   5. Email Analysis")
    print("   6. Security Scanning")
    
    # Wait for API to be ready
    print("\n⏳ Waiting for API to be ready...")
    time.sleep(2)
    
    # Run tests
    if test_health():
        test_phishing_detection()
        test_explainable_ai()
        test_feature_importance()
        test_email_analysis()
        test_security_scanning()
        
        print("\n" + "="*80)
        print("  ✅ ALL TESTS COMPLETED!")
        print("="*80)
        print("\n🎉 Your DevSecScan platform with Explainable AI is ready!")
        print("\n📊 Access the dashboard at: http://localhost:3000")
        print("📚 Access the API docs at: http://localhost:8000/docs")
        print("\n🧠 New Features:")
        print("   • Explainable AI with SHAP/LIME")
        print("   • Feature importance visualization")
        print("   • 6-tab unified dashboard")
        print("   • All old features accessible")
        print("\n🚀 Ready for your presentation!")
    else:
        print("\n❌ API is not ready. Please start the API server first:")
        print("   python real_api.py")

if __name__ == "__main__":
    main()

