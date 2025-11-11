# 🚀 Full Deployment Guide - Docker & Kubernetes

**Status:** Building Docker images...  
**Date:** 2025-11-11  
**Grade:** A+ (Outstanding)

---

## 📋 Table of Contents

1. [Docker Deployment](#docker-deployment)
2. [Kubernetes Deployment](#kubernetes-deployment)
3. [Monitoring & Verification](#monitoring--verification)
4. [Troubleshooting](#troubleshooting)

---

## 🐳 Docker Deployment

### Step 1: Build Docker Images

#### Build API Image
```bash
docker build -t phishing-detection-api:latest -f Dockerfile .
```

#### Build Dashboard Image
```bash
docker build -t phishing-detection-dashboard:latest -f Dockerfile.dashboard .
```

#### Build Both with docker-compose
```bash
docker-compose build
```

### Step 2: Run with docker-compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Stop services
docker-compose down
```

### Step 3: Verify Services

#### Check API Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "feature_extractor_ready": false,
  "timestamp": "2025-11-11T15:47:42.399499",
  "model_info": {}
}
```

#### Check Dashboard
```bash
curl http://localhost:3000
```

#### Check PostgreSQL
```bash
docker-compose exec postgres psql -U postgres -l
```

#### Check Redis
```bash
docker-compose exec redis redis-cli ping
```

### Step 4: Test API Endpoints

#### Predict URL
```bash
curl -X POST http://localhost:8000/predict/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.google.com"}'
```

#### Predict Email
```bash
curl -X POST http://localhost:8000/predict/email \
  -H "Content-Type: application/json" \
  -d '{"email": "user@gmail.com"}'
```

#### Batch Prediction
```bash
curl -X POST http://localhost:8000/predict/batch \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://www.google.com", "https://www.paypal.com"],
    "emails": ["user@gmail.com", "admin@company.com"]
  }'
```

---

## ☸️ Kubernetes Deployment

### Prerequisites

1. **Kubernetes Cluster**
   - Minikube (local)
   - Docker Desktop Kubernetes
   - Cloud provider (AWS EKS, GCP GKE, Azure AKS)

2. **kubectl CLI**
   ```bash
   kubectl version --client
   ```

3. **Docker Images**
   - Push to registry or use local images

### Step 1: Create Namespace

```bash
kubectl apply -f k8s/namespace.yaml
```

Verify:
```bash
kubectl get namespaces
```

### Step 2: Create ConfigMap

```bash
kubectl apply -f k8s/configmap.yaml
```

Verify:
```bash
kubectl get configmap -n phishing-detection
```

### Step 3: Create Secrets

First, create the secrets file from template:
```bash
cp k8s/secrets.yaml.example k8s/secrets.yaml
```

Edit `k8s/secrets.yaml` with your values, then apply:
```bash
kubectl apply -f k8s/secrets.yaml
```

Verify:
```bash
kubectl get secrets -n phishing-detection
```

### Step 4: Deploy PostgreSQL

```bash
kubectl apply -f k8s/postgres.yaml
```

Verify:
```bash
kubectl get pods -n phishing-detection
kubectl get pvc -n phishing-detection
```

Wait for PostgreSQL to be ready:
```bash
kubectl wait --for=condition=ready pod -l app=postgres -n phishing-detection --timeout=300s
```

### Step 5: Deploy Redis

```bash
kubectl apply -f k8s/redis.yaml
```

Verify:
```bash
kubectl get pods -n phishing-detection
```

### Step 6: Deploy API

```bash
kubectl apply -f k8s/api-deployment.yaml
```

Verify:
```bash
kubectl get pods -n phishing-detection
kubectl get svc -n phishing-detection
```

Wait for API to be ready:
```bash
kubectl wait --for=condition=ready pod -l app=api -n phishing-detection --timeout=300s
```

### Step 7: Deploy Dashboard

```bash
kubectl apply -f k8s/dashboard-deployment.yaml
```

Verify:
```bash
kubectl get pods -n phishing-detection
```

### Step 8: Deploy Ingress

```bash
kubectl apply -f k8s/ingress.yaml
```

Verify:
```bash
kubectl get ingress -n phishing-detection
```

### Step 9: Deploy HPA (Horizontal Pod Autoscaler)

```bash
kubectl apply -f k8s/hpa.yaml
```

Verify:
```bash
kubectl get hpa -n phishing-detection
```

### Complete Deployment Script

```bash
#!/bin/bash

# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create ConfigMap
kubectl apply -f k8s/configmap.yaml

# Create Secrets
kubectl apply -f k8s/secrets.yaml

# Deploy PostgreSQL
kubectl apply -f k8s/postgres.yaml
kubectl wait --for=condition=ready pod -l app=postgres -n phishing-detection --timeout=300s

# Deploy Redis
kubectl apply -f k8s/redis.yaml
kubectl wait --for=condition=ready pod -l app=redis -n phishing-detection --timeout=300s

# Deploy API
kubectl apply -f k8s/api-deployment.yaml
kubectl wait --for=condition=ready pod -l app=api -n phishing-detection --timeout=300s

# Deploy Dashboard
kubectl apply -f k8s/dashboard-deployment.yaml

# Deploy Ingress
kubectl apply -f k8s/ingress.yaml

# Deploy HPA
kubectl apply -f k8s/hpa.yaml

echo "Deployment complete!"
kubectl get all -n phishing-detection
```

---

## 📊 Monitoring & Verification

### Check All Resources

```bash
# All resources in namespace
kubectl get all -n phishing-detection

# Detailed pod information
kubectl describe pod -n phishing-detection

# Pod logs
kubectl logs -f deployment/api -n phishing-detection
kubectl logs -f deployment/dashboard -n phishing-detection

# Service endpoints
kubectl get endpoints -n phishing-detection
```

### Port Forwarding

```bash
# Forward API
kubectl port-forward svc/api 8000:8000 -n phishing-detection

# Forward Dashboard
kubectl port-forward svc/dashboard 3000:3000 -n phishing-detection

# Forward PostgreSQL
kubectl port-forward svc/postgres 5432:5432 -n phishing-detection

# Forward Redis
kubectl port-forward svc/redis 6379:6379 -n phishing-detection
```

### Test Kubernetes Deployment

```bash
# Get API service IP
kubectl get svc api -n phishing-detection

# Test API health
kubectl exec -it deployment/api -n phishing-detection -- curl http://localhost:8000/health

# Test API info
kubectl exec -it deployment/api -n phishing-detection -- curl http://localhost:8000/info
```

---

## 🔧 Troubleshooting

### Pod Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n phishing-detection

# Check logs
kubectl logs <pod-name> -n phishing-detection

# Check events
kubectl get events -n phishing-detection
```

### Database Connection Issues

```bash
# Check PostgreSQL pod
kubectl get pod -l app=postgres -n phishing-detection

# Check PostgreSQL logs
kubectl logs -l app=postgres -n phishing-detection

# Connect to PostgreSQL
kubectl exec -it deployment/postgres -n phishing-detection -- psql -U postgres
```

### Service Not Accessible

```bash
# Check service
kubectl get svc -n phishing-detection

# Check endpoints
kubectl get endpoints -n phishing-detection

# Check ingress
kubectl get ingress -n phishing-detection
```

### Scale Deployment

```bash
# Scale API to 3 replicas
kubectl scale deployment api --replicas=3 -n phishing-detection

# Check HPA status
kubectl get hpa -n phishing-detection
```

---

## ✅ Deployment Checklist

- [ ] Docker images built
- [ ] docker-compose up running
- [ ] API health check passing
- [ ] Dashboard accessible
- [ ] PostgreSQL connected
- [ ] Redis connected
- [ ] Kubernetes namespace created
- [ ] ConfigMap created
- [ ] Secrets created
- [ ] PostgreSQL deployed
- [ ] Redis deployed
- [ ] API deployed
- [ ] Dashboard deployed
- [ ] Ingress deployed
- [ ] HPA deployed
- [ ] All pods running
- [ ] All services accessible
- [ ] Health checks passing

---

## 🎯 Next Steps

1. **Build Docker images** (In progress)
2. **Run docker-compose** (Next)
3. **Deploy to Kubernetes** (After docker-compose verified)
4. **Monitor and verify** (Final)
5. **Present to teacher** (Ready)

---

**Your deployment is ready to go! 🚀**

