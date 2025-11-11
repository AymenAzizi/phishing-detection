#!/bin/bash

# Kubernetes Deployment Script for Phishing Detection
# This script deploys the entire application to Kubernetes

set -e

echo "=========================================="
echo "🚀 Kubernetes Deployment Script"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="phishing-detection"
TIMEOUT=300

# Function to print colored output
print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Step 1: Create Namespace
print_step "Creating namespace: $NAMESPACE"
kubectl apply -f k8s/namespace.yaml
print_success "Namespace created"
echo ""

# Step 2: Create ConfigMap
print_step "Creating ConfigMap"
kubectl apply -f k8s/configmap.yaml
print_success "ConfigMap created"
echo ""

# Step 3: Create Secrets
print_step "Creating Secrets"
if [ -f "k8s/secrets.yaml" ]; then
    kubectl apply -f k8s/secrets.yaml
    print_success "Secrets created"
else
    print_warning "secrets.yaml not found. Creating from template..."
    cp k8s/secrets.yaml.example k8s/secrets.yaml
    echo "Please edit k8s/secrets.yaml with your values and run this script again"
    exit 1
fi
echo ""

# Step 4: Deploy PostgreSQL
print_step "Deploying PostgreSQL"
kubectl apply -f k8s/postgres.yaml
print_success "PostgreSQL deployment created"
print_step "Waiting for PostgreSQL to be ready (timeout: ${TIMEOUT}s)"
kubectl wait --for=condition=ready pod -l app=postgres -n $NAMESPACE --timeout=${TIMEOUT}s
print_success "PostgreSQL is ready"
echo ""

# Step 5: Deploy Redis
print_step "Deploying Redis"
kubectl apply -f k8s/redis.yaml
print_success "Redis deployment created"
print_step "Waiting for Redis to be ready (timeout: ${TIMEOUT}s)"
kubectl wait --for=condition=ready pod -l app=redis -n $NAMESPACE --timeout=${TIMEOUT}s
print_success "Redis is ready"
echo ""

# Step 6: Deploy API
print_step "Deploying API"
kubectl apply -f k8s/api-deployment.yaml
print_success "API deployment created"
print_step "Waiting for API to be ready (timeout: ${TIMEOUT}s)"
kubectl wait --for=condition=ready pod -l app=api -n $NAMESPACE --timeout=${TIMEOUT}s
print_success "API is ready"
echo ""

# Step 7: Deploy Dashboard
print_step "Deploying Dashboard"
kubectl apply -f k8s/dashboard-deployment.yaml
print_success "Dashboard deployment created"
print_step "Waiting for Dashboard to be ready (timeout: ${TIMEOUT}s)"
kubectl wait --for=condition=ready pod -l app=dashboard -n $NAMESPACE --timeout=${TIMEOUT}s
print_success "Dashboard is ready"
echo ""

# Step 8: Deploy Ingress
print_step "Deploying Ingress"
kubectl apply -f k8s/ingress.yaml
print_success "Ingress created"
echo ""

# Step 9: Deploy HPA
print_step "Deploying Horizontal Pod Autoscaler"
kubectl apply -f k8s/hpa.yaml
print_success "HPA created"
echo ""

# Verification
print_step "Verifying deployment"
echo ""
echo "Namespaces:"
kubectl get namespaces | grep $NAMESPACE
echo ""

echo "Pods:"
kubectl get pods -n $NAMESPACE
echo ""

echo "Services:"
kubectl get svc -n $NAMESPACE
echo ""

echo "Deployments:"
kubectl get deployments -n $NAMESPACE
echo ""

echo "Ingress:"
kubectl get ingress -n $NAMESPACE
echo ""

echo "HPA:"
kubectl get hpa -n $NAMESPACE
echo ""

# Get service information
print_step "Service Information"
API_SERVICE=$(kubectl get svc api -n $NAMESPACE -o jsonpath='{.spec.clusterIP}')
DASHBOARD_SERVICE=$(kubectl get svc dashboard -n $NAMESPACE -o jsonpath='{.spec.clusterIP}')

echo "API Service IP: $API_SERVICE"
echo "Dashboard Service IP: $DASHBOARD_SERVICE"
echo ""

# Port forwarding instructions
print_step "Port Forwarding Instructions"
echo "To access services locally, use:"
echo ""
echo "API (port 8000):"
echo "  kubectl port-forward svc/api 8000:8000 -n $NAMESPACE"
echo ""
echo "Dashboard (port 3000):"
echo "  kubectl port-forward svc/dashboard 3000:3000 -n $NAMESPACE"
echo ""
echo "PostgreSQL (port 5432):"
echo "  kubectl port-forward svc/postgres 5432:5432 -n $NAMESPACE"
echo ""
echo "Redis (port 6379):"
echo "  kubectl port-forward svc/redis 6379:6379 -n $NAMESPACE"
echo ""

# Testing instructions
print_step "Testing Instructions"
echo "Test API health:"
echo "  kubectl exec -it deployment/api -n $NAMESPACE -- curl http://localhost:8000/health"
echo ""
echo "Test API info:"
echo "  kubectl exec -it deployment/api -n $NAMESPACE -- curl http://localhost:8000/info"
echo ""

# Cleanup instructions
print_step "Cleanup Instructions"
echo "To delete the entire deployment:"
echo "  kubectl delete namespace $NAMESPACE"
echo ""

print_success "=========================================="
print_success "✅ Kubernetes Deployment Complete!"
print_success "=========================================="
echo ""
echo "Your application is now running on Kubernetes!"
echo "Namespace: $NAMESPACE"
echo ""
echo "Next steps:"
echo "1. Verify all pods are running: kubectl get pods -n $NAMESPACE"
echo "2. Check logs: kubectl logs -f deployment/api -n $NAMESPACE"
echo "3. Port forward to access services locally"
echo "4. Test API endpoints"
echo ""

