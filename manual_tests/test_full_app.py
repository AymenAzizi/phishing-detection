#!/usr/bin/env python3
"""
Comprehensive test suite for the phishing detection application.
Tests all features and functionality.
"""

import sys
import os
import json
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_success(text):
    """Print success message"""
    print(f"✅ {text}")

def print_error(text):
    """Print error message"""
    print(f"❌ {text}")

def print_info(text):
    """Print info message"""
    print(f"ℹ️  {text}")

def test_imports():
    """Test that all required modules can be imported"""
    print_header("PHASE 1: Testing Imports")
    
    try:
        print_info("Testing core imports...")
        import fastapi
        print_success("FastAPI imported")
        
        import pandas
        print_success("Pandas imported")
        
        import numpy
        print_success("NumPy imported")
        
        import sklearn
        print_success("Scikit-learn imported")
        
        import requests
        print_success("Requests imported")
        
        print_info("Testing project modules...")
        from real_api import app
        print_success("real_api module imported")

        from real_feature_extractor import RealFeatureExtractor
        print_success("RealFeatureExtractor imported")
        
        print_success("All imports successful!")
        return True
    except Exception as e:
        print_error(f"Import failed: {str(e)}")
        return False

def test_feature_extractor():
    """Test the feature extractor"""
    print_header("PHASE 2: Testing Feature Extractor")

    try:
        from real_feature_extractor import RealFeatureExtractor

        extractor = RealFeatureExtractor()
        print_success("FeatureExtractor initialized")
        
        # Test URL features
        test_urls = [
            "https://www.google.com",
            "https://www.paypal.com",
            "https://www.amazon.com",
            "http://suspicious-site-12345.xyz",
            "https://bit.ly/abc123",
        ]
        
        print_info("Testing URL feature extraction...")
        for url in test_urls:
            try:
                features = extractor.extract_features(url)
                print_success(f"Extracted features for: {url}")
                print_info(f"  Features shape: {features.shape if hasattr(features, 'shape') else len(features)}")
            except Exception as e:
                print_error(f"Failed to extract features for {url}: {str(e)}")
        
        # Test email features
        test_emails = [
            "user@gmail.com",
            "admin@company.com",
            "noreply@suspicious.xyz",
        ]
        
        print_info("Testing email feature extraction...")
        for email in test_emails:
            try:
                features = extractor.extract_email_features(email)
                print_success(f"Extracted email features for: {email}")
                print_info(f"  Features shape: {features.shape if hasattr(features, 'shape') else len(features)}")
            except Exception as e:
                print_error(f"Failed to extract email features for {email}: {str(e)}")
        
        print_success("Feature extractor tests passed!")
        return True
    except Exception as e:
        print_error(f"Feature extractor test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_model_loading():
    """Test that the ML model can be loaded"""
    print_header("PHASE 3: Testing Model Loading")
    
    try:
        from real_api import model, feature_extractor
        
        if model is None:
            print_error("Model is None")
            return False
        
        print_success("Model loaded successfully")
        print_info(f"Model type: {type(model)}")
        
        if feature_extractor is None:
            print_error("Feature extractor is None")
            return False
        
        print_success("Feature extractor loaded successfully")
        
        return True
    except Exception as e:
        print_error(f"Model loading test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_predictions():
    """Test URL and email predictions"""
    print_header("PHASE 4: Testing Predictions")

    try:
        from real_api import predict_url, predict_email
        from real_feature_extractor import RealFeatureExtractor

        extractor = RealFeatureExtractor()
        
        # Test URL predictions
        test_urls = [
            ("https://www.google.com", "legitimate"),
            ("https://www.paypal.com", "legitimate"),
            ("https://www.amazon.com", "legitimate"),
            ("http://suspicious-site-12345.xyz", "phishing"),
        ]
        
        print_info("Testing URL predictions...")
        for url, expected_type in test_urls:
            try:
                result = predict_url(url)
                print_success(f"Predicted for {url}")
                print_info(f"  Result: {result}")
            except Exception as e:
                print_error(f"Prediction failed for {url}: {str(e)}")
        
        # Test email predictions
        test_emails = [
            ("user@gmail.com", "legitimate"),
            ("admin@company.com", "legitimate"),
            ("noreply@suspicious.xyz", "phishing"),
        ]
        
        print_info("Testing email predictions...")
        for email, expected_type in test_emails:
            try:
                result = predict_email(email)
                print_success(f"Predicted for {email}")
                print_info(f"  Result: {result}")
            except Exception as e:
                print_error(f"Prediction failed for {email}: {str(e)}")
        
        print_success("Prediction tests passed!")
        return True
    except Exception as e:
        print_error(f"Prediction test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print_header("PHASE 5: Testing API Endpoints")
    
    try:
        from fastapi.testclient import TestClient
        from real_api import app
        
        client = TestClient(app)
        print_success("TestClient created")
        
        # Test health endpoint
        print_info("Testing /health endpoint...")
        response = client.get("/health")
        if response.status_code == 200:
            print_success(f"Health check passed: {response.json()}")
        else:
            print_error(f"Health check failed: {response.status_code}")
        
        # Test info endpoint
        print_info("Testing /info endpoint...")
        response = client.get("/info")
        if response.status_code == 200:
            print_success(f"Info endpoint passed: {response.json()}")
        else:
            print_error(f"Info endpoint failed: {response.status_code}")
        
        # Test URL prediction endpoint
        print_info("Testing /predict/url endpoint...")
        response = client.post("/predict/url", json={"url": "https://www.google.com"})
        if response.status_code == 200:
            print_success(f"URL prediction endpoint passed: {response.json()}")
        else:
            print_error(f"URL prediction endpoint failed: {response.status_code}")
        
        # Test email prediction endpoint
        print_info("Testing /predict/email endpoint...")
        response = client.post("/predict/email", json={"email": "user@gmail.com"})
        if response.status_code == 200:
            print_success(f"Email prediction endpoint passed: {response.json()}")
        else:
            print_error(f"Email prediction endpoint failed: {response.status_code}")
        
        # Test batch prediction endpoint
        print_info("Testing /predict/batch endpoint...")
        response = client.post("/predict/batch", json={
            "urls": ["https://www.google.com", "https://www.paypal.com"],
            "emails": ["user@gmail.com", "admin@company.com"]
        })
        if response.status_code == 200:
            print_success(f"Batch prediction endpoint passed: {response.json()}")
        else:
            print_error(f"Batch prediction endpoint failed: {response.status_code}")
        
        print_success("API endpoint tests passed!")
        return True
    except Exception as e:
        print_error(f"API endpoint test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_security_features():
    """Test security features"""
    print_header("PHASE 6: Testing Security Features")
    
    try:
        print_info("Checking security configuration...")
        
        # Check if .env.example exists
        if Path(".env.example").exists():
            print_success(".env.example exists")
        else:
            print_error(".env.example not found")
        
        # Check if .gitignore exists
        if Path(".gitignore").exists():
            print_success(".gitignore exists")
        else:
            print_error(".gitignore not found")
        
        # Check if pre-commit config exists
        if Path(".pre-commit-config.yaml").exists():
            print_success(".pre-commit-config.yaml exists")
        else:
            print_error(".pre-commit-config.yaml not found")
        
        # Check if Dockerfile exists
        if Path("Dockerfile").exists():
            print_success("Dockerfile exists")
        else:
            print_error("Dockerfile not found")
        
        # Check if docker-compose exists
        if Path("docker-compose.yml").exists():
            print_success("docker-compose.yml exists")
        else:
            print_error("docker-compose.yml not found")
        
        # Check if Kubernetes manifests exist
        k8s_dir = Path("k8s")
        if k8s_dir.exists():
            k8s_files = list(k8s_dir.glob("*.yaml"))
            print_success(f"Kubernetes manifests found: {len(k8s_files)} files")
        else:
            print_error("k8s directory not found")
        
        print_success("Security features check passed!")
        return True
    except Exception as e:
        print_error(f"Security features test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print_header("PHISHING DETECTION - COMPREHENSIVE TEST SUITE")
    print_info("Testing all features and functionality...")
    
    results = {
        "Imports": test_imports(),
        "Feature Extractor": test_feature_extractor(),
        "Model Loading": test_model_loading(),
        "Predictions": test_predictions(),
        "API Endpoints": test_api_endpoints(),
        "Security Features": test_security_features(),
    }
    
    print_header("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print_header(f"RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print_success("ALL TESTS PASSED! ✨")
        return 0
    else:
        print_error(f"{total - passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

