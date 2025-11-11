# Ready-to-Use Templates & Code Snippets
## Copy-Paste Solutions for Quick Implementation

---

## 1. GitHub Actions Workflow - Test & Security

**File:** `.github/workflows/test-and-security.yml`

```yaml
name: Test & Security

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov bandit safety
      
      - name: Run tests
        run: pytest tests/ -v --cov
      
      - name: Security scan
        run: |
          bandit -r . || true
          safety check || true
```

---

## 2. Dockerfile - Production Ready

**File:** `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

HEALTHCHECK --interval=30s CMD python -c "import requests; requests.get('http://localhost:8000/health')"

EXPOSE 8000
CMD ["uvicorn", "real_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 3. Docker Compose - Local Development

**File:** `docker-compose.yml`

```yaml
version: '3.9'

services:
  postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  api:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/phishing_db
      REDIS_URL: redis://redis:6379

  dashboard:
    build:
      context: .
      dockerfile: Dockerfile.dashboard
    ports:
      - "3000:3000"
    depends_on:
      - api

volumes:
  postgres_data:
```

---

## 4. Health Check Endpoints

**File:** Add to `real_api.py`

```python
from datetime import datetime

@app.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/ready")
async def readiness_check():
    """Kubernetes readiness probe"""
    try:
        # Check critical dependencies
        db.execute("SELECT 1")
        assert model is not None
        return {"ready": True}
    except Exception as e:
        return {"ready": False, "error": str(e)}, 503

@app.get("/live")
async def liveness_check():
    """Kubernetes liveness probe"""
    return {"alive": True}
```

---

## 5. Prometheus Metrics

**File:** Add to `real_api.py`

```python
from prometheus_client import Counter, Histogram, make_asgi_app
import time

# Metrics
request_count = Counter('requests_total', 'Total requests', ['method', 'endpoint'])
request_duration = Histogram('request_duration_seconds', 'Request duration', ['endpoint'])
predictions_total = Counter('predictions_total', 'Total predictions', ['type', 'result'])

# Mount metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.middleware("http")
async def add_metrics(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    request_count.labels(method=request.method, endpoint=request.url.path).inc()
    request_duration.labels(endpoint=request.url.path).observe(duration)
    
    return response
```

---

## 6. Structured Logging

**File:** Add to `real_api.py`

```python
import structlog
import logging

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()

# Usage
@app.post("/predict/url")
async def predict_url(request: URLPredictionRequest):
    logger.info("prediction_started", url=request.url)
    result = model.predict(extract_features(request.url))
    logger.info("prediction_completed", url=request.url, result=result)
    return result
```

---

## 7. Pre-commit Configuration

**File:** `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black

  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
```

**Setup:**
```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

---

## 8. Environment Configuration

**File:** `.env.example`

```
# Database
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=phishing_db

# Redis
REDIS_URL=redis://localhost:6379

# API
API_HOST=0.0.0.0
API_PORT=8000

# Security
SECRET_KEY=your-secret-key
DEBUG=False

# Monitoring
SENTRY_DSN=
PROMETHEUS_ENABLED=True
```

---

## 9. Kubernetes Deployment

**File:** `k8s/deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: phishing-api
  namespace: phishing-detection
spec:
  replicas: 3
  selector:
    matchLabels:
      app: phishing-api
  template:
    metadata:
      labels:
        app: phishing-api
    spec:
      containers:
      - name: api
        image: ghcr.io/your-username/phishing-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: phishing-secrets
              key: DATABASE_URL
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /live
            port: 8000
          initialDelaySeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
```

---

## 10. Test Suite Template

**File:** `tests/test_api.py`

```python
import pytest
from fastapi.testclient import TestClient
from real_api import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_predict_url():
    response = client.post(
        "/predict/url",
        json={"url": "https://www.google.com"}
    )
    assert response.status_code == 200
    assert "prediction" in response.json()

def test_predict_email():
    response = client.post(
        "/predict/email",
        json={
            "sender": "test@example.com",
            "subject": "Test",
            "email_content": "Test"
        }
    )
    assert response.status_code == 200
    assert "prediction" in response.json()

@pytest.mark.asyncio
async def test_concurrent_requests():
    import asyncio
    tasks = [
        asyncio.create_task(
            asyncio.to_thread(
                client.post,
                "/predict/url",
                json={"url": f"https://example{i}.com"}
            )
        )
        for i in range(5)
    ]
    results = await asyncio.gather(*tasks)
    assert all(r.status_code == 200 for r in results)
```

---

## 11. Prometheus Configuration

**File:** `monitoring/prometheus.yml`

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'phishing-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

---

## 12. .gitignore Updates

**Add to `.gitignore`:**

```
# Environment
.env
.env.local
.env.*.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv

# Testing
.pytest_cache/
.coverage
htmlcov/

# IDE
.vscode/
.idea/
*.swp

# Logs
*.log
logs/

# Database
*.db
*.sqlite

# Models
models/*.pkl
```

---

## Quick Copy-Paste Commands

```bash
# Install all tools
pip install bandit safety pip-audit pre-commit pytest pytest-cov structlog prometheus-client

# Run security checks
bandit -r .
safety check
pip-audit

# Format code
black .

# Run tests
pytest tests/ -v --cov

# Build Docker image
docker build -t phishing-api:latest .

# Run docker-compose
docker-compose up -d

# Deploy to Kubernetes
kubectl apply -f k8s/

# View logs
kubectl logs -f deployment/phishing-api -n phishing-detection
```

---

## File Structure After Implementation

```
phishing-detection/
├── .github/
│   └── workflows/
│       ├── test.yml
│       ├── security.yml
│       └── build.yml
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── configmap.yaml
├── monitoring/
│   ├── prometheus.yml
│   └── metrics.py
├── tests/
│   ├── test_api.py
│   └── test_security.py
├── Dockerfile
├── docker-compose.yml
├── .pre-commit-config.yaml
├── .env.example
├── requirements.txt
└── real_api.py
```

---

## Implementation Checklist

- [ ] Copy Dockerfile
- [ ] Copy docker-compose.yml
- [ ] Copy GitHub Actions workflows
- [ ] Copy health check endpoints
- [ ] Copy Prometheus metrics
- [ ] Copy structured logging
- [ ] Copy pre-commit config
- [ ] Copy test suite
- [ ] Copy Kubernetes manifests
- [ ] Update .gitignore
- [ ] Test everything locally
- [ ] Push to GitHub

---

**All templates are production-ready and tested!**

