#!/usr/bin/env python3
"""
ML Model Security Testing
Tests for adversarial attacks, model poisoning, and data integrity
"""

import pytest
import numpy as np
import pandas as pd
import pickle
import os
from unittest.mock import patch, MagicMock
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# Import your existing modules
import sys
sys.path.append('.')
from real_feature_extractor import RealFeatureExtractor
from real_model_trainer import RealPhishingModelTrainer

class TestMLSecurity:
    """Test ML model security vulnerabilities"""
    
    @pytest.fixture
    def sample_model(self):
        """Load or create a sample model for testing"""
        if os.path.exists('models/best_phishing_model.pkl'):
            with open('models/best_phishing_model.pkl', 'rb') as f:
                return pickle.load(f)
        else:
            # Create a dummy model for testing
            return RandomForestClassifier(n_estimators=10, random_state=42)
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing"""
        return np.random.rand(100, 16)  # 16 features
    
    def test_model_integrity(self, sample_model):
        """Test that model hasn't been tampered with"""
        # Check model structure
        assert hasattr(sample_model, 'predict')
        assert hasattr(sample_model, 'predict_proba')
        
        # Test model consistency
        test_input = np.random.rand(1, 16)
        pred1 = sample_model.predict(test_input)
        pred2 = sample_model.predict(test_input)
        assert np.array_equal(pred1, pred2), "Model predictions should be consistent"
    
    def test_adversarial_robustness(self, sample_model, sample_data):
        """Test model robustness against adversarial examples"""
        # Generate adversarial examples
        adversarial_data = sample_data.copy()
        
        # Add small perturbations
        noise = np.random.normal(0, 0.1, sample_data.shape)
        adversarial_data += noise
        
        # Test that model doesn't change predictions drastically
        original_pred = sample_model.predict(sample_data[:10])
        adversarial_pred = sample_model.predict(adversarial_data[:10])
        
        # Allow some tolerance for small changes
        changes = np.sum(original_pred != adversarial_pred)
        assert changes <= 2, f"Model too sensitive to adversarial noise: {changes} changes"
    
    def test_data_poisoning_detection(self):
        """Test detection of poisoned training data"""
        # Simulate poisoned data
        clean_data = np.random.rand(100, 16)
        clean_labels = np.random.randint(0, 2, 100)
        
        # Add poisoned samples
        poisoned_data = np.vstack([clean_data, np.random.rand(10, 16) * 10])  # Outliers
        poisoned_labels = np.hstack([clean_labels, np.ones(10)])  # All labeled as phishing
        
        # Test poisoning detection
        from security.ml_security import detect_data_poisoning
        is_poisoned = detect_data_poisoning(poisoned_data, poisoned_labels)
        assert is_poisoned, "Should detect poisoned data"
    
    def test_model_drift_detection(self):
        """Test detection of model drift"""
        # Simulate training and production data
        training_data = np.random.normal(0, 1, (1000, 16))
        production_data = np.random.normal(2, 1, (100, 16))  # Different distribution
        
        from security.ml_security import detect_model_drift
        drift_detected = detect_model_drift(training_data, production_data)
        assert drift_detected, "Should detect distribution drift"
    
    def test_feature_importance_consistency(self, sample_model):
        """Test that feature importance is consistent"""
        if hasattr(sample_model, 'feature_importances_'):
            importance = sample_model.feature_importances_
            
            # Check that importance values are valid
            assert len(importance) > 0, "Feature importance should not be empty"
            assert all(imp >= 0 for imp in importance), "Importance should be non-negative"
            assert abs(sum(importance) - 1.0) < 0.01, "Importance should sum to 1"
    
    def test_model_bias_detection(self):
        """Test for model bias and fairness"""
        # Create biased dataset
        biased_data = np.random.rand(100, 16)
        biased_labels = np.zeros(100)
        
        # Introduce bias: certain features lead to specific predictions
        biased_data[:50, 0] = 1  # First 50 samples have feature 0 = 1
        biased_labels[:50] = 1   # All labeled as phishing
        
        # Test bias detection
        from security.ml_security import detect_model_bias
        bias_detected = detect_model_bias(biased_data, biased_labels)
        assert bias_detected, "Should detect model bias"
    
    def test_model_interpretability(self, sample_model, sample_data):
        """Test model interpretability and explainability"""
        # Test SHAP-like feature importance
        from security.ml_security import get_feature_importance
        
        importance = get_feature_importance(sample_model, sample_data[:5])
        assert len(importance) == 5, "Should return importance for each sample"
        assert all(len(imp) == 16 for imp in importance), "Should have importance for each feature"
    
    def test_model_encryption(self):
        """Test model encryption and secure storage"""
        from security.ml_security import encrypt_model, decrypt_model
        
        # Test model encryption
        model_data = b"test_model_data"
        encrypted = encrypt_model(model_data)
        decrypted = decrypt_model(encrypted)
        
        assert encrypted != model_data, "Encrypted data should be different"
        assert decrypted == model_data, "Decrypted data should match original"
    
    def test_secure_model_loading(self):
        """Test secure model loading with integrity checks"""
        from security.ml_security import secure_model_loader
        
        # Test secure loading
        try:
            model = secure_model_loader('models/best_phishing_model.pkl')
            assert model is not None, "Should load model successfully"
        except FileNotFoundError:
            pytest.skip("Model file not found - skipping secure loading test")
    
    def test_model_versioning_security(self):
        """Test model versioning and rollback security"""
        from security.ml_security import ModelVersionManager
        
        version_manager = ModelVersionManager()
        
        # Test version creation
        version_id = version_manager.create_version("test_model", "v1.0")
        assert version_id is not None, "Should create version successfully"
        
        # Test version validation
        is_valid = version_manager.validate_version(version_id)
        assert is_valid, "Should validate version successfully"

class TestDataSecurity:
    """Test data security and privacy"""
    
    def test_data_encryption(self):
        """Test data encryption at rest"""
        from security.data_security import encrypt_data, decrypt_data
        
        test_data = "sensitive_phishing_data"
        encrypted = encrypt_data(test_data)
        decrypted = decrypt_data(encrypted)
        
        assert encrypted != test_data, "Encrypted data should be different"
        assert decrypted == test_data, "Decrypted data should match original"
    
    def test_pii_detection(self):
        """Test PII detection in data"""
        from security.data_security import detect_pii
        
        # Test data with potential PII
        test_data = [
            "user@example.com visited suspicious site",
            "Phone: 123-456-7890",
            "SSN: 123-45-6789",
            "Normal phishing detection text"
        ]
        
        pii_detected = detect_pii(test_data)
        assert pii_detected, "Should detect PII in data"
    
    def test_data_anonymization(self):
        """Test data anonymization"""
        from security.data_security import anonymize_data
        
        sensitive_data = "user@example.com clicked on phishing link"
        anonymized = anonymize_data(sensitive_data)
        
        assert "user@example.com" not in anonymized, "Should remove email addresses"
        assert "phishing link" in anonymized, "Should preserve non-PII content"

class TestAPISecurity:
    """Test API security"""
    
    def test_input_validation(self):
        """Test API input validation"""
        from security.api_security import validate_input
        
        # Test malicious inputs
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../etc/passwd",
            "javascript:alert('xss')"
        ]
        
        for malicious_input in malicious_inputs:
            is_valid = validate_input(malicious_input)
            assert not is_valid, f"Should reject malicious input: {malicious_input}"
    
    def test_rate_limiting(self):
        """Test API rate limiting"""
        from security.api_security import RateLimiter
        
        rate_limiter = RateLimiter(requests_per_minute=10)
        
        # Test rate limiting
        for i in range(15):
            allowed = rate_limiter.is_allowed("test_user")
            if i < 10:
                assert allowed, f"Should allow request {i+1}"
            else:
                assert not allowed, f"Should block request {i+1} due to rate limiting"
    
    def test_authentication_security(self):
        """Test authentication security"""
        from security.api_security import AuthenticationManager
        
        auth_manager = AuthenticationManager()
        
        # Test token generation
        token = auth_manager.generate_token("test_user")
        assert token is not None, "Should generate token"
        
        # Test token validation
        is_valid = auth_manager.validate_token(token)
        assert is_valid, "Should validate token"
        
        # Test expired token
        expired_token = auth_manager.generate_token("test_user", expires_in=0)
        is_valid = auth_manager.validate_token(expired_token)
        assert not is_valid, "Should reject expired token"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
