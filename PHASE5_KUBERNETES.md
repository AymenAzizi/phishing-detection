# Phase 5: Infrastructure as Code - Kubernetes Implementation
## Kubernetes Manifests & Deployment (Estimated: 6-8 hours)

---

## Step 1: Create Kubernetes Namespace

Create `k8s/namespace.yaml`:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: phishing-detection
  labels:
    name: phishing-detection
```

---

## Step 2: Create ConfigMap for Configuration

Create `k8s/configmap.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: phishing-config
  namespace: phishing-detection
data:
  API_HOST: "0.0.0.0"
  API_PORT: "8000"
  DASHBOARD_PORT: "3000"
  LOG_LEVEL: "INFO"
  PROMETHEUS_ENABLED: "true"
  JAEGER_ENABLED: "true"
  DATABASE_HOST: "postgres"
  DATABASE_PORT: "5432"
  DATABASE_NAME: "phishing_db"
  REDIS_HOST: "redis"
  REDIS_PORT: "6379"
```

---

## Step 3: Create Secrets for Sensitive Data

Create `k8s/secrets.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: phishing-secrets
  namespace: phishing-detection
type: Opaque
stringData:
  DATABASE_USER: postgres
  DATABASE_PASSWORD: your-secure-password
  SECRET_KEY: your-secret-key
  API_KEY: your-api-key
  SENTRY_DSN: your-sentry-dsn
```

**Note:** In production, use external secret management (HashiCorp Vault, AWS Secrets Manager)

---

## Step 4: Create PostgreSQL Deployment

Create `k8s/postgres.yaml`:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: phishing-detection
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: phishing-detection
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:14-alpine
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: phishing-secrets
              key: DATABASE_USER
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: phishing-secrets
              key: DATABASE_PASSWORD
        - name: POSTGRES_DB
          valueFrom:
            configMapKeyRef:
              name: phishing-config
              key: DATABASE_NAME
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        livenessProbe:
          exec:
            command:
            - /bin/sh
            - -c
            - pg_isready -U postgres
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - /bin/sh
            - -c
            - pg_isready -U postgres
          initialDelaySeconds: 5
          periodSeconds: 10
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: phishing-detection
spec:
  selector:
    app: postgres
  ports:
  - protocol: TCP
    port: 5432
    targetPort: 5432
  type: ClusterIP
```

---

## Step 5: Create Redis Deployment

Create `k8s/redis.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: phishing-detection
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        livenessProbe:
          exec:
            command:
            - redis-cli
            - ping
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - redis-cli
            - ping
          initialDelaySeconds: 5
          periodSeconds: 10

---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: phishing-detection
spec:
  selector:
    app: redis
  ports:
  - protocol: TCP
    port: 6379
    targetPort: 6379
  type: ClusterIP
```

---

## Step 6: Create API Deployment

Create `k8s/api-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: phishing-api
  namespace: phishing-detection
  labels:
    app: phishing-api
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
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
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
          name: http
        - containerPort: 9090
          name: metrics
        env:
        - name: DATABASE_URL
          value: "postgresql://$(DB_USER):$(DB_PASSWORD)@postgres:5432/$(DB_NAME)"
        - name: DB_USER
          valueFrom:
            secretKeyRef:
              name: phishing-secrets
              key: DATABASE_USER
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: phishing-secrets
              key: DATABASE_PASSWORD
        - name: DB_NAME
          valueFrom:
            configMapKeyRef:
              name: phishing-config
              key: DATABASE_NAME
        - name: REDIS_URL
          value: "redis://redis:6379"
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: phishing-config
              key: LOG_LEVEL
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
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: models
          mountPath: /app/models
      volumes:
      - name: models
        emptyDir: {}

---
apiVersion: v1
kind: Service
metadata:
  name: phishing-api
  namespace: phishing-detection
spec:
  selector:
    app: phishing-api
  ports:
  - name: http
    protocol: TCP
    port: 8000
    targetPort: 8000
  - name: metrics
    protocol: TCP
    port: 9090
    targetPort: 9090
  type: LoadBalancer
```

---

## Step 7: Create Dashboard Deployment

Create `k8s/dashboard-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: phishing-dashboard
  namespace: phishing-detection
spec:
  replicas: 2
  selector:
    matchLabels:
      app: phishing-dashboard
  template:
    metadata:
      labels:
        app: phishing-dashboard
    spec:
      containers:
      - name: dashboard
        image: ghcr.io/your-username/phishing-dashboard:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 3000
        env:
        - name: API_URL
          value: "http://phishing-api:8000"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: phishing-dashboard
  namespace: phishing-detection
spec:
  selector:
    app: phishing-dashboard
  ports:
  - protocol: TCP
    port: 3000
    targetPort: 3000
  type: LoadBalancer
```

---

## Step 8: Create Ingress

Create `k8s/ingress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: phishing-ingress
  namespace: phishing-detection
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - phishing-api.example.com
    - phishing-dashboard.example.com
    secretName: phishing-tls
  rules:
  - host: phishing-api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: phishing-api
            port:
              number: 8000
  - host: phishing-dashboard.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: phishing-dashboard
            port:
              number: 3000
```

---

## Step 9: Create HorizontalPodAutoscaler

Create `k8s/hpa.yaml`:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: phishing-api-hpa
  namespace: phishing-detection
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: phishing-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## Step 10: Deploy to Kubernetes

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create secrets and config
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml

# Deploy databases
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml

# Wait for databases
kubectl wait --for=condition=ready pod -l app=postgres -n phishing-detection --timeout=300s

# Deploy applications
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/dashboard-deployment.yaml

# Create ingress
kubectl apply -f k8s/ingress.yaml

# Create autoscaler
kubectl apply -f k8s/hpa.yaml

# Check status
kubectl get all -n phishing-detection
```

---

## Useful Kubectl Commands

```bash
# View deployments
kubectl get deployments -n phishing-detection

# View pods
kubectl get pods -n phishing-detection

# View services
kubectl get svc -n phishing-detection

# View logs
kubectl logs -f deployment/phishing-api -n phishing-detection

# Port forward
kubectl port-forward svc/phishing-api 8000:8000 -n phishing-detection

# Execute command in pod
kubectl exec -it pod/phishing-api-xxx -n phishing-detection -- bash

# Describe pod
kubectl describe pod/phishing-api-xxx -n phishing-detection

# Delete deployment
kubectl delete deployment phishing-api -n phishing-detection
```

---

## Verification Checklist

- [ ] Namespace created
- [ ] ConfigMap created
- [ ] Secrets created
- [ ] PostgreSQL deployed and running
- [ ] Redis deployed and running
- [ ] API deployed with 3 replicas
- [ ] Dashboard deployed with 2 replicas
- [ ] Services accessible
- [ ] Ingress configured
- [ ] HPA configured
- [ ] Health checks passing
- [ ] Logs accessible

---

## Next Steps

1. Test Kubernetes deployment locally with Minikube
2. Deploy to cloud (AWS EKS, GCP GKE, Azure AKS)
3. Configure monitoring
4. Set up CI/CD for Kubernetes
5. Move to Phase 6: Advanced Features

