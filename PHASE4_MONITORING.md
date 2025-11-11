# Phase 4: Monitoring & Observability Implementation Guide
## Prometheus, Logging, and Health Checks (Estimated: 10-12 hours)

---

## Step 1: Add Prometheus Metrics to FastAPI

Create `monitoring/metrics.py`:

```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Request metrics
request_count = Counter(
    'phishing_requests_total',
    'Total requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'phishing_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

# Model metrics
predictions_total = Counter(
    'phishing_predictions_total',
    'Total predictions made',
    ['type', 'result']
)

prediction_confidence = Histogram(
    'phishing_prediction_confidence',
    'Prediction confidence scores',
    ['type']
)

# System metrics
active_connections = Gauge(
    'phishing_active_connections',
    'Active database connections'
)

model_load_time = Gauge(
    'phishing_model_load_time_seconds',
    'Time to load ML model'
)

cache_hits = Counter(
    'phishing_cache_hits_total',
    'Cache hits',
    ['cache_type']
)

cache_misses = Counter(
    'phishing_cache_misses_total',
    'Cache misses',
    ['cache_type']
)
```

---

## Step 2: Integrate Prometheus with FastAPI

Update `real_api.py`:

```python
from fastapi import FastAPI
from prometheus_client import make_asgi_app, CollectorRegistry
from monitoring.metrics import *
import time

app = FastAPI()

# Add Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.middleware("http")
async def add_metrics(request, call_next):
    """Middleware to track request metrics"""
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    
    # Record metrics
    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    request_duration.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response

@app.post("/predict/url")
async def predict_url(request: URLPredictionRequest):
    """Predict URL with metrics"""
    start_time = time.time()
    
    # Your prediction logic
    result = model.predict(extract_features(request.url))
    
    # Record metrics
    predictions_total.labels(
        type="url",
        result="phishing" if result["is_phishing"] else "safe"
    ).inc()
    
    prediction_confidence.labels(type="url").observe(result["confidence"])
    
    return result

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes"""
    try:
        # Check database
        db.execute("SELECT 1")
        
        # Check model
        assert model is not None
        
        # Check cache
        cache.ping()
        
        return {"ready": True}
    except Exception as e:
        return {"ready": False, "error": str(e)}, 503
```

---

## Step 3: Structured Logging

Create `monitoring/logging_config.py`:

```python
import structlog
import logging
from pythonjsonlogger import jsonlogger

def setup_logging():
    """Configure structured logging"""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter()
    handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

# Usage in code
logger = structlog.get_logger()

def example_logging():
    logger.info(
        "prediction_made",
        url="https://example.com",
        is_phishing=False,
        confidence=0.95,
        processing_time=0.123
    )
```

---

## Step 4: Prometheus Configuration

Create `monitoring/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    monitor: 'phishing-detection'

scrape_configs:
  - job_name: 'phishing-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'phishing-dashboard'
    static_configs:
      - targets: ['localhost:3000']
    metrics_path: '/metrics'

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

alerting:
  alertmanagers:
    - static_configs:
        - targets: []

rule_files:
  - 'alert_rules.yml'
```

---

## Step 5: Alert Rules

Create `monitoring/alert_rules.yml`:

```yaml
groups:
  - name: phishing_detection
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(phishing_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }}"

      - alert: SlowRequests
        expr: histogram_quantile(0.95, phishing_request_duration_seconds) > 1
        for: 5m
        annotations:
          summary: "Slow requests detected"
          description: "95th percentile latency is {{ $value }}s"

      - alert: ModelNotLoaded
        expr: phishing_model_load_time_seconds == 0
        for: 1m
        annotations:
          summary: "ML model not loaded"
          description: "Model failed to load"

      - alert: HighCacheMissRate
        expr: rate(phishing_cache_misses_total[5m]) / (rate(phishing_cache_hits_total[5m]) + rate(phishing_cache_misses_total[5m])) > 0.5
        for: 5m
        annotations:
          summary: "High cache miss rate"
          description: "Cache miss rate is {{ $value | humanizePercentage }}"
```

---

## Step 6: Distributed Tracing with Jaeger

Create `monitoring/tracing.py`:

```python
from jaeger_client import Config
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

def init_jaeger_tracer(service_name):
    """Initialize Jaeger tracer"""
    
    jaeger_exporter = JaegerExporter(
        agent_host_name="localhost",
        agent_port=6831,
    )
    
    trace.set_tracer_provider(TracerProvider())
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(jaeger_exporter)
    )
    
    return trace.get_tracer(__name__)

# Usage
tracer = init_jaeger_tracer("phishing-api")

def predict_with_tracing(url):
    with tracer.start_as_current_span("predict_url") as span:
        span.set_attribute("url", url)
        
        with tracer.start_as_current_span("extract_features"):
            features = extract_features(url)
        
        with tracer.start_as_current_span("model_predict"):
            result = model.predict(features)
        
        return result
```

---

## Step 7: Health Check Endpoints

Update `real_api.py`:

```python
from datetime import datetime
import psutil

@app.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health/detailed")
async def detailed_health():
    """Detailed health check"""
    try:
        # Check database
        db_status = "healthy"
        try:
            db.execute("SELECT 1")
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"
        
        # Check model
        model_status = "loaded" if model is not None else "not_loaded"
        
        # Check cache
        cache_status = "healthy"
        try:
            cache.ping()
        except Exception as e:
            cache_status = f"unhealthy: {str(e)}"
        
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        
        return {
            "status": "healthy" if all([
                db_status == "healthy",
                model_status == "loaded",
                cache_status == "healthy"
            ]) else "degraded",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "database": db_status,
                "model": model_status,
                "cache": cache_status
            },
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent
            }
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 503

@app.get("/ready")
async def readiness_check():
    """Kubernetes readiness probe"""
    try:
        # Check critical dependencies
        db.execute("SELECT 1")
        assert model is not None
        cache.ping()
        
        return {"ready": True}
    except Exception as e:
        return {"ready": False, "error": str(e)}, 503

@app.get("/live")
async def liveness_check():
    """Kubernetes liveness probe"""
    return {"alive": True}
```

---

## Step 8: Update docker-compose.yml

Add monitoring services:

```yaml
  jaeger:
    image: jaegertracing/all-in-one:latest
    container_name: phishing_jaeger
    ports:
      - "6831:6831/udp"
      - "16686:16686"
    networks:
      - phishing_network

  prometheus:
    image: prom/prometheus:latest
    container_name: phishing_prometheus
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./monitoring/alert_rules.yml:/etc/prometheus/alert_rules.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
    networks:
      - phishing_network
```

---

## Step 9: Grafana Dashboard (Optional)

Add to docker-compose.yml:

```yaml
  grafana:
    image: grafana/grafana:latest
    container_name: phishing_grafana
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
    ports:
      - "3001:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - phishing_network
```

---

## Verification Checklist

- [ ] Prometheus metrics endpoint accessible at `/metrics`
- [ ] Structured logging configured
- [ ] Health check endpoints working
- [ ] Readiness probe working
- [ ] Liveness probe working
- [ ] Prometheus scraping metrics
- [ ] Jaeger receiving traces
- [ ] Grafana dashboard accessible
- [ ] Alert rules configured
- [ ] Logs in JSON format

---

## Access Points

- **Prometheus:** http://localhost:9090
- **Jaeger:** http://localhost:16686
- **Grafana:** http://localhost:3001
- **Metrics:** http://localhost:8000/metrics
- **Health:** http://localhost:8000/health
- **Detailed Health:** http://localhost:8000/health/detailed

---

## Next Steps

1. Test all monitoring endpoints
2. Create Grafana dashboards
3. Configure alerts
4. Move to Phase 5: Infrastructure as Code

