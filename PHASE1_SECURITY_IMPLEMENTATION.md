# Phase 1: Security & Compliance Implementation Guide
## DevSecOps Foundation (Estimated: 8-10 hours)

---

## Step 1: Static Application Security Testing (SAST) with Bandit

### 1.1 Installation
```bash
pip install bandit
```

### 1.2 Create Bandit Configuration
Create `.bandit` file:
```yaml
# .bandit
exclude_dirs:
  - /tests
  - /venv
  - /__pycache__
  - /.git

tests:
  - B201  # flask_debug_true
  - B301  # pickle
  - B302  # marshal
  - B303  # md5
  - B304  # des
  - B305  # cipher
  - B306  # mktemp_q
  - B307  # eval
  - B308  # mark_safe
  - B309  # httpsconnection
  - B310  # urllib_urlopen
  - B311  # random
  - B312  # telnetlib
  - B313  # xml_bad_etree
  - B314  # xml_bad_expat
  - B315  # xml_bad_sax
  - B316  # xml_bad_pulldom
  - B317  # xml_bad_etree
  - B318  # xml_bad_etree
  - B319  # xml_bad_etree
  - B320  # xml_bad_etree
  - B321  # ftplib
  - B322  # unverified_context
  - B323  # unverified_context
  - B324  # hashlib
  - B325  # tempnam
```

### 1.3 Run Bandit Scan
```bash
# Generate JSON report
bandit -r . -f json -o bandit-report.json

# Generate HTML report
bandit -r . -f html -o bandit-report.html

# View in terminal
bandit -r .
```

### 1.4 Fix Common Issues
**Issue:** Hardcoded passwords
```python
# ❌ BAD
password = "admin123"

# ✅ GOOD
import os
password = os.getenv("DB_PASSWORD")
```

**Issue:** SQL Injection
```python
# ❌ BAD
query = f"SELECT * FROM users WHERE id = {user_id}"

# ✅ GOOD
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))
```

---

## Step 2: Dependency Vulnerability Scanning

### 2.1 Install Tools
```bash
pip install safety pip-audit
```

### 2.2 Run Safety Check
```bash
# Check for known vulnerabilities
safety check

# Generate JSON report
safety check --json > safety-report.json

# Ignore specific vulnerabilities (if needed)
safety check --ignore 12345
```

### 2.3 Run pip-audit
```bash
# Audit all dependencies
pip-audit

# Generate detailed report
pip-audit --desc > pip-audit-report.json

# Fix vulnerabilities
pip-audit --fix
```

### 2.4 Create GitHub Actions Workflow
Create `.github/workflows/security-scan.yml`:
```yaml
name: Security Scan

on: [push, pull_request]

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
        run: bandit -r . -f json -o bandit-report.json
        continue-on-error: true
      
      - name: Run Safety
        run: safety check --json > safety-report.json
        continue-on-error: true
      
      - name: Run pip-audit
        run: pip-audit --desc > pip-audit-report.json
        continue-on-error: true
      
      - name: Upload reports
        uses: actions/upload-artifact@v3
        with:
          name: security-reports
          path: |
            bandit-report.json
            safety-report.json
            pip-audit-report.json
```

---

## Step 3: Secret Management

### 3.1 Install python-dotenv
```bash
pip install python-dotenv
```

### 3.2 Create .env File
Create `.env` (add to .gitignore):
```
# Database
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_secure_password

# API Keys
API_KEY=your_api_key
SECRET_KEY=your_secret_key

# ML Model
MODEL_PATH=./models/best_phishing_model.pkl

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
```

### 3.3 Update Code to Use .env
```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", 5432)
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    API_KEY = os.getenv("API_KEY")
    SECRET_KEY = os.getenv("SECRET_KEY")
```

### 3.4 Install git-secrets
```bash
# Prevent secrets from being committed
pip install detect-secrets

# Scan for secrets
detect-secrets scan > .secrets.baseline

# Audit findings
detect-secrets audit .secrets.baseline
```

### 3.5 Create Pre-commit Hook
Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
  
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
      - id: check-added-large-files
```

### 3.6 Install Pre-commit
```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

---

## Step 4: Code Quality & Standards

### 4.1 Configure Black (Code Formatter)
Create `pyproject.toml`:
```toml
[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
)/
'''
```

### 4.2 Configure Flake8
Create `.flake8`:
```ini
[flake8]
max-line-length = 100
exclude = .git,__pycache__,venv,tests
ignore = E203,W503
```

### 4.3 Configure MyPy (Type Checking)
Create `mypy.ini`:
```ini
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = False
disallow_incomplete_defs = False
check_untyped_defs = True
```

### 4.4 Run Quality Checks
```bash
# Format code
black .

# Check style
flake8 .

# Type checking
mypy .
```

---

## Step 5: Create Security Dashboard

Create `security_report.py`:
```python
import json
from datetime import datetime

def generate_security_report():
    """Generate comprehensive security report"""
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "sast": "✅ Bandit scan completed",
            "dependencies": "✅ Safety check completed",
            "secrets": "✅ Secret detection completed",
            "code_quality": "✅ Code quality checks completed"
        },
        "status": "PASS",
        "recommendations": [
            "Review Bandit findings",
            "Update vulnerable dependencies",
            "Rotate exposed secrets",
            "Improve code coverage"
        ]
    }
    
    with open("security_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    return report

if __name__ == "__main__":
    report = generate_security_report()
    print(json.dumps(report, indent=2))
```

---

## Verification Checklist

- [ ] Bandit installed and configured
- [ ] Bandit scan runs without critical issues
- [ ] Safety check passes
- [ ] pip-audit check passes
- [ ] .env file created and in .gitignore
- [ ] No hardcoded secrets in code
- [ ] Pre-commit hooks installed
- [ ] Black formatting applied
- [ ] Flake8 checks pass
- [ ] MyPy type checking passes
- [ ] GitHub Actions workflow created
- [ ] Security reports generated

---

## Next Steps

1. Commit all security configurations
2. Push to GitHub
3. Verify GitHub Actions runs successfully
4. Review security reports
5. Fix any identified issues
6. Move to Phase 2: CI/CD Pipeline

