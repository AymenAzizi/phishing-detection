# Phase 2: CI/CD Pipeline Implementation Guide
## GitHub Actions Automation (Estimated: 8-10 hours)

---

## Overview
Create automated workflows for testing, building, and deploying your application.

---

## Step 1: Testing Workflow

Create `.github/workflows/test.yml`:

```yaml
name: Tests & Code Quality

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11']
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        cache: 'pip'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-asyncio
    
    - name: Lint with flake8
      run: |
        pip install flake8
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=100 --statistics
    
    - name: Type check with mypy
      run: |
        pip install mypy
        mypy . --ignore-missing-imports || true
    
    - name: Format check with black
      run: |
        pip install black
        black --check . || true
    
    - name: Run tests with pytest
      run: |
        pytest tests/ -v --cov=. --cov-report=xml --cov-report=html
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        REDIS_URL: redis://localhost:6379
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
        fail_ci_if_error: false
    
    - name: Archive test results
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: test-results-${{ matrix.python-version }}
        path: |
          htmlcov/
          coverage.xml
```

---

## Step 2: Security Scanning Workflow

Create `.github/workflows/security.yml`:

```yaml
name: Security Scanning

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  schedule:
    - cron: '0 0 * * 0'  # Weekly scan

jobs:
  security:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install bandit safety pip-audit
    
    - name: Run Bandit
      run: |
        bandit -r . -f json -o bandit-report.json || true
        bandit -r . -f txt
    
    - name: Run Safety
      run: |
        safety check --json > safety-report.json || true
        safety check
    
    - name: Run pip-audit
      run: |
        pip-audit --desc > pip-audit-report.json || true
        pip-audit
    
    - name: Upload security reports
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: security-reports
        path: |
          bandit-report.json
          safety-report.json
          pip-audit-report.json
    
    - name: Comment PR with security results
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v6
      with:
        script: |
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: '✅ Security scan completed. Check artifacts for detailed reports.'
          })
```

---

## Step 3: Build & Push Docker Images

Create `.github/workflows/build.yml`:

```yaml
name: Build & Push Docker Images

on:
  push:
    branches: [ main, develop ]
    tags: [ 'v*' ]
  pull_request:
    branches: [ main, develop ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    strategy:
      matrix:
        include:
          - dockerfile: Dockerfile
            image: api
          - dockerfile: Dockerfile.dashboard
            image: dashboard
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Log in to Container Registry
      if: github.event_name != 'pull_request'
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-${{ matrix.image }}
        tags: |
          type=ref,event=branch
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}
          type=sha
    
    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: .
        file: ${{ matrix.dockerfile }}
        push: ${{ github.event_name != 'pull_request' }}
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
```

---

## Step 4: Deployment Workflow

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/v')
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to production
      run: |
        echo "Deploying version ${{ github.ref }}"
        # Add your deployment commands here
        # Example: kubectl apply -f k8s/
        # Example: docker pull and restart containers
    
    - name: Run smoke tests
      run: |
        echo "Running smoke tests..."
        # Add smoke test commands
    
    - name: Notify deployment
      if: success()
      uses: actions/github-script@v6
      with:
        script: |
          github.rest.repos.createDeployment({
            owner: context.repo.owner,
            repo: context.repo.repo,
            ref: context.ref,
            environment: 'production',
            description: 'Deployment successful',
            auto_merge: false,
            required_contexts: []
          })
    
    - name: Rollback on failure
      if: failure()
      run: |
        echo "Deployment failed, initiating rollback..."
        # Add rollback commands
```

---

## Step 5: Code Coverage Badge

Add to `README.md`:

```markdown
[![Tests](https://github.com/YOUR_USERNAME/phishing-detection/actions/workflows/test.yml/badge.svg)](https://github.com/YOUR_USERNAME/phishing-detection/actions)
[![Security](https://github.com/YOUR_USERNAME/phishing-detection/actions/workflows/security.yml/badge.svg)](https://github.com/YOUR_USERNAME/phishing-detection/actions)
[![codecov](https://codecov.io/gh/YOUR_USERNAME/phishing-detection/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/phishing-detection)
```

---

## Step 6: Create Test Suite

Create `tests/test_api.py`:

```python
import pytest
from fastapi.testclient import TestClient
from real_api import app

client = TestClient(app)

def test_health_check():
    """Test API health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_predict_url():
    """Test URL prediction endpoint"""
    response = client.post(
        "/predict/url",
        json={"url": "https://www.google.com"}
    )
    assert response.status_code == 200
    assert "prediction" in response.json()

def test_predict_email():
    """Test email prediction endpoint"""
    response = client.post(
        "/predict/email",
        json={
            "sender": "test@example.com",
            "subject": "Test",
            "email_content": "Test content"
        }
    )
    assert response.status_code == 200
    assert "prediction" in response.json()

@pytest.mark.asyncio
async def test_concurrent_requests():
    """Test concurrent request handling"""
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

## Step 7: GitHub Secrets Configuration

Set these in GitHub Settings → Secrets:

```
DOCKER_USERNAME = your_docker_username
DOCKER_PASSWORD = your_docker_password
CODECOV_TOKEN = your_codecov_token
SENTRY_DSN = your_sentry_dsn
```

---

## Verification Checklist

- [ ] All workflow files created in `.github/workflows/`
- [ ] Test workflow runs successfully
- [ ] Security workflow runs successfully
- [ ] Build workflow creates Docker images
- [ ] Coverage reports generated
- [ ] Badges display in README
- [ ] GitHub Secrets configured
- [ ] Pull requests trigger workflows
- [ ] Deployment workflow ready

---

## Next Steps

1. Push all workflow files to GitHub
2. Verify workflows run on first push
3. Create a test PR to verify PR workflows
4. Monitor workflow execution
5. Move to Phase 3: Containerization

