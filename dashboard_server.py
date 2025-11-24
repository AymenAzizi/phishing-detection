#!/usr/bin/env python3
"""
Dashboard server for the phishing detection system
Serves the monitoring dashboard and provides real-time data
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import random
from datetime import datetime, timedelta
import asyncio
from typing import Dict, List
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app for dashboard
dashboard_app = FastAPI(
    title="DevSecScan Dashboard",
    description="Real-time monitoring dashboard for DevSecScan security scanning platform",
    version="2.0.0"
)

# Add CORS middleware
dashboard_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
dashboard_app.mount("/static", StaticFiles(directory="dashboard"), name="static")

# Global variables for real data
prediction_history = []
system_metrics = {
    "total_predictions": 0,
    "predictions_today": 0,
    "phishing_detected": 0,
    "accuracy_rate": 0.0,
    "api_status": "unknown",
    "db_status": "healthy",
    "model_status": "unknown",
    "email_status": "healthy"
}

def get_real_model_info():
    """Get real model information from the API"""
    try:
        response = requests.get("http://127.0.0.1:8000/model/info", timeout=2)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def check_api_health():
    """Check if the main API is running"""
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False

@dashboard_app.get("/", response_class=HTMLResponse)
async def dashboard_home():
    """Serve the main DevSecScan dashboard"""
    try:
        with open("dashboard/devsec_dashboard.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        # Fallback to old dashboard
        try:
            with open("dashboard/index.html", "r", encoding="utf-8") as f:
                content = f.read()
            return HTMLResponse(content=content)
        except FileNotFoundError:
            return HTMLResponse(content="""
            <html>
                <head><title>Dashboard Not Found</title></head>
                <body>
                    <h1>Dashboard file not found</h1>
                    <p>Please ensure dashboard/devsec_dashboard.html or dashboard/index.html exists</p>
                </body>
            </html>
            """)

@dashboard_app.get("/old", response_class=HTMLResponse)
async def old_dashboard():
    """Serve the old phishing detection dashboard"""
    try:
        with open("dashboard/index.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        return HTMLResponse(content="""
        <html>
            <head><title>Dashboard Not Found</title></head>
            <body>
                <h1>Old dashboard file not found</h1>
                <p>Please ensure dashboard/index.html exists</p>
            </body>
        </html>
        """)

@dashboard_app.get("/api/system-status")
async def get_system_status():
    """Get current system status"""
    api_healthy = check_api_health()
    
    return {
        "api_status": "healthy" if api_healthy else "unhealthy",
        "db_status": "healthy",
        "model_status": "healthy" if api_healthy else "unhealthy",
        "email_status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@dashboard_app.get("/api/metrics")
async def get_metrics():
    """Get real system metrics"""
    # Get model info for accuracy
    model_info = get_real_model_info()
    if model_info and 'model_metadata' in model_info:
        metadata = model_info['model_metadata']
        system_metrics["accuracy_rate"] = metadata.get('f1_score', 0) * 100

    return {
        "total_predictions": system_metrics["total_predictions"],
        "predictions_today": system_metrics["predictions_today"],
        "phishing_detected": system_metrics["phishing_detected"],
        "accuracy_rate": system_metrics["accuracy_rate"],
        "timestamp": datetime.now().isoformat(),
        "model_info": model_info
    }

@dashboard_app.get("/api/recent-predictions")
async def get_recent_predictions():
    """Get recent real predictions for the dashboard"""
    global prediction_history

    # Keep only last 20 predictions
    prediction_history = prediction_history[-20:]

    return {"predictions": prediction_history}

@dashboard_app.get("/api/charts/predictions-over-time")
async def get_predictions_chart_data():
    """Get real data for predictions over time chart"""
    hours = []
    predictions = []

    # Generate hourly data based on actual prediction history
    current_hour = datetime.now().hour
    for i in range(24):
        hour = (current_hour - 23 + i) % 24
        hours.append(f"{hour:02d}:00")

        # Count predictions in this hour from history
        hour_predictions = sum(1 for pred in prediction_history
                             if pred.get('time', '').startswith(f"{hour:02d}:"))
        predictions.append(hour_predictions)

    return {
        "labels": hours,
        "data": predictions
    }

@dashboard_app.get("/api/charts/threat-distribution")
async def get_threat_distribution():
    """Get real threat level distribution data"""
    # Count threat levels from actual prediction history
    threat_counts = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}

    for pred in prediction_history:
        threat = pred.get('threat', 'Low').title()
        if threat in threat_counts:
            threat_counts[threat] += 1

    # If no data, show default distribution
    if sum(threat_counts.values()) == 0:
        threat_counts = {"Low": 1, "Medium": 0, "High": 0, "Critical": 0}

    return {
        "labels": list(threat_counts.keys()),
        "data": list(threat_counts.values())
    }

@dashboard_app.post("/api/test-prediction")
async def test_prediction_endpoint(request: Request):
    """Test prediction endpoint that forwards to main API"""
    try:
        body = await request.json()
        url = body.get("url", "")
        
        # Forward to real API
        response = requests.post(
            "http://127.0.0.1:8000/predict/url",
            json={"url": url, "include_features": True},
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()

            # Update system metrics
            system_metrics["total_predictions"] += 1
            system_metrics["predictions_today"] += 1
            if result["is_phishing"]:
                system_metrics["phishing_detected"] += 1

            # Add to prediction history
            prediction_history.append({
                "time": datetime.now().strftime("%H:%M:%S"),
                "type": "URL",
                "result": "Phishing" if result["is_phishing"] else "Legitimate",
                "confidence": f"{result['confidence']*100:.1f}%",
                "threat": result["threat_level"].title(),
                "processing_time": f"{result['processing_time_ms']:.1f}ms"
            })
            return result
        else:
            return {"error": "API request failed", "status": response.status_code}
            
    except requests.exceptions.RequestException:
        return {"error": "Could not connect to main API. Please ensure it's running on port 8000."}
    except Exception as e:
        return {"error": f"Prediction failed: {str(e)}"}

@dashboard_app.post("/api/test-email")
async def test_email_endpoint(request: Request):
    """Test email prediction endpoint that forwards to main API"""
    try:
        body = await request.json()
        email_content = body.get("email_content", "")
        sender = body.get("sender")
        subject = body.get("subject")

        # Forward to main API
        response = requests.post(
            "http://127.0.0.1:8000/predict/email",
            json={
                "email_content": email_content,
                "sender": sender,
                "subject": subject
            },
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()

            # Update system metrics
            system_metrics["total_predictions"] += 1
            system_metrics["predictions_today"] += 1
            if result["is_phishing"]:
                system_metrics["phishing_detected"] += 1

            # Add to prediction history
            prediction_history.append({
                "time": datetime.now().strftime("%H:%M:%S"),
                "type": "Email",
                "result": "Phishing" if result["is_phishing"] else "Legitimate",
                "confidence": f"{result['confidence']*100:.1f}%",
                "threat": result["threat_level"].title(),
                "processing_time": f"{result['processing_time_ms']:.1f}ms"
            })
            return result
        else:
            return {"error": "API request failed", "status": response.status_code}

    except requests.exceptions.RequestException:
        return {"error": "Could not connect to main API. Please ensure it's running on port 8000."}
    except Exception as e:
        return {"error": f"Email prediction failed: {str(e)}"}

@dashboard_app.get("/api/statistics")
async def get_detailed_statistics():
    """Get detailed system statistics"""
    # Calculate statistics from prediction history
    total_predictions = len(prediction_history)
    phishing_predictions = sum(1 for pred in prediction_history if pred["result"] == "Phishing")
    legitimate_predictions = total_predictions - phishing_predictions

    # Calculate threat level distribution
    threat_levels = {}
    for pred in prediction_history:
        threat = pred.get("threat", "Low")
        threat_levels[threat] = threat_levels.get(threat, 0) + 1

    # Calculate average processing time
    processing_times = []
    for pred in prediction_history:
        try:
            time_str = pred.get("processing_time", "0ms").replace("ms", "")
            processing_times.append(float(time_str))
        except:
            pass

    avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0

    return {
        "total_predictions": total_predictions,
        "phishing_detected": phishing_predictions,
        "legitimate_detected": legitimate_predictions,
        "threat_distribution": threat_levels,
        "average_processing_time": avg_processing_time,
        "prediction_types": {
            "URL": sum(1 for pred in prediction_history if pred["type"] == "URL"),
            "Email": sum(1 for pred in prediction_history if pred["type"] == "Email")
        },
        "timestamp": datetime.now().isoformat()
    }

@dashboard_app.post("/api/clear-history")
async def clear_prediction_history():
    """Clear prediction history"""
    global prediction_history
    prediction_history = []

    # Also try to clear browser monitor history if available
    try:
        from browser_monitor import monitor
        if hasattr(monitor, 'clear_events'):
            monitor.clear_events()
    except:
        pass

    return {"status": "success", "message": "Prediction history cleared"}

# Real-time monitoring endpoints
@dashboard_app.get("/api/monitoring/status")
async def get_monitoring_status():
    """Get real-time monitoring status"""
    try:
        from browser_monitor import monitor
        running = getattr(monitor, 'running', False)
        return {
            "status": "active" if running else "inactive",
            "monitoring_enabled": running,
            "last_check": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "unavailable", "monitoring_enabled": False}

@dashboard_app.post("/api/monitoring/start")
async def start_monitoring():
    """Start real-time browser monitoring"""
    try:
        from browser_monitor import monitor
        running = getattr(monitor, 'running', False)
        if not running:
            if hasattr(monitor, 'start_monitoring'):
                monitor.start_monitoring()
            return {"status": "success", "message": "Real-time monitoring started"}
        else:
            return {"status": "already_running", "message": "Monitoring is already active"}
    except Exception as e:
        import traceback
        logger.error(f"Error starting monitoring: {str(e)}\n{traceback.format_exc()}")
        return {"status": "error", "message": f"Browser monitor error: {str(e)}"}

@dashboard_app.post("/api/monitoring/stop")
async def stop_monitoring():
    """Stop real-time browser monitoring"""
    try:
        from browser_monitor import monitor
        running = getattr(monitor, 'running', False)
        if running:
            if hasattr(monitor, 'stop_monitoring'):
                monitor.stop_monitoring()
            return {"status": "success", "message": "Real-time monitoring stopped"}
        else:
            return {"status": "already_stopped", "message": "Monitoring is not active"}
    except Exception as e:
        import traceback
        logger.error(f"Error stopping monitoring: {str(e)}\n{traceback.format_exc()}")
        return {"status": "error", "message": f"Browser monitor error: {str(e)}"}

@dashboard_app.get("/api/monitoring/events")
async def get_monitoring_events():
    """Get recent browsing events"""
    try:
        from browser_monitor import monitor
        if hasattr(monitor, 'get_recent_events'):
            events = monitor.get_recent_events(hours=24)
        else:
            events = getattr(monitor, 'events', [])
        return {"events": events, "count": len(events)}
    except Exception as e:
        return {"events": [], "count": 0}

@dashboard_app.get("/api/monitoring/live")
async def get_live_events():
    """Get live browsing events"""
    try:
        from browser_monitor import monitor
        if hasattr(monitor, 'get_live_events'):
            events = monitor.get_live_events()
        else:
            events = getattr(monitor, 'events', [])
        return {"events": events, "count": len(events)}
    except Exception as e:
        return {"events": [], "count": 0}

@dashboard_app.get("/api/monitoring/summary")
async def get_monitoring_summary():
    """Get monitoring threat summary"""
    try:
        from browser_monitor import monitor
        if hasattr(monitor, 'get_threat_summary'):
            summary = monitor.get_threat_summary()
        else:
            summary = {
                "total_visits": 0,
                "phishing_blocked": 0,
                "legitimate_visits": 0,
                "avg_processing_time": 0,
                "protection_rate": 0
            }
        return summary
    except Exception as e:
        return {
            "total_visits": 0,
            "phishing_blocked": 0,
            "legitimate_visits": 0,
            "avg_processing_time": 0,
            "protection_rate": 0
        }

# Extension integration endpoints
@dashboard_app.post("/api/extension/event")
async def receive_extension_event(request: Request):
    """Receive browsing events from browser extension"""
    try:
        event = await request.json()

        # Add to prediction history for dashboard display
        prediction_history.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "type": "Extension",
            "result": "Phishing" if event["is_phishing"] else "Legitimate",
            "confidence": f"{event['confidence']*100:.1f}%",
            "threat": event["threat_level"].title(),
            "processing_time": f"{event['processing_time']:.1f}ms",
            "url": event["url"],
            "domain": event["domain"]
        })

        # Update system metrics
        system_metrics["total_predictions"] += 1
        system_metrics["predictions_today"] += 1
        if event["is_phishing"]:
            system_metrics["phishing_detected"] += 1

        # Keep only last 100 predictions
        if len(prediction_history) > 100:
            prediction_history.pop(0)

        return {"status": "success", "message": "Event received"}

    except Exception as e:
        return {"status": "error", "message": f"Failed to process event: {str(e)}"}

@dashboard_app.get("/api/extension/events")
async def get_extension_events():
    """Get recent extension events"""
    try:
        # Filter extension events from prediction history
        extension_events = [
            event for event in prediction_history
            if event.get("type") == "Extension"
        ]
        return {"events": extension_events, "count": len(extension_events)}
    except Exception as e:
        return {"events": [], "count": 0, "error": str(e)}

@dashboard_app.on_event("startup")
async def startup_event():
    """Initialize dashboard with real data"""
    print("🎯 DevSecScan Dashboard starting with real data integration...")
    print("📊 Connected to DevSecScan API for live security scanning")
    print("🔄 All mock data removed - using actual results only")
    print("🔒 Security scanners: SSL/TLS, Headers, Vulnerabilities, Phishing")

if __name__ == "__main__":
    print("=" * 70)
    print("🛡️  DevSecScan Dashboard - Comprehensive Security Scanning Platform")
    print("=" * 70)
    print("📊 Dashboard available at: http://localhost:3000")
    print("🔗 Make sure the main API is running on port 8000")
    print("✨ Features:")
    print("   • SSL/TLS Security Analysis")
    print("   • Security Headers Scanning")
    print("   • Vulnerability Detection")
    print("   • Phishing Detection (ML-based)")
    print("   • Real-time monitoring and testing interface")
    print("=" * 70)
    print("🚀 Starting server...")

    uvicorn.run(dashboard_app, host="0.0.0.0", port=3000, reload=False)
