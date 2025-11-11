# Phase 3: Containerization Implementation Guide
## Docker & Docker Compose Setup (Estimated: 5-6 hours)

---

## Step 1: Create Dockerfile for API

Create `Dockerfile`:

```dockerfile
# Multi-stage build for smaller image size
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Set environment variables
ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "real_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Step 2: Create Dockerfile for Dashboard

Create `Dockerfile.dashboard`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:3000')"

EXPOSE 3000

CMD ["uvicorn", "dashboard_server:dashboard_app", "--host", "0.0.0.0", "--port", "3000"]
```

---

## Step 3: Create .dockerignore

Create `.dockerignore`:

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv
.git
.gitignore
.dockerignore
.env
.env.local
*.db
*.log
logs/
.pytest_cache
.mypy_cache
.coverage
htmlcov/
dist/
build/
*.egg-info/
.DS_Store
node_modules/
.idea/
.vscode/
*.swp
*.swo
*~
.tmp/
```

---

## Step 4: Create docker-compose.yml

Create `docker-compose.yml`:

```yaml
version: '3.9'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:14-alpine
    container_name: phishing_postgres
    environment:
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-postgres}
      POSTGRES_DB: ${DB_NAME:-phishing_db}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-postgres}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - phishing_network

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: phishing_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - phishing_network

  # Backend API
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: phishing_api
    environment:
      DATABASE_URL: postgresql://${DB_USER:-postgres}:${DB_PASSWORD:-postgres}@postgres:5432/${DB_NAME:-phishing_db}
      REDIS_URL: redis://redis:6379
      PYTHONUNBUFFERED: 1
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./models:/app/models
      - ./logs:/app/logs
    networks:
      - phishing_network
    restart: unless-stopped

  # Frontend Dashboard
  dashboard:
    build:
      context: .
      dockerfile: Dockerfile.dashboard
    container_name: phishing_dashboard
    environment:
      API_URL: http://api:8000
      PYTHONUNBUFFERED: 1
    ports:
      - "3000:3000"
    depends_on:
      - api
    volumes:
      - ./dashboard:/app/dashboard
    networks:
      - phishing_network
    restart: unless-stopped

  # Prometheus Monitoring (Optional)
  prometheus:
    image: prom/prometheus:latest
    container_name: phishing_prometheus
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
    networks:
      - phishing_network
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  prometheus_data:

networks:
  phishing_network:
    driver: bridge
```

---

## Step 5: Create .env.example

Create `.env.example`:

```
# Database Configuration
DB_HOST=postgres
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=phishing_db

# Redis Configuration
REDIS_URL=redis://redis:6379

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Dashboard Configuration
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=3000

# Security
SECRET_KEY=your-secret-key-here
DEBUG=False

# Monitoring
SENTRY_DSN=
PROMETHEUS_ENABLED=True

# ML Model
MODEL_PATH=/app/models/best_phishing_model.pkl
```

---

## Step 6: Build and Run Locally

```bash
# Copy environment file
cp .env.example .env

# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Remove volumes (careful!)
docker-compose down -v
```

---

## Step 7: Docker Compose Commands Reference

```bash
# Build specific service
docker-compose build api

# Run specific service
docker-compose up -d api

# View service logs
docker-compose logs -f api

# Execute command in container
docker-compose exec api bash

# Run tests in container
docker-compose exec api pytest tests/

# Check service status
docker-compose ps

# Remove all containers and volumes
docker-compose down -v

# Rebuild without cache
docker-compose build --no-cache
```

---

## Step 8: Optimize Docker Images

### Reduce Image Size

```dockerfile
# Use alpine images (smaller)
FROM python:3.11-alpine

# Multi-stage builds (shown above)

# Remove unnecessary files
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Use .dockerignore (shown above)
```

### Image Size Comparison
- `python:3.11` → ~900MB
- `python:3.11-slim` → ~150MB
- `python:3.11-alpine` → ~50MB

---

## Step 9: Security Best Practices

```dockerfile
# ✅ DO: Use specific versions
FROM python:3.11-slim

# ✅ DO: Run as non-root user
RUN useradd -m -u 1000 appuser
USER appuser

# ✅ DO: Use health checks
HEALTHCHECK --interval=30s CMD curl -f http://localhost:8000/health

# ✅ DO: Set environment variables
ENV PYTHONUNBUFFERED=1

# ❌ DON'T: Run as root
# ❌ DON'T: Use latest tags
# ❌ DON'T: Store secrets in images
# ❌ DON'T: Install unnecessary packages
```

---

## Step 10: Push to Docker Hub

```bash
# Login to Docker Hub
docker login

# Tag image
docker tag phishing_api:latest YOUR_USERNAME/phishing-api:latest

# Push image
docker push YOUR_USERNAME/phishing-api:latest

# Pull image
docker pull YOUR_USERNAME/phishing-api:latest
```

---

## Verification Checklist

- [ ] Dockerfile created and builds successfully
- [ ] Dockerfile.dashboard created and builds successfully
- [ ] .dockerignore created
- [ ] docker-compose.yml created
- [ ] .env.example created
- [ ] Services start with `docker-compose up`
- [ ] API accessible at http://localhost:8000
- [ ] Dashboard accessible at http://localhost:3000
- [ ] Database connection works
- [ ] Redis connection works
- [ ] Health checks pass
- [ ] Images pushed to Docker Hub (optional)

---

## Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Database Connection Failed
```bash
# Check database logs
docker-compose logs postgres

# Verify database is running
docker-compose ps postgres
```

### Out of Disk Space
```bash
# Clean up Docker
docker system prune -a

# Remove unused volumes
docker volume prune
```

---

## Next Steps

1. Test docker-compose locally
2. Verify all services communicate
3. Create deployment documentation
4. Move to Phase 4: Monitoring & Observability

