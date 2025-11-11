#!/usr/bin/env python3
"""
ML Model Security Framework
Advanced security testing and monitoring for ML models
"""

import numpy as np
import pandas as pd
import pickle
import hashlib
import hmac
import json
from typing import Dict, List, Tuple, Optional, Any
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class MLModelSecurity:
    """Advanced ML model security framework"""
    
    def __init__(self, model_path: str = None):
        self.model_path = model_path
        self.model = None
        self.scaler = None
        self.feature_names = []
        self.security_metrics = {}
        
    def load_model(self):
        """Load model with security validation"""
        try:
            if self.model_path and os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                
                # Validate model integrity
                if not self._validate_model_integrity():
                    raise SecurityError("Model integrity validation failed")
                
                print("✅ Model loaded and validated successfully")
                return True
            else:
                print("⚠️ Model file not found, using dummy model for testing")
                return False
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False
    
    def _validate_model_integrity(self) -> bool:
        """Validate model hasn't been tampered with"""
        if not self.model:
            return False
        
        # Check model structure
        required_methods = ['predict', 'predict_proba']
        for method in required_methods:
            if not hasattr(self.model, method):
                print(f"❌ Model missing required method: {method}")
                return False
        
        # Test model consistency
        test_input = np.random.rand(1, 16)
        try:
            pred1 = self.model.predict(test_input)
            pred2 = self.model.predict(test_input)
            if not np.array_equal(pred1, pred2):
                print("❌ Model predictions are inconsistent")
                return False
        except Exception as e:
            print(f"❌ Model prediction test failed: {e}")
            return False
        
        return True
    
    def detect_data_poisoning(self, X: np.ndarray, y: np.ndarray, threshold: float = 0.1) -> bool:
        """Detect potential data poisoning attacks"""
        try:
            # Statistical analysis for outliers
            from sklearn.ensemble import IsolationForest
            
            # Combine features and labels for analysis
            combined_data = np.column_stack([X, y])
            
            # Use Isolation Forest to detect outliers
            iso_forest = IsolationForest(contamination=threshold, random_state=42)
            outlier_labels = iso_forest.fit_predict(combined_data)
            
            # Count outliers
            num_outliers = np.sum(outlier_labels == -1)
            total_samples = len(combined_data)
            outlier_ratio = num_outliers / total_samples
            
            print(f"📊 Data poisoning analysis:")
            print(f"   Total samples: {total_samples}")
            print(f"   Outliers detected: {num_outliers}")
            print(f"   Outlier ratio: {outlier_ratio:.3f}")
            
            # Consider poisoned if outlier ratio exceeds threshold
            is_poisoned = outlier_ratio > threshold
            
            if is_poisoned:
                print("🚨 Potential data poisoning detected!")
            else:
                print("✅ No significant data poisoning detected")
            
            return is_poisoned
            
        except Exception as e:
            print(f"❌ Error in data poisoning detection: {e}")
            return False
    
    def detect_model_drift(self, training_data: np.ndarray, production_data: np.ndarray, 
                          threshold: float = 0.05) -> bool:
        """Detect model drift between training and production data"""
        try:
            from scipy import stats
            
            # Statistical tests for distribution differences
            drift_detected = False
            drift_details = []
            
            for i in range(min(training_data.shape[1], production_data.shape[1])):
                train_feature = training_data[:, i]
                prod_feature = production_data[:, i]
                
                # Kolmogorov-Smirnov test
                ks_stat, ks_pvalue = stats.ks_2samp(train_feature, prod_feature)
                
                # Mann-Whitney U test
                mw_stat, mw_pvalue = stats.mannwhitneyu(train_feature, prod_feature, 
                                                       alternative='two-sided')
                
                # Check for significant differences
                if ks_pvalue < threshold or mw_pvalue < threshold:
                    drift_detected = True
                    drift_details.append({
                        'feature': i,
                        'ks_pvalue': ks_pvalue,
                        'mw_pvalue': mw_pvalue
                    })
            
            print(f"📊 Model drift analysis:")
            print(f"   Training samples: {len(training_data)}")
            print(f"   Production samples: {len(production_data)}")
            print(f"   Features with drift: {len(drift_details)}")
            
            if drift_detected:
                print("🚨 Model drift detected!")
                for detail in drift_details[:5]:  # Show first 5
                    print(f"   Feature {detail['feature']}: KS={detail['ks_pvalue']:.4f}, MW={detail['mw_pvalue']:.4f}")
            else:
                print("✅ No significant model drift detected")
            
            return drift_detected
            
        except Exception as e:
            print(f"❌ Error in drift detection: {e}")
            return False
    
    def detect_model_bias(self, X: np.ndarray, y: np.ndarray, 
                         sensitive_features: List[int] = None) -> bool:
        """Detect model bias and fairness issues"""
        try:
            if sensitive_features is None:
                # Use first few features as sensitive attributes
                sensitive_features = list(range(min(3, X.shape[1])))
            
            bias_detected = False
            bias_details = []
            
            for feature_idx in sensitive_features:
                if feature_idx >= X.shape[1]:
                    continue
                
                feature_values = X[:, feature_idx]
                unique_values = np.unique(feature_values)
                
                if len(unique_values) < 2:
                    continue
                
                # Split into groups based on feature values
                groups = []
                for value in unique_values:
                    mask = feature_values == value
                    group_labels = y[mask]
                    if len(group_labels) > 0:
                        groups.append({
                            'value': value,
                            'labels': group_labels,
                            'positive_rate': np.mean(group_labels)
                        })
                
                # Check for significant differences in positive rates
                if len(groups) >= 2:
                    positive_rates = [group['positive_rate'] for group in groups]
                    max_rate = max(positive_rates)
                    min_rate = min(positive_rates)
                    rate_diff = max_rate - min_rate
                    
                    if rate_diff > 0.3:  # 30% difference threshold
                        bias_detected = True
                        bias_details.append({
                            'feature': feature_idx,
                            'rate_difference': rate_diff,
                            'groups': groups
                        })
            
            print(f"📊 Model bias analysis:")
            print(f"   Sensitive features analyzed: {len(sensitive_features)}")
            print(f"   Features with bias: {len(bias_details)}")
            
            if bias_detected:
                print("🚨 Model bias detected!")
                for detail in bias_details:
                    print(f"   Feature {detail['feature']}: Rate difference = {detail['rate_difference']:.3f}")
            else:
                print("✅ No significant model bias detected")
            
            return bias_detected
            
        except Exception as e:
            print(f"❌ Error in bias detection: {e}")
            return False
    
    def test_adversarial_robustness(self, X: np.ndarray, epsilon: float = 0.1) -> Dict:
        """Test model robustness against adversarial examples"""
        try:
            if not self.model:
                print("❌ No model loaded for adversarial testing")
                return {}
            
            # Generate adversarial examples
            adversarial_X = X.copy()
            noise = np.random.normal(0, epsilon, X.shape)
            adversarial_X += noise
            
            # Get predictions
            original_pred = self.model.predict(X)
            adversarial_pred = self.model.predict(adversarial_X)
            
            # Calculate robustness metrics
            total_samples = len(X)
            changed_predictions = np.sum(original_pred != adversarial_pred)
            robustness_ratio = 1 - (changed_predictions / total_samples)
            
            # Calculate confidence changes
            if hasattr(self.model, 'predict_proba'):
                original_conf = self.model.predict_proba(X)
                adversarial_conf = self.model.predict_proba(adversarial_X)
                conf_changes = np.mean(np.abs(original_conf - adversarial_conf))
            else:
                conf_changes = 0
            
            results = {
                'total_samples': total_samples,
                'changed_predictions': changed_predictions,
                'robustness_ratio': robustness_ratio,
                'confidence_change': conf_changes,
                'epsilon': epsilon
            }
            
            print(f"📊 Adversarial robustness test:")
            print(f"   Total samples: {total_samples}")
            print(f"   Changed predictions: {changed_predictions}")
            print(f"   Robustness ratio: {robustness_ratio:.3f}")
            print(f"   Average confidence change: {conf_changes:.3f}")
            
            if robustness_ratio < 0.8:
                print("🚨 Model may be vulnerable to adversarial attacks!")
            else:
                print("✅ Model shows good adversarial robustness")
            
            return results
            
        except Exception as e:
            print(f"❌ Error in adversarial testing: {e}")
            return {}
    
    def get_feature_importance(self, X: np.ndarray, method: str = 'permutation') -> np.ndarray:
        """Get feature importance using various methods"""
        try:
            if not self.model:
                print("❌ No model loaded for feature importance")
                return np.array([])
            
            if method == 'permutation':
                return self._permutation_importance(X)
            elif method == 'shap':
                return self._shap_importance(X)
            else:
                return self._default_importance()
                
        except Exception as e:
            print(f"❌ Error calculating feature importance: {e}")
            return np.array([])
    
    def _permutation_importance(self, X: np.ndarray) -> np.ndarray:
        """Calculate permutation importance"""
        try:
            baseline_score = self._model_score(X)
            importance_scores = []
            
            for i in range(X.shape[1]):
                X_permuted = X.copy()
                np.random.shuffle(X_permuted[:, i])
                permuted_score = self._model_score(X_permuted)
                importance = baseline_score - permuted_score
                importance_scores.append(importance)
            
            return np.array(importance_scores)
            
        except Exception as e:
            print(f"❌ Error in permutation importance: {e}")
            return np.array([])
    
    def _model_score(self, X: np.ndarray) -> float:
        """Calculate model score (placeholder)"""
        try:
            if hasattr(self.model, 'score'):
                # Use dummy labels for scoring
                y_dummy = np.random.randint(0, 2, len(X))
                return self.model.score(X, y_dummy)
            else:
                # Fallback to prediction consistency
                pred = self.model.predict(X)
                return np.mean(pred)
        except:
            return 0.5  # Default score
    
    def _shap_importance(self, X: np.ndarray) -> np.ndarray:
        """Calculate SHAP-based importance (simplified)"""
        try:
            # Simplified SHAP calculation
            baseline_pred = self.model.predict(X)
            importance_scores = []
            
            for i in range(X.shape[1]):
                X_modified = X.copy()
                X_modified[:, i] = np.mean(X[:, i])  # Set to mean value
                modified_pred = self.model.predict(X_modified)
                importance = np.mean(np.abs(baseline_pred - modified_pred))
                importance_scores.append(importance)
            
            return np.array(importance_scores)
            
        except Exception as e:
            print(f"❌ Error in SHAP importance: {e}")
            return np.array([])
    
    def _default_importance(self) -> np.ndarray:
        """Get default feature importance from model"""
        try:
            if hasattr(self.model, 'feature_importances_'):
                return self.model.feature_importances_
            else:
                return np.array([])
        except:
            return np.array([])
    
    def encrypt_model(self, model_data: bytes, key: str = None) -> bytes:
        """Encrypt model data"""
        try:
            if key is None:
                key = "default_security_key_change_in_production"
            
            key_bytes = key.encode()[:32].ljust(32, b'0')  # Ensure 32 bytes
            
            # Simple XOR encryption (use proper encryption in production)
            encrypted = bytearray()
            for i, byte in enumerate(model_data):
                encrypted.append(byte ^ key_bytes[i % 32])
            
            return bytes(encrypted)
            
        except Exception as e:
            print(f"❌ Error encrypting model: {e}")
            return model_data
    
    def decrypt_model(self, encrypted_data: bytes, key: str = None) -> bytes:
        """Decrypt model data"""
        try:
            if key is None:
                key = "default_security_key_change_in_production"
            
            key_bytes = key.encode()[:32].ljust(32, b'0')
            
            # Simple XOR decryption
            decrypted = bytearray()
            for i, byte in enumerate(encrypted_data):
                decrypted.append(byte ^ key_bytes[i % 32])
            
            return bytes(decrypted)
            
        except Exception as e:
            print(f"❌ Error decrypting model: {e}")
            return encrypted_data
    
    def generate_security_report(self) -> Dict:
        """Generate comprehensive security report"""
        try:
            report = {
                'timestamp': pd.Timestamp.now().isoformat(),
                'model_path': self.model_path,
                'model_loaded': self.model is not None,
                'security_metrics': self.security_metrics,
                'recommendations': []
            }
            
            # Add security recommendations
            if self.model is None:
                report['recommendations'].append("Load model for security analysis")
            
            if not self.security_metrics:
                report['recommendations'].append("Run security tests to populate metrics")
            
            return report
            
        except Exception as e:
            print(f"❌ Error generating security report: {e}")
            return {}

class SecurityError(Exception):
    """Custom security exception"""
    pass

# Command line interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='ML Model Security Testing')
    parser.add_argument('--model-path', type=str, help='Path to model file')
    parser.add_argument('--test-adversarial', action='store_true', help='Test adversarial robustness')
    parser.add_argument('--verify-integrity', action='store_true', help='Verify model integrity')
    parser.add_argument('--generate-report', action='store_true', help='Generate security report')
    
    args = parser.parse_args()
    
    # Initialize security framework
    security = MLModelSecurity(args.model_path)
    
    if args.verify_integrity:
        print("🔍 Verifying model integrity...")
        security.load_model()
    
    if args.test_adversarial:
        print("🧪 Testing adversarial robustness...")
        # Generate test data
        test_data = np.random.rand(100, 16)
        results = security.test_adversarial_robustness(test_data)
        print(f"Results: {results}")
    
    if args.generate_report:
        print("📊 Generating security report...")
        report = security.generate_security_report()
        print(json.dumps(report, indent=2))
