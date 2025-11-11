# Deployment Guide

This guide covers deployment options for the Phishing Detection System in various environments.

## 🐳 Docker Deployment

### Quick Start with Docker Compose

1. **Clone and setup**
```bash
git clone <repository-url>
cd phishing-detection-system
cp .env.example .env
```

2. **Configure environment**
Edit `.env` file with your settings:
```bash
# Required settings
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://phishing_user:phishing_pass@db:5432/phishing_db
REDIS_URL=redis://redis:6379

# Optional email settings
IMAP_SERVER=imap.gmail.com
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

3. **Start services**
```bash
# Development
docker-compose up -d

# Production
docker-compose -f docker-compose.prod.yml up -d
```

4. **Verify deployment**
```bash
# Check service health
curl http://localhost:8000/health

# Access dashboard
open http://localhost:3000
```

### Service Architecture

The Docker deployment includes:

- **API Service**: FastAPI application (Port 8000)
- **Database**: PostgreSQL 14 (Port 5432)
- **Cache**: Redis 7 (Port 6379)
- **Monitoring**: Prometheus (Port 9090)
- **Dashboard**: Grafana (Port 3000)

### Scaling Services

```bash
# Scale API instances
docker-compose up --scale api=3

# Scale with load balancer
docker-compose -f docker-compose.lb.yml up -d
```

## ☸️ Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (1.20+)
- kubectl configured
- Helm 3.x (optional)

### Manual Deployment

1. **Create namespace**
```bash
kubectl create namespace phishing-detection
```

2. **Deploy database**
```bash
kubectl apply -f k8s/postgres/
```

3. **Deploy Redis**
```bash
kubectl apply -f k8s/redis/
```

4. **Deploy API**
```bash
kubectl apply -f k8s/api/
```

5. **Deploy monitoring**
```bash
kubectl apply -f k8s/monitoring/
```

### Helm Deployment

```bash
# Add repository
helm repo add phishing-detection ./helm

# Install
helm install phishing-detection phishing-detection/phishing-detection \
  --namespace phishing-detection \
  --create-namespace \
  --values values.prod.yaml
```

### Configuration

Create `values.prod.yaml`:
```yaml
api:
  replicaCount: 3
  image:
    tag: "latest"
  resources:
    requests:
      memory: "512Mi"
      cpu: "250m"
    limits:
      memory: "1Gi"
      cpu: "500m"

database:
  enabled: true
  persistence:
    size: 20Gi

redis:
  enabled: true
  persistence:
    size: 5Gi

monitoring:
  enabled: true
  grafana:
    adminPassword: "secure-password"
```

## 🌐 Cloud Deployment

### AWS ECS

1. **Build and push image**
```bash
# Build image
docker build -t phishing-detection:latest .

# Tag for ECR
docker tag phishing-detection:latest 123456789.dkr.ecr.us-west-2.amazonaws.com/phishing-detection:latest

# Push to ECR
docker push 123456789.dkr.ecr.us-west-2.amazonaws.com/phishing-detection:latest
```

2. **Create ECS task definition**
```json
{
  "family": "phishing-detection",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::123456789:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "api",
      "image": "123456789.dkr.ecr.us-west-2.amazonaws.com/phishing-detection:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://user:pass@rds-endpoint:5432/phishing_db"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/phishing-detection",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

3. **Create ECS service**
```bash
aws ecs create-service \
  --cluster phishing-detection-cluster \
  --service-name phishing-detection-service \
  --task-definition phishing-detection:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"
```

### Google Cloud Run

1. **Deploy to Cloud Run**
```bash
# Build and deploy
gcloud run deploy phishing-detection \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL="postgresql://user:pass@/phishing_db?host=/cloudsql/project:region:instance"
```

2. **Configure Cloud SQL**
```bash
# Create Cloud SQL instance
gcloud sql instances create phishing-db \
  --database-version POSTGRES_14 \
  --tier db-f1-micro \
  --region us-central1

# Create database
gcloud sql databases create phishing_db --instance phishing-db
```

### Azure Container Instances

```bash
# Create resource group
az group create --name phishing-detection --location eastus

# Deploy container
az container create \
  --resource-group phishing-detection \
  --name phishing-detection-api \
  --image phishing-detection:latest \
  --cpu 1 \
  --memory 2 \
  --ports 8000 \
  --environment-variables \
    DATABASE_URL="postgresql://user:pass@postgres-server:5432/phishing_db" \
    REDIS_URL="redis://redis-server:6379"
```

## 🔧 Production Configuration

### Environment Variables

```bash
# Security
SECRET_KEY=your-256-bit-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=postgresql://user:password@host:5432/database
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Redis
REDIS_URL=redis://host:6379
REDIS_POOL_SIZE=10

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
MAX_CONCURRENT_REQUESTS=100

# Monitoring
ENABLE_METRICS=true
LOG_LEVEL=INFO
SENTRY_DSN=https://your-sentry-dsn

# Email (optional)
IMAP_SERVER=imap.gmail.com
EMAIL_USERNAME=monitoring@company.com
EMAIL_PASSWORD=app-specific-password
```

### Performance Tuning

1. **API Workers**
```bash
# Calculate workers: (2 x CPU cores) + 1
API_WORKERS=9  # For 4-core machine
```

2. **Database Connection Pool**
```bash
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
DATABASE_POOL_TIMEOUT=30
```

3. **Redis Configuration**
```bash
REDIS_POOL_SIZE=10
REDIS_TIMEOUT=5
```

### Security Hardening

1. **SSL/TLS Configuration**
```nginx
server {
    listen 443 ssl http2;
    server_name api.phishing-detection.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

2. **Firewall Rules**
```bash
# Allow only necessary ports
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw deny 8000/tcp   # Block direct API access
```

3. **Database Security**
```sql
-- Create dedicated user
CREATE USER phishing_api WITH PASSWORD 'secure-password';
GRANT CONNECT ON DATABASE phishing_db TO phishing_api;
GRANT USAGE ON SCHEMA public TO phishing_api;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO phishing_api;
```

## 📊 Monitoring Setup

### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'phishing-detection-api'
    static_configs:
      - targets: ['api:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s
```

### Grafana Dashboards

Import dashboard JSON files:
- `monitoring/grafana/api-dashboard.json`
- `monitoring/grafana/ml-model-dashboard.json`
- `monitoring/grafana/system-dashboard.json`

### Alerting Rules

```yaml
# alerts.yml
groups:
  - name: phishing-detection
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          
      - alert: ModelAccuracyDrop
        expr: model_accuracy < 0.9
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Model accuracy below threshold"
```

## 🔄 CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest
          
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: |
          docker build -t phishing-detection:${{ github.sha }} .
          docker tag phishing-detection:${{ github.sha }} phishing-detection:latest
          
  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: |
          # Deploy to your production environment
          kubectl set image deployment/api api=phishing-detection:${{ github.sha }}
```

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Errors**
```bash
# Check database connectivity
docker exec -it postgres psql -U phishing_user -d phishing_db -c "SELECT 1;"

# Check logs
docker logs phishing-detection-api
```

2. **Memory Issues**
```bash
# Monitor memory usage
docker stats

# Increase memory limits
docker-compose up --scale api=2 -d
```

3. **Model Loading Errors**
```bash
# Check model files
ls -la models/
docker exec -it api ls -la /app/models/

# Verify model format
python -c "import joblib; print(joblib.load('models/best_model.pkl'))"
```

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Database health
curl http://localhost:8000/health/ready

# Detailed system status
curl http://localhost:8000/health/detailed
```

### Log Analysis

```bash
# View API logs
docker logs -f phishing-detection-api

# Search for errors
docker logs phishing-detection-api 2>&1 | grep ERROR

# Monitor in real-time
tail -f logs/api.log | jq '.'
```

## 📈 Scaling Guidelines

### Horizontal Scaling

- **API**: Scale based on CPU/memory usage
- **Database**: Use read replicas for read-heavy workloads
- **Cache**: Use Redis Cluster for high availability

### Vertical Scaling

- **Memory**: 2GB minimum, 4GB recommended
- **CPU**: 2 cores minimum, 4 cores recommended
- **Storage**: SSD recommended for database

### Load Testing

```bash
# Install artillery
npm install -g artillery

# Run load test
artillery run load-test.yml

# Monitor during test
watch -n 1 'curl -s http://localhost:8000/metrics | grep http_requests'
```

This deployment guide provides comprehensive instructions for deploying the Phishing Detection System in various environments with proper security, monitoring, and scaling considerations.
