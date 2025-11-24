#!/usr/bin/env python3
"""
DevSecScan API - Comprehensive Security Scanning Platform
Combines phishing detection with SSL/TLS, headers, and vulnerability scanning
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import pickle
import numpy as np
from typing import Dict, List, Optional
import time
import uuid
from datetime import datetime
import os
import re
from urllib.parse import urlparse
from real_feature_extractor import RealFeatureExtractor
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import structlog

# Import security scanners
from security_scanners.comprehensive_scanner import ComprehensiveScanner

# Import ML explainer
try:
    from ml_explainer import MLExplainer
    ML_EXPLAINER_AVAILABLE = True
except ImportError:
    ML_EXPLAINER_AVAILABLE = False
    print("⚠️ ML Explainer not available. Install SHAP and LIME for explainable AI features.")

# Pydantic models
class URLPredictionRequest(BaseModel):
    url: str
    include_features: bool = False

class URLPredictionResponse(BaseModel):
    prediction_id: str
    url: str
    is_phishing: bool
    confidence: float
    threat_level: str
    processing_time_ms: float
    timestamp: str
    risk_factors: List[str]
    features: Optional[Dict] = None

class EmailPredictionRequest(BaseModel):
    email_content: str
    sender: Optional[str] = None
    subject: Optional[str] = None

class EmailPredictionResponse(BaseModel):
    prediction_id: str
    sender: Optional[str] = None
    subject: Optional[str] = None
    is_phishing: bool
    confidence: float
    threat_level: str
    processing_time_ms: float
    timestamp: str
    risk_factors: List[str]

class SystemStatus(BaseModel):
    status: str
    model_loaded: bool
    feature_extractor_ready: bool
    timestamp: str
    model_info: Dict

    class Config:
        protected_namespaces = ()

# New security scanning models
class SecurityScanRequest(BaseModel):
    url: str
    scan_types: Optional[List[str]] = None  # ['ssl', 'headers', 'vulnerabilities', 'phishing']
    depth: str = 'standard'  # 'quick', 'standard', 'deep'

class SecurityScanResponse(BaseModel):
    scan_id: str
    url: str
    overall_score: float
    grade: str
    security_level: str
    total_issues: int
    issues_by_severity: Dict[str, int]
    scanner_scores: Dict[str, float]
    timestamp: str
    scan_depth: str
    scans: Dict
    top_recommendations: List[Dict]

# Initialize FastAPI app
app = FastAPI(
    title="DevSecScan API",
    description="Comprehensive security scanning platform for developers - SSL/TLS, Headers, Vulnerabilities, and Phishing Detection",
    version="4.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for ML model
ml_model = None
feature_scaler = None
feature_extractor = None
feature_names = []
model_metadata = {}
feature_extractor_ready = False

# Global security scanner
security_scanner = None

# Global ML explainer
ml_explainer = None

def load_trained_model():
    """Load the trained ML model and components"""
    global ml_model, feature_scaler, feature_extractor, feature_names, model_metadata, feature_extractor_ready

    try:
        print("🔄 Loading trained ML model...")

        # Load model
        if os.path.exists('models/best_phishing_model.pkl'):
            with open('models/best_phishing_model.pkl', 'rb') as f:
                ml_model = pickle.load(f)
            print("✅ ML model loaded successfully")
        else:
            print("❌ ML model not found at models/best_phishing_model.pkl")
            return False

        # Load scaler
        if os.path.exists('models/feature_scaler.pkl'):
            with open('models/feature_scaler.pkl', 'rb') as f:
                feature_scaler = pickle.load(f)
            print("✅ Feature scaler loaded successfully")

        # Load feature names
        if os.path.exists('models/feature_names.pkl'):
            with open('models/feature_names.pkl', 'rb') as f:
                feature_names = pickle.load(f)
            print("✅ Feature names loaded successfully")

        # Load metadata
        if os.path.exists('models/model_metadata.pkl'):
            with open('models/model_metadata.pkl', 'rb') as f:
                model_metadata = pickle.load(f)
            print("✅ Model metadata loaded successfully")

        # Initialize feature extractor
        feature_extractor = RealFeatureExtractor()
        feature_extractor_ready = True
        print("✅ Feature extractor initialized")

        print(f"🎯 Model: {model_metadata.get('model_name', 'Unknown')}")
        print(f"📊 F1-Score: {model_metadata.get('f1_score', 'Unknown')}")
        print(f"🔢 Features: {len(feature_names)}")

        return True

    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_risk_factors(features_dict: Dict) -> List[str]:
    """Generate human-readable risk factors from features"""
    risk_factors = []

    if features_dict.get('Have_IP'):
        risk_factors.append("URL contains IP address instead of domain")
    if features_dict.get('Have_At'):
        risk_factors.append("URL contains @ symbol (credential hiding)")
    if features_dict.get('URL_Length') == 0:
        risk_factors.append("Unusually long URL")
    if features_dict.get('Redirection'):
        risk_factors.append("URL contains redirection patterns")
    if features_dict.get('https_Domain'):
        risk_factors.append("Does not use HTTPS")
    if features_dict.get('TinyURL'):
        risk_factors.append("Uses URL shortening service")
    if features_dict.get('Prefix_Suffix'):
        risk_factors.append("Domain contains prefix/suffix separators")
    if features_dict.get('iFrame'):
        risk_factors.append("Page contains iFrame elements")
    if features_dict.get('Mouse_Over'):
        risk_factors.append("Page uses mouse-over events")
    if features_dict.get('Right_Click'):
        risk_factors.append("Right-click disabled on page")
    if features_dict.get('Web_Forwards'):
        risk_factors.append("Page contains forwarding scripts")

    return risk_factors if risk_factors else ["No specific risk factors detected"]

def predict_phishing_ml(url: str, include_features: bool = False) -> Dict:
    """Make phishing prediction using trained ML model"""
    if ml_model is None:
        raise HTTPException(status_code=503, detail="ML model not loaded. Please train the model first.")

    start_time = time.time()

    try:
        # Extract features
        features_dict = feature_extractor.extract_url_features(url)
        features_vector = [features_dict.get(name, 0) for name in feature_names]
        features_array = np.array(features_vector).reshape(1, -1)

        # Scale features if scaler is available
        if feature_scaler is not None:
            features_array = feature_scaler.transform(features_array)

        # Make prediction
        prediction = ml_model.predict(features_array)[0]
        prediction_proba = ml_model.predict_proba(features_array)[0]

        # Get confidence (probability of predicted class)
        confidence = float(prediction_proba[int(prediction)])

        # Determine threat level
        if not prediction:  # Legitimate
            threat_level = "low"
        else:  # Phishing
            if confidence >= 0.9:
                threat_level = "critical"
            elif confidence >= 0.7:
                threat_level = "high"
            else:
                threat_level = "medium"

        # Generate risk factors based on features
        risk_factors = generate_risk_factors(features_dict)

        processing_time = (time.time() - start_time) * 1000

        result = {
            "prediction_id": str(uuid.uuid4()),
            "url": url,
            "is_phishing": bool(prediction),
            "confidence": confidence,
            "threat_level": threat_level,
            "processing_time_ms": processing_time,
            "timestamp": datetime.utcnow().isoformat(),
            "risk_factors": risk_factors,
            "features": features_dict if include_features else None
        }

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

def analyze_email_content(email_content: str, sender: str = None, subject: str = None) -> Dict:
    """Analyze email content for phishing indicators using heuristics + URL ML model"""
    start_time = time.time()

    try:
        risk_score = 0.0
        risk_factors = []

        content_lower = email_content.lower()

        # Check for urgency keywords
        urgency_keywords = ['urgent', 'immediate', 'act now', 'expires', 'limited time', 'hurry']
        urgency_count = sum(1 for keyword in urgency_keywords if keyword in content_lower)
        if urgency_count > 0:
            risk_score += 0.3
            risk_factors.append("Contains urgency keywords")

        # Check for financial keywords
        financial_keywords = ['bank', 'paypal', 'credit card', 'account', 'payment', 'verify', 'suspend']
        financial_count = sum(1 for keyword in financial_keywords if keyword in content_lower)
        if financial_count > 0:
            risk_score += 0.3
            risk_factors.append("Contains financial keywords")

        # Check for threat keywords
        threat_keywords = ['suspend', 'terminate', 'block', 'security', 'unauthorized', 'compromised']
        threat_count = sum(1 for keyword in threat_keywords if keyword in content_lower)
        if threat_count > 0:
            risk_score += 0.2
            risk_factors.append("Contains threat keywords")

        # Check for suspicious URLs (heuristic)
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, email_content)
        suspicious_url_count = sum(1 for url in urls if any(sus in url.lower() for sus in ['bit.ly', 'tinyurl', '.tk', '.ml']))
        if suspicious_url_count > 0:
            risk_score += 0.4
            risk_factors.append("Contains suspicious URLs")

        # Use ML model to analyze URLs inside the email, if available
        ml_flagged_urls = []
        if ml_model is not None and urls:
            for url in urls:
                try:
                    ml_result = predict_phishing_ml(url)
                    if ml_result.get("is_phishing") and ml_result.get("confidence", 0.0) >= 0.7:
                        ml_flagged_urls.append((url, ml_result["confidence"]))
                except Exception:
                    # Don't break email analysis if URL model fails for one URL
                    continue

        if ml_flagged_urls:
            # Boost risk score if any embedded URL looks phishing
            risk_score += 0.3
            for url, conf in ml_flagged_urls[:3]:
                risk_factors.append(
                    f"ML model flagged URL as phishing: {url} ({conf * 100:.1f}% confidence)"
                )

        # Check sender domain if provided
        if sender and any(sus in sender.lower() for sus in ['.tk', '.ml', 'temp', 'fake']):
            risk_score += 0.2
            risk_factors.append("Suspicious sender domain")

        # Normalize risk score
        risk_score = min(risk_score, 1.0)

        # Determine if phishing
        is_phishing = risk_score > 0.5
        confidence = risk_score if is_phishing else 1.0 - risk_score

        # Determine threat level
        if not is_phishing:
            threat_level = "low"
        elif risk_score >= 0.8:
            threat_level = "critical"
        elif risk_score >= 0.7:
            threat_level = "high"
        else:
            threat_level = "medium"

        processing_time = (time.time() - start_time) * 1000

        return {
            "prediction_id": str(uuid.uuid4()),
            "sender": sender,
            "subject": subject,
            "is_phishing": is_phishing,
            "confidence": float(confidence),
            "threat_level": threat_level,
            "processing_time_ms": processing_time,
            "timestamp": datetime.utcnow().isoformat(),
            "risk_factors": risk_factors
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email prediction failed: {str(e)}")

# API Endpoints
@app.on_event("startup")
async def startup_event():
    """Load model and initialize scanners on startup"""
    global security_scanner, ml_explainer

    print("🚀 DevSecScan API starting...")
    success = load_trained_model()
    if success:
        print("✅ ML model loaded successfully")
        print("🎯 API ready for real phishing detection")
    else:
        print("⚠️  API starting without trained ML model")
        print("📝 To train the model, run: python real_model_trainer.py")

    # Initialize security scanner
    try:
        security_scanner = ComprehensiveScanner()
        print("✅ Security scanners initialized")
        print("🔒 SSL/TLS, Headers, and Vulnerability scanning ready")
    except Exception as e:
        print(f"⚠️  Security scanners initialization failed: {e}")

    # Initialize ML explainer
    if ML_EXPLAINER_AVAILABLE and success:
        try:
            ml_explainer = MLExplainer()
            print("✅ ML Explainer initialized (SHAP/LIME)")
            print("🧠 Explainable AI features ready")
        except Exception as e:
            print(f"⚠️  ML Explainer initialization failed: {e}")
            ml_explainer = None
        print("📝 Some security scanning features may not be available")

@app.get("/")
async def root():
    return {
        "message": "Real Phishing Detection API",
        "version": "2.0.0",
        "status": "operational",
        "detection_method": "rule-based",
        "docs": "/docs"
    }

@app.post("/predict/url", response_model=URLPredictionResponse)
async def predict_url(request: URLPredictionRequest):
    """Analyze URL for phishing using trained ML model"""
    if ml_model is None:
        raise HTTPException(
            status_code=503,
            detail="ML model not loaded. Please train the model first by running: python real_model_trainer.py"
        )

    try:
        result = predict_phishing_ml(request.url, request.include_features)
        return URLPredictionResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/predict/email", response_model=EmailPredictionResponse)
async def predict_email(request: EmailPredictionRequest):
    """Analyze email for phishing indicators"""
    try:
        result = analyze_email_content(request.email_content, request.sender, request.subject)
        return EmailPredictionResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email prediction failed: {str(e)}")

@app.post("/api/v1/explain")
async def explain_prediction(request: URLPredictionRequest):
    """Explain phishing prediction using SHAP/LIME"""
    if ml_explainer is None:
        raise HTTPException(
            status_code=503,
            detail="ML Explainer not available. Install SHAP and LIME libraries."
        )

    if ml_model is None:
        raise HTTPException(
            status_code=503,
            detail="ML model not loaded."
        )

    try:
        # Get prediction with features
        result = predict_phishing_ml(request.url, include_features=True)

        # Extract features for explanation
        features_dict = feature_extractor.extract_url_features(request.url)
        features_vector = np.array([features_dict.get(name, 0) for name in feature_names])

        # Scale features
        if feature_scaler is not None:
            features_vector = feature_scaler.transform(features_vector.reshape(1, -1))[0]

        # Get explanation
        explanation = ml_explainer.explain_prediction(
            features_vector,
            feature_dict=features_dict,
            method="shap"
        )

        # Combine prediction and explanation
        return {
            **result,
            "explanation": explanation
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")

@app.get("/api/v1/feature-importance")
async def get_feature_importance():
    """Get global feature importance from the model"""
    if ml_explainer is None:
        raise HTTPException(
            status_code=503,
            detail="ML Explainer not available."
        )

    try:
        importance = ml_explainer.get_global_feature_importance()
        return importance
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get feature importance: {str(e)}")

@app.get("/model/info")
async def get_model_info():
    """Get information about the loaded ML model"""
    if ml_model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    return {
        "model_metadata": model_metadata,
        "feature_names": feature_names,
        "model_type": type(ml_model).__name__,
        "feature_count": len(feature_names),
        "status": "loaded"
    }

@app.post("/retrain")
async def retrain_model():
    """Trigger model retraining"""
    try:
        import subprocess
        result = subprocess.run(
            ["python", "real_model_trainer.py"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )

        if result.returncode == 0:
            # Reload the model
            success = load_trained_model()
            return {
                "status": "success" if success else "failed_to_reload",
                "message": "Model retrained successfully" if success else "Training completed but failed to reload",
                "output": result.stdout
            }
        else:
            return {
                "status": "failed",
                "message": "Training failed",
                "error": result.stderr
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retraining failed: {str(e)}")

# ============================================================================
# MONITORING & OBSERVABILITY
# ============================================================================

# Prometheus Metrics
url_predictions_total = Counter(
    'url_predictions_total',
    'Total URL predictions',
    ['result']
)
email_predictions_total = Counter(
    'email_predictions_total',
    'Total email predictions',
    ['result']
)
prediction_duration = Histogram(
    'prediction_duration_seconds',
    'Prediction processing time',
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0)
)
active_predictions = Gauge(
    'active_predictions',
    'Number of active predictions'
)

# Health Check Endpoints
@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    return {
        "status": "healthy",
        "ml_model_loaded": ml_model is not None,
        "security_scanners_ready": security_scanner is not None,
        "ml_explainer_ready": ml_explainer is not None,
        "feature_extractor_ready": feature_extractor_ready,
        "timestamp": datetime.utcnow().isoformat(),
        "service": "DevSecScan API",
        "version": "4.0.0",
        "features": {
            "phishing_detection": ml_model is not None,
            "explainable_ai": ml_explainer is not None,
            "security_scanning": security_scanner is not None,
            "email_analysis": True
        }
    }

@app.get("/ready")
async def readiness_check():
    """Readiness check - verifies dependencies"""
    try:
        # Check if model is loaded
        if model is None:
            return {"status": "not_ready", "reason": "model_not_loaded"}, 503

        # Check if feature extractor is loaded
        if feature_extractor is None:
            return {"status": "not_ready", "reason": "feature_extractor_not_loaded"}, 503

        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
            "model_loaded": model is not None,
            "feature_extractor_loaded": feature_extractor is not None
        }
    except Exception as e:
        return {"status": "not_ready", "reason": str(e)}, 503

@app.get("/live")
async def liveness_check():
    """Liveness check - verifies service is running"""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": time.time()
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()

@app.get("/info")
async def info():
    """Service information endpoint"""
    return {
        "service": "devsec-scan-api",
        "version": "4.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "timestamp": datetime.utcnow().isoformat(),
        "features": [
            "SSL/TLS Security Scanning",
            "Security Headers Analysis",
            "Vulnerability Detection",
            "ML-based Phishing Detection"
        ]
    }

# ============================================================================
# PHISHING DETECTION ENDPOINTS (v1 API)
# ============================================================================

@app.post("/api/v1/predict", response_model=URLPredictionResponse)
async def predict_url_v1(request: URLPredictionRequest):
    """Analyze URL for phishing using trained ML model (v1 API)"""
    if ml_model is None:
        raise HTTPException(
            status_code=503,
            detail="ML model not loaded. Please check model file exists."
        )

    try:
        result = predict_phishing_ml(request.url, request.include_features)
        return URLPredictionResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/api/v1/email", response_model=EmailPredictionResponse)
async def predict_email_v1(request: EmailPredictionRequest):
    """Analyze email for phishing indicators (v1 API)"""
    try:
        result = analyze_email_content(request.email_content, request.sender, request.subject)
        return EmailPredictionResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email analysis failed: {str(e)}")

# ============================================================================
# NEW SECURITY SCANNING ENDPOINTS
# ============================================================================

@app.post("/api/v1/scan/comprehensive", response_model=SecurityScanResponse)
async def comprehensive_security_scan(request: SecurityScanRequest):
    """
    Comprehensive security scan - all scanners

    Runs SSL/TLS, Security Headers, Vulnerability, and Phishing detection scans
    """
    if security_scanner is None:
        raise HTTPException(status_code=503, detail="Security scanner not initialized")

    try:
        start_time = time.time()

        # Run comprehensive scan
        results = security_scanner.scan(
            url=request.url,
            scan_types=request.scan_types,
            depth=request.depth
        )

        processing_time = (time.time() - start_time) * 1000

        return SecurityScanResponse(
            scan_id=str(uuid.uuid4()),
            url=request.url,
            overall_score=results['overall']['overall_score'],
            grade=results['overall']['grade'],
            security_level=results['overall']['summary']['security_level'],
            total_issues=results['overall']['total_issues'],
            issues_by_severity=results['overall']['issues_by_severity'],
            scanner_scores=results['overall']['scanner_scores'],
            timestamp=datetime.utcnow().isoformat(),
            scan_depth=request.depth,
            scans=results['scans'],
            top_recommendations=results['overall']['top_recommendations']
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Security scan failed: {str(e)}")

@app.post("/api/v1/scan/quick")
async def quick_security_scan(request: SecurityScanRequest):
    """
    Quick security scan - SSL and Headers only (fast)
    """
    if security_scanner is None:
        raise HTTPException(status_code=503, detail="Security scanner not initialized")

    try:
        results = security_scanner.quick_scan(request.url)

        return {
            "scan_id": str(uuid.uuid4()),
            "url": request.url,
            "overall_score": results['overall']['overall_score'],
            "grade": results['overall']['grade'],
            "scans": results['scans'],
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick scan failed: {str(e)}")

@app.post("/api/v1/scan/ssl")
async def ssl_scan(request: SecurityScanRequest):
    """SSL/TLS security scan only"""
    if security_scanner is None:
        raise HTTPException(status_code=503, detail="Security scanner not initialized")

    try:
        results = security_scanner.ssl_scanner.scan(request.url)
        return {
            "scan_id": str(uuid.uuid4()),
            "url": request.url,
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SSL scan failed: {str(e)}")

@app.post("/api/v1/scan/headers")
async def headers_scan(request: SecurityScanRequest):
    """Security headers scan only"""
    if security_scanner is None:
        raise HTTPException(status_code=503, detail="Security scanner not initialized")

    try:
        results = security_scanner.headers_scanner.scan(request.url)
        return {
            "scan_id": str(uuid.uuid4()),
            "url": request.url,
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Headers scan failed: {str(e)}")

@app.post("/api/v1/scan/vulnerabilities")
async def vulnerability_scan(request: SecurityScanRequest):
    """Vulnerability scan only"""
    if security_scanner is None:
        raise HTTPException(status_code=503, detail="Security scanner not initialized")

    try:
        results = security_scanner.vulnerability_scanner.scan(request.url)
        return {
            "scan_id": str(uuid.uuid4()),
            "url": request.url,
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vulnerability scan failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting DevSecScan API...")
    print("📊 Health check: http://localhost:8000/health")
    print("📚 Interactive docs: http://localhost:8000/docs")
    print("🔒 Security scanning endpoints:")
    print("   - POST /api/v1/scan/comprehensive")
    print("   - POST /api/v1/scan/quick")
    print("   - POST /api/v1/scan/ssl")
    print("   - POST /api/v1/scan/headers")
    print("   - POST /api/v1/scan/vulnerabilities")
    print("⚡ Ready for comprehensive security scanning!")

    uvicorn.run(app, host="0.0.0.0", port=8000)