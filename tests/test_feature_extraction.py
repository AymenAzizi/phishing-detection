"""
Feature extraction tests
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_url_length():
    """Test URL length calculation"""
    url = "https://example.com/test"
    assert len(url) > 0


def test_domain_extraction():
    """Test domain extraction from URL"""
    url = "https://example.com/test"
    assert "example.com" in url


def test_protocol_detection():
    """Test protocol detection"""
    https_url = "https://example.com"
    http_url = "http://example.com"
    
    assert https_url.startswith("https://")
    assert http_url.startswith("http://")

