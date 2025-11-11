# API Documentation

The Phishing Detection System provides a comprehensive REST API for analyzing URLs and emails for phishing attempts.

## 🔗 Base URL

```
Production: https://api.phishing-detection.com
Development: http://localhost:8000
```

## 🔐 Authentication

The API uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Get Authentication Token

**POST** `/auth/token`

```bash
curl -X POST "http://localhost:8000/auth/token" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "admin",
       "password": "admin"
     }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

## 📊 Core Endpoints

### 1. URL Analysis

**POST** `/api/v1/predict/url`

Analyze a URL for phishing indicators.

**Request:**
```json
{
  "url": "https://suspicious-site.com/login",
  "include_features": false
}
```

**Response:**
```json
{
  "prediction_id": "550e8400-e29b-41d4-a716-446655440000",
  "url": "https://suspicious-site.com/login",
  "is_phishing": true,
  "confidence": 0.94,
  "threat_level": "high",
  "processing_time_ms": 145.2,
  "timestamp": "2024-01-15T10:30:00Z",
  "risk_factors": [
    "Suspicious top-level domain",
    "Contains suspicious keywords",
    "Domain age less than 30 days"
  ],
  "features": {
    "has_ip": 0,
    "url_length": 45,
    "suspicious_tld": 1,
    "subdomain_count": 2
  }
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/predict/url" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://suspicious-site.com/login",
       "include_features": true
     }'
```

### 2. Email Analysis

**POST** `/api/v1/predict/email`

Analyze email content for phishing indicators.

**Request:**
```json
{
  "email_content": "Subject: Urgent Account Verification\n\nYour account will be suspended...",
  "email_headers": {
    "From": "security@bank.com",
    "Reply-To": "noreply@suspicious.com"
  },
  "sender": "security@bank.com",
  "subject": "Urgent Account Verification",
  "include_features": false
}
```

**Response:**
```json
{
  "prediction_id": "550e8400-e29b-41d4-a716-446655440001",
  "sender": "security@bank.com",
  "subject": "Urgent Account Verification",
  "is_phishing": true,
  "confidence": 0.89,
  "threat_level": "high",
  "processing_time_ms": 203.7,
  "timestamp": "2024-01-15T10:31:00Z",
  "risk_factors": [
    "Sender and reply-to domains don't match",
    "Contains urgency keywords",
    "Contains financial keywords"
  ],
  "suspicious_urls": [
    "http://bit.ly/verify-account"
  ]
}
```

### 3. Batch Analysis

**POST** `/api/v1/predict/batch`

Analyze multiple URLs or emails in a single request.

**Request:**
```json
{
  "prediction_type": "url",
  "items": [
    {
      "url": "https://example.com"
    },
    {
      "url": "https://suspicious-site.tk"
    }
  ]
}
```

**Response:**
```json
{
  "total_items": 2,
  "successful_predictions": 2,
  "failed_predictions": 0,
  "total_processing_time_ms": 298.5,
  "results": [
    {
      "prediction_id": "550e8400-e29b-41d4-a716-446655440002",
      "url": "https://example.com",
      "is_phishing": false,
      "confidence": 0.92,
      "threat_level": "low"
    },
    {
      "prediction_id": "550e8400-e29b-41d4-a716-446655440003",
      "url": "https://suspicious-site.tk",
      "is_phishing": true,
      "confidence": 0.87,
      "threat_level": "medium"
    }
  ],
  "errors": []
}
```

### 4. Feedback Submission

**POST** `/api/v1/feedback`

Submit feedback to improve model accuracy.

**Request:**
```json
{
  "prediction_id": "550e8400-e29b-41d4-a716-446655440000",
  "actual_label": 0,
  "confidence": 0.9,
  "comments": "This was actually a legitimate banking website",
  "user_id": "analyst_001"
}
```

**Response:**
```json
{
  "feedback_id": "fb550e8400-e29b-41d4-a716-446655440000",
  "status": "accepted",
  "message": "Feedback received and will be used to improve the model",
  "timestamp": "2024-01-15T10:32:00Z"
}
```

## 🏥 Health & Monitoring

### Health Check

**GET** `/health`

Basic health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "uptime_seconds": 3600,
  "components": {
    "api": "healthy",
    "database": "healthy",
    "ml_model": "healthy",
    "feature_extractors": "healthy"
  }
}
```

### Detailed Health Check

**GET** `/health/detailed`

Comprehensive system health information.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "uptime_seconds": 3600,
  "system_metrics": {
    "cpu_percent": 25.4,
    "memory_percent": 68.2,
    "memory_available_gb": 2.1,
    "disk_percent": 45.8,
    "disk_free_gb": 15.2
  },
  "process_metrics": {
    "memory_rss_mb": 512.3,
    "memory_vms_mb": 1024.6,
    "cpu_percent": 12.5,
    "num_threads": 8
  },
  "components": {
    "api": "healthy",
    "database": "healthy",
    "ml_model": "healthy",
    "feature_extractors": "healthy"
  }
}
```

### System Metrics

**GET** `/metrics`

Prometheus-compatible metrics endpoint.

**Response:**
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="POST",endpoint="/api/v1/predict/url",status="200"} 1234

# HELP prediction_processing_time_seconds Time spent processing predictions
# TYPE prediction_processing_time_seconds histogram
prediction_processing_time_seconds_bucket{le="0.1"} 856
prediction_processing_time_seconds_bucket{le="0.2"} 1205
prediction_processing_time_seconds_bucket{le="+Inf"} 1234

# HELP model_accuracy Current model accuracy
# TYPE model_accuracy gauge
model_accuracy 0.952
```

## 🔧 Admin Endpoints

### System Configuration

**GET** `/api/v1/admin/system/config`

Get system configuration (requires admin role).

**Response:**
```json
{
  "api_version": "1.0.0",
  "model_info": {
    "model_name": "Enhanced_XGBoost",
    "model_type": "XGBoost",
    "version": "1.0.0",
    "training_date": "2024-01-01T00:00:00Z",
    "accuracy": 0.95,
    "f1_score": 0.94,
    "feature_count": 25
  },
  "feature_extractors": ["URL Features", "Email Features"],
  "rate_limits": {"default": 100},
  "authentication_enabled": true
}
```

### Model Management

**POST** `/api/v1/admin/model/update`

Update the ML model (requires admin role).

**Request:**
```json
{
  "model_path": "/path/to/new/model.pkl",
  "backup_current": true
}
```

### System Statistics

**GET** `/api/v1/admin/stats`

Get comprehensive system statistics.

**Response:**
```json
{
  "total_predictions": 10000,
  "predictions_today": 150,
  "accuracy_rate": 0.95,
  "false_positive_rate": 0.03,
  "false_negative_rate": 0.02,
  "average_processing_time_ms": 145.2,
  "top_threat_sources": [
    {"domain": "suspicious-site.com", "count": 25},
    {"domain": "phishing-example.org", "count": 18}
  ],
  "model_performance": {
    "precision": 0.96,
    "recall": 0.94,
    "f1_score": 0.95,
    "auc": 0.98
  }
}
```

## 📝 Request/Response Schemas

### Common Response Fields

All prediction responses include these fields:

| Field | Type | Description |
|-------|------|-------------|
| `prediction_id` | string | Unique identifier for the prediction |
| `is_phishing` | boolean | Whether content is classified as phishing |
| `confidence` | float | Prediction confidence (0.0 to 1.0) |
| `threat_level` | string | Threat level: "low", "medium", "high", "critical" |
| `processing_time_ms` | float | Processing time in milliseconds |
| `timestamp` | string | ISO 8601 timestamp |

### Threat Levels

| Level | Confidence Range | Description |
|-------|------------------|-------------|
| `low` | 0.0 - 0.5 | Legitimate content |
| `medium` | 0.5 - 0.7 | Potentially suspicious |
| `high` | 0.7 - 0.9 | Likely phishing |
| `critical` | 0.9 - 1.0 | Highly confident phishing |

## ⚠️ Error Handling

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Invalid or missing token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 422 | Validation Error - Invalid request format |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |
| 503 | Service Unavailable - System overloaded |

### Error Response Format

```json
{
  "error": "validation_error",
  "message": "Invalid URL format",
  "details": {
    "field": "url",
    "issue": "URL must start with http:// or https://"
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_550e8400-e29b-41d4-a716-446655440000"
}
```

## 🚀 Rate Limiting

### Default Limits

- **Anonymous requests**: 10 requests per minute
- **Authenticated requests**: 100 requests per minute
- **Admin requests**: 1000 requests per minute

### Rate Limit Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248000
```

## 📚 SDK Examples

### Python SDK

```python
import requests

class PhishingDetectionClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}
    
    def analyze_url(self, url):
        response = requests.post(
            f"{self.base_url}/api/v1/predict/url",
            json={"url": url},
            headers=self.headers
        )
        return response.json()
    
    def analyze_email(self, email_content, sender=None):
        response = requests.post(
            f"{self.base_url}/api/v1/predict/email",
            json={"email_content": email_content, "sender": sender},
            headers=self.headers
        )
        return response.json()

# Usage
client = PhishingDetectionClient("http://localhost:8000", "your-token")
result = client.analyze_url("https://suspicious-site.com")
print(f"Phishing: {result['is_phishing']}, Confidence: {result['confidence']}")
```

### JavaScript SDK

```javascript
class PhishingDetectionClient {
    constructor(baseUrl, token) {
        this.baseUrl = baseUrl;
        this.headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
    }
    
    async analyzeUrl(url) {
        const response = await fetch(`${this.baseUrl}/api/v1/predict/url`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({ url })
        });
        return response.json();
    }
    
    async analyzeEmail(emailContent, sender = null) {
        const response = await fetch(`${this.baseUrl}/api/v1/predict/email`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({ email_content: emailContent, sender })
        });
        return response.json();
    }
}

// Usage
const client = new PhishingDetectionClient('http://localhost:8000', 'your-token');
client.analyzeUrl('https://suspicious-site.com')
    .then(result => console.log(`Phishing: ${result.is_phishing}, Confidence: ${result.confidence}`));
```

## 🔍 Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces provide interactive API exploration with request/response examples and the ability to test endpoints directly.
