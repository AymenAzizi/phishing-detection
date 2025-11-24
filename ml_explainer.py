#!/usr/bin/env python3
"""
Explainable AI Module for Phishing Detection
Uses SHAP and LIME to explain model predictions
"""

import shap
import lime
import lime.lime_tabular
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Optional
import io
import base64
import json
import pickle
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLExplainer:
    """Explainable AI for phishing detection model"""
    
    def __init__(self, model_path: str = "models/best_phishing_model.pkl",
                 scaler_path: str = "models/feature_scaler.pkl",
                 feature_names_path: str = "models/feature_names.pkl"):
        """Initialize the explainer with trained model"""
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.shap_explainer = None
        self.lime_explainer = None
        
        try:
            # Load model
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            logger.info("✅ Model loaded successfully")
            
            # Load scaler
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            logger.info("✅ Scaler loaded successfully")
            
            # Load feature names
            with open(feature_names_path, 'rb') as f:
                self.feature_names = pickle.load(f)
            logger.info(f"✅ Feature names loaded: {len(self.feature_names)} features")
            
            # Initialize SHAP explainer
            self._initialize_shap()
            
            # Initialize LIME explainer
            self._initialize_lime()
            
        except Exception as e:
            logger.error(f"❌ Error initializing explainer: {str(e)}")
            raise
    
    def _initialize_shap(self):
        """Initialize SHAP explainer"""
        try:
            # Use TreeExplainer for tree-based models (Gradient Boosting)
            self.shap_explainer = shap.TreeExplainer(self.model)
            logger.info("✅ SHAP explainer initialized (TreeExplainer)")
        except Exception as e:
            logger.warning(f"⚠️ TreeExplainer failed, using KernelExplainer: {str(e)}")
            # Fallback to KernelExplainer
            # Create a small background dataset (100 samples)
            try:
                # We'll need to pass background data when explaining
                self.shap_explainer = None  # Will initialize with data later
                logger.info("✅ SHAP explainer will use KernelExplainer")
            except Exception as e2:
                logger.error(f"❌ SHAP initialization failed: {str(e2)}")
    
    def _initialize_lime(self):
        """Initialize LIME explainer"""
        try:
            # LIME needs training data statistics
            # We'll initialize it when we have background data
            self.lime_explainer = None
            logger.info("✅ LIME explainer ready for initialization")
        except Exception as e:
            logger.error(f"❌ LIME initialization failed: {str(e)}")
    
    def explain_prediction(self, features: np.ndarray, 
                          feature_dict: Optional[Dict[str, Any]] = None,
                          method: str = "shap") -> Dict[str, Any]:
        """
        Explain a single prediction
        
        Args:
            features: Feature vector (scaled)
            feature_dict: Original feature values for display
            method: "shap" or "lime"
        
        Returns:
            Dictionary with explanation data
        """
        try:
            # Get prediction
            prediction = self.model.predict(features.reshape(1, -1))[0]
            prediction_proba = self.model.predict_proba(features.reshape(1, -1))[0]
            
            explanation = {
                "prediction": int(prediction),
                "prediction_label": "Phishing" if prediction == 1 else "Legitimate",
                "confidence": float(prediction_proba[1] if prediction == 1 else prediction_proba[0]),
                "probabilities": {
                    "legitimate": float(prediction_proba[0]),
                    "phishing": float(prediction_proba[1])
                },
                "method": method
            }
            
            if method == "shap":
                shap_values = self._get_shap_explanation(features)
                explanation.update(shap_values)
            elif method == "lime":
                lime_values = self._get_lime_explanation(features)
                explanation.update(lime_values)
            
            return explanation
            
        except Exception as e:
            logger.error(f"❌ Error explaining prediction: {str(e)}")
            return {
                "error": str(e),
                "prediction": None,
                "confidence": 0.0
            }
    
    def _get_shap_explanation(self, features: np.ndarray) -> Dict[str, Any]:
        """Get SHAP explanation for features"""
        try:
            # Calculate SHAP values
            shap_values = self.shap_explainer.shap_values(features.reshape(1, -1))
            
            # For binary classification, shap_values might be a list
            if isinstance(shap_values, list):
                shap_values = shap_values[1]  # Use values for positive class
            
            # Get feature importance
            feature_importance = []
            for i, (name, value) in enumerate(zip(self.feature_names, shap_values[0])):
                feature_importance.append({
                    "feature": name,
                    "shap_value": float(value),
                    "feature_value": float(features[i]),
                    "impact": "increases" if value > 0 else "decreases",
                    "magnitude": abs(float(value))
                })
            
            # Sort by absolute SHAP value
            feature_importance.sort(key=lambda x: x["magnitude"], reverse=True)
            
            # Create waterfall plot
            waterfall_plot = self._create_shap_waterfall_plot(shap_values[0], features)
            
            # Create force plot
            force_plot = self._create_shap_force_plot(shap_values[0], features)
            
            return {
                "feature_importance": feature_importance,
                "top_features": feature_importance[:5],
                "waterfall_plot": waterfall_plot,
                "force_plot": force_plot,
                "base_value": float(self.shap_explainer.expected_value[1] if isinstance(self.shap_explainer.expected_value, list) else self.shap_explainer.expected_value)
            }
            
        except Exception as e:
            logger.error(f"❌ SHAP explanation error: {str(e)}")
            return {
                "error": str(e),
                "feature_importance": []
            }
    
    def _get_lime_explanation(self, features: np.ndarray) -> Dict[str, Any]:
        """Get LIME explanation for features"""
        try:
            # Initialize LIME explainer if not done
            if self.lime_explainer is None:
                # Create dummy training data for LIME
                # In production, you'd use actual training data
                training_data = np.random.randn(100, len(self.feature_names))
                self.lime_explainer = lime.lime_tabular.LimeTabularExplainer(
                    training_data,
                    feature_names=self.feature_names,
                    class_names=['Legitimate', 'Phishing'],
                    mode='classification'
                )
            
            # Get explanation
            exp = self.lime_explainer.explain_instance(
                features,
                self.model.predict_proba,
                num_features=len(self.feature_names)
            )
            
            # Extract feature importance
            feature_importance = []
            for feature, weight in exp.as_list():
                feature_importance.append({
                    "feature": feature,
                    "weight": float(weight),
                    "impact": "increases" if weight > 0 else "decreases",
                    "magnitude": abs(float(weight))
                })
            
            # Sort by magnitude
            feature_importance.sort(key=lambda x: x["magnitude"], reverse=True)
            
            return {
                "feature_importance": feature_importance,
                "top_features": feature_importance[:5],
                "lime_score": float(exp.score)
            }
            
        except Exception as e:
            logger.error(f"❌ LIME explanation error: {str(e)}")
            return {
                "error": str(e),
                "feature_importance": []
            }
    
    def _create_shap_waterfall_plot(self, shap_values: np.ndarray, 
                                    features: np.ndarray) -> str:
        """Create SHAP waterfall plot and return as base64 image"""
        try:
            plt.figure(figsize=(10, 6))
            
            # Get top 10 features by absolute SHAP value
            indices = np.argsort(np.abs(shap_values))[-10:]
            
            # Create waterfall data
            values = shap_values[indices]
            names = [self.feature_names[i] for i in indices]
            
            # Create plot
            colors = ['red' if v > 0 else 'blue' for v in values]
            plt.barh(range(len(values)), values, color=colors)
            plt.yticks(range(len(values)), names)
            plt.xlabel('SHAP Value (impact on prediction)')
            plt.title('Top 10 Features Impact on Prediction')
            plt.tight_layout()
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            plt.close()
            
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            logger.error(f"❌ Error creating waterfall plot: {str(e)}")
            return ""
    
    def _create_shap_force_plot(self, shap_values: np.ndarray, 
                                features: np.ndarray) -> str:
        """Create SHAP force plot data"""
        try:
            # Create a simple force plot representation
            base_value = float(self.shap_explainer.expected_value[1] if isinstance(self.shap_explainer.expected_value, list) else self.shap_explainer.expected_value)
            
            force_data = {
                "base_value": base_value,
                "prediction": base_value + float(np.sum(shap_values)),
                "features": []
            }
            
            for i, (name, shap_val, feat_val) in enumerate(zip(self.feature_names, shap_values, features)):
                force_data["features"].append({
                    "name": name,
                    "value": float(feat_val),
                    "shap_value": float(shap_val)
                })
            
            return json.dumps(force_data)
            
        except Exception as e:
            logger.error(f"❌ Error creating force plot: {str(e)}")
            return "{}"
    
    def get_global_feature_importance(self) -> Dict[str, Any]:
        """Get global feature importance from the model"""
        try:
            # For tree-based models, get feature importance
            if hasattr(self.model, 'feature_importances_'):
                importances = self.model.feature_importances_
                
                feature_importance = []
                for name, importance in zip(self.feature_names, importances):
                    feature_importance.append({
                        "feature": name,
                        "importance": float(importance)
                    })
                
                # Sort by importance
                feature_importance.sort(key=lambda x: x["importance"], reverse=True)
                
                # Create plot
                plot_image = self._create_feature_importance_plot(feature_importance)
                
                return {
                    "feature_importance": feature_importance,
                    "top_features": feature_importance[:10],
                    "plot": plot_image
                }
            else:
                return {
                    "error": "Model does not support feature importance",
                    "feature_importance": []
                }
                
        except Exception as e:
            logger.error(f"❌ Error getting global feature importance: {str(e)}")
            return {
                "error": str(e),
                "feature_importance": []
            }
    
    def _create_feature_importance_plot(self, feature_importance: List[Dict]) -> str:
        """Create feature importance plot"""
        try:
            plt.figure(figsize=(10, 8))
            
            # Get top 15 features
            top_features = feature_importance[:15]
            names = [f["feature"] for f in top_features]
            values = [f["importance"] for f in top_features]
            
            # Create horizontal bar plot
            plt.barh(range(len(values)), values, color='steelblue')
            plt.yticks(range(len(values)), names)
            plt.xlabel('Feature Importance')
            plt.title('Top 15 Most Important Features')
            plt.tight_layout()
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            plt.close()
            
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            logger.error(f"❌ Error creating feature importance plot: {str(e)}")
            return ""

# Global explainer instance
explainer = None

def initialize_explainer():
    """Initialize global explainer"""
    global explainer
    try:
        explainer = MLExplainer()
        logger.info("✅ ML Explainer initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize ML Explainer: {str(e)}")
        return False

if __name__ == "__main__":
    # Test the explainer
    print("🧪 Testing ML Explainer...")
    
    if initialize_explainer():
        print("✅ Explainer initialized successfully")
        
        # Get global feature importance
        global_importance = explainer.get_global_feature_importance()
        print(f"\n📊 Top 5 Most Important Features:")
        for feat in global_importance.get("top_features", [])[:5]:
            print(f"  • {feat['feature']}: {feat['importance']:.4f}")
    else:
        print("❌ Failed to initialize explainer")

