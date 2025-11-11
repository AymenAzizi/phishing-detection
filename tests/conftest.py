"""
Pytest configuration and fixtures
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def sample_url():
    """Sample URL for testing"""
    return "https://example.com"


@pytest.fixture
def sample_phishing_url():
    """Sample phishing URL for testing"""
    return "http://suspicious-paypal-login.tk/verify"


@pytest.fixture
def sample_safe_url():
    """Sample safe URL for testing"""
    return "https://www.google.com"

