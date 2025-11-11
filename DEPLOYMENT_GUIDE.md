# Deployment Guide - Phishing Detection Platform

## Quick Start

### Local Development with Docker Compose

```bash
# 1. Clone the repository
git clone <repository-url>
cd phishing-detection

# 2. Create environment file
cp .env.example .env

# 3. Start all services
docker-compose up -d

# 4. Verify services
docker-compose ps

# 5. Access services
- API: http://localhost:8000
- Dashboard: http://localhost:3000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001
```

### Kubernetes Deployment

#### Prerequisites
- Kubernetes cluster (1.20+)
- kubectl configured
- Docker images pushed to registry

#### Step 1: Create Namespace and Secrets

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create secrets (update with real values)
cp k8s/secrets.yaml.example k8s/secrets.yaml
# Edit k8s/secrets.yaml with your credentials
kubectl apply -f k8s/secrets.yaml
```

#### Step 2: Deploy Infrastructure

```bash
# Deploy ConfigMaps
kubectl apply -f k8s/configmap.yaml

# Deploy PostgreSQL
kubectl apply -f k8s/postgres.yaml

# Deploy Redis
kubectl apply -f k8s/redis.yaml

# Wait for services to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n phishing-detection --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n phishing-detection --timeout=300s
```

#### Step 3: Deploy Applications

```bash
# Deploy API
kubectl apply -f k8s/api-deployment.yaml

# Deploy Dashboard
kubectl apply -f k8s/dashboard-deployment.yaml

# Deploy Ingress
kubectl apply -f k8s/ingress.yaml

# Deploy Autoscaling
kubectl apply -f k8s/hpa.yaml
```

#### Step 4: Verify Deployment

```bash
# Check all pods
kubectl get pods -n phishing-detection

# Check services
kubectl get svc -n phishing-detection

# Check ingress
kubectl get ingress -n phishing-detection

# View logs
kubectl logs -f deployment/phishing-api -n phishing-detection
```

## Health Checks

### API Health Endpoints

```bash
# Basic health check
curl http://localhost:8000/health

# Readiness check
curl http://localhost:8000/ready

# Liveness check
curl http://localhost:8000/live

# Service info
curl http://localhost:8000/info

# Prometheus metrics
curl http://localhost:8000/metrics
```

## Monitoring

### Prometheus

Access at: http://localhost:9090

Key metrics:
- `url_predictions_total` - Total predictions
- `prediction_duration_seconds` - Processing time
- `active_predictions` - Current predictions

### Grafana

Access at: http://localhost:3001
- Default credentials: admin/admin
- Add Prometheus as data source
- Import dashboards

## Scaling

### Manual Scaling

```bash
# Scale API to 5 replicas
kubectl scale deployment phishing-api --replicas=5 -n phishing-detection

# Scale Dashboard to 3 replicas
kubectl scale deployment phishing-dashboard --replicas=3 -n phishing-detection
```

### Autoscaling

HPA is configured to automatically scale based on:
- CPU utilization (70% for API, 75% for Dashboard)
- Memory utilization (80% for API, 85% for Dashboard)

## Troubleshooting

### Pod not starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n phishing-detection

# Check logs
kubectl logs <pod-name> -n phishing-detection
```

### Database connection issues

```bash
# Test database connection
kubectl exec -it deployment/phishing-api -n phishing-detection -- \
  python -c "import psycopg2; psycopg2.connect('postgresql://...')"
```

### Redis connection issues

```bash
# Test Redis connection
kubectl exec -it deployment/phishing-api -n phishing-detection -- \
  redis-cli -h redis ping
```

## Backup and Recovery

### Database Backup

```bash
# Create backup
kubectl exec -it deployment/postgres -n phishing-detection -- \
  pg_dump -U postgres phishing_db > backup.sql

# Restore backup
kubectl exec -i deployment/postgres -n phishing-detection -- \
  psql -U postgres phishing_db < backup.sql
```

## Security

- All secrets are stored in Kubernetes Secrets
- TLS/SSL enabled via cert-manager
- Network policies can be added for pod-to-pod communication
- RBAC configured for service accounts

## Performance Tuning

### Resource Limits

Adjust in deployment files:
- API: 512Mi memory, 250m CPU (requests), 1Gi/500m (limits)
- Dashboard: 256Mi memory, 100m CPU (requests), 512Mi/250m (limits)

### Replica Count

Adjust in deployment files:
- API: 3 replicas (min), 10 (max with HPA)
- Dashboard: 2 replicas (min), 5 (max with HPA)

## Cleanup

```bash
# Delete all resources
kubectl delete namespace phishing-detection

# Or delete specific resources
kubectl delete -f k8s/
```

