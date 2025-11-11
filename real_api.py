#!/usr/bin/env python3
"""
Real Phishing Detection API - ML Model Integration
Uses trained ML models and real feature extraction for accurate phishing detection
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

# Initialize FastAPI app
app = FastAPI(
    title="Real Phishing Detection API",
    description="Production phishing detection using ML models",
    version="3.0.0"
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
    """Analyze email content for phishing indicators using heuristics"""
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

        # Check for suspicious URLs
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, email_content)
        suspicious_url_count = sum(1 for url in urls if any(sus in url.lower() for sus in ['bit.ly', 'tinyurl', '.tk', '.ml']))
        if suspicious_url_count > 0:
            risk_score += 0.4
            risk_factors.append("Contains suspicious URLs")

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
    """Load model on startup"""
    print("🚀 Phishing Detection API starting...")
    success = load_trained_model()
    if success:
        print("✅ ML model loaded successfully")
        print("🎯 API ready for real phishing detection")
    else:
        print("⚠️  API starting without trained ML model")
        print("📝 To train the model, run: python real_model_trainer.py")

@app.get("/")
async def root():
    return {
        "message": "Real Phishing Detection API",
        "version": "2.0.0",
        "status": "operational",
        "detection_method": "rule-based",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return SystemStatus(
        status="healthy",
        model_loaded=True,  # Rule-based system is always "loaded"
        feature_extractor_ready=feature_extractor_ready,
        timestamp=datetime.utcnow().isoformat(),
        model_info=model_metadata
    )

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
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "phishing-detection-api"
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
        "service": "phishing-detection-api",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    print("🚀 Starting Real Phishing Detection API...")
    print("📊 Health check: http://localhost:8000/health")
    print("📚 Interactive docs: http://localhost:8000/docs")
    print("⚡ Ready for real phishing detection!")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)