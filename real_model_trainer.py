#!/usr/bin/env python3
"""
Real ML Model Trainer for Phishing Detection
Uses actual data from DataFiles to train production models
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import pickle
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class RealPhishingModelTrainer:
    def __init__(self):
        self.models = {}
        self.scaler = StandardScaler()
        self.feature_names = []
        self.best_model = None
        self.best_score = 0
        
    def load_and_prepare_data(self):
        """Load and prepare the real dataset"""
        print("📊 Loading real phishing detection dataset...")
        
        # Load all datasets
        datasets = []
        
        # Load phishing data (label = 1)
        phishing_df = pd.read_csv('DataFiles/4.phishing.csv')
        print(f"   Loaded {len(phishing_df)} phishing samples")
        
        # Load legitimate data (label = 0)  
        legitimate_df = pd.read_csv('DataFiles/3.legitimate.csv')
        print(f"   Loaded {len(legitimate_df)} legitimate samples")
        
        # Standardize column names before combining
        phishing_df.columns = phishing_df.columns.str.replace('Tiny_URL', 'TinyURL')
        phishing_df.columns = phishing_df.columns.str.replace('Prefix/Suffix', 'Prefix_Suffix')
        legitimate_df.columns = legitimate_df.columns.str.replace('Tiny_URL', 'TinyURL')
        legitimate_df.columns = legitimate_df.columns.str.replace('Prefix/Suffix', 'Prefix_Suffix')

        # Combine datasets
        combined_df = pd.concat([phishing_df, legitimate_df], ignore_index=True)

        # Remove duplicate columns if any
        combined_df = combined_df.loc[:, ~combined_df.columns.duplicated()]

        print(f"   Total dataset size: {len(combined_df)} samples")
        print(f"   Features: {list(combined_df.columns)}")
        print(f"   Class distribution: {combined_df['Label'].value_counts().to_dict()}")

        # Prepare features and target
        feature_columns = [col for col in combined_df.columns if col not in ['Domain', 'Label']]

        X = combined_df[feature_columns].copy()
        y = combined_df['Label'].copy()

        # Ensure all features are numeric
        for col in X.columns:
            X[col] = pd.to_numeric(X[col], errors='coerce').fillna(0)

        # Verify data balance
        print(f"   Feature matrix shape: {X.shape}")
        print(f"   Target distribution: Legitimate: {(y==0).sum()}, Phishing: {(y==1).sum()}")

        # Show sample data for verification
        print(f"\n   Sample legitimate features:")
        legitimate_sample = X[y==0].iloc[0]
        for i, (name, value) in enumerate(zip(feature_columns, legitimate_sample)):
            print(f"     {name}: {value}")

        print(f"\n   Sample phishing features:")
        phishing_sample = X[y==1].iloc[0]
        for i, (name, value) in enumerate(zip(feature_columns, phishing_sample)):
            print(f"     {name}: {value}")

        self.feature_names = feature_columns

        return X, y
    
    def train_models(self, X, y):
        """Train multiple ML models"""
        print("\n🤖 Training machine learning models...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Define models to train (simplified to avoid XGBoost issues)
        model_configs = {
            'Random Forest': {
                'model': RandomForestClassifier(random_state=42),
                'params': {
                    'n_estimators': [100, 200],
                    'max_depth': [10, 20],
                    'min_samples_split': [2, 5]
                }
            },
            'Gradient Boosting': {
                'model': GradientBoostingClassifier(random_state=42),
                'params': {
                    'n_estimators': [100, 200],
                    'max_depth': [5, 10],
                    'learning_rate': [0.1, 0.2]
                }
            },
            'Logistic Regression': {
                'model': LogisticRegression(random_state=42, max_iter=1000),
                'params': {
                    'C': [0.1, 1, 10],
                    'penalty': ['l2']
                }
            }
        }
        
        results = {}
        
        for name, config in model_configs.items():
            print(f"\n   Training {name}...")
            
            # Grid search for best parameters
            grid_search = GridSearchCV(
                config['model'], 
                config['params'], 
                cv=5, 
                scoring='f1',
                n_jobs=-1
            )
            
            # Use scaled data for models that need it
            if name in ['Logistic Regression', 'SVM']:
                grid_search.fit(X_train_scaled, y_train)
                y_pred = grid_search.predict(X_test_scaled)
            else:
                grid_search.fit(X_train, y_train)
                y_pred = grid_search.predict(X_test)
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            
            results[name] = {
                'model': grid_search.best_estimator_,
                'accuracy': accuracy,
                'f1_score': f1,
                'best_params': grid_search.best_params_
            }
            
            print(f"      Accuracy: {accuracy:.4f}")
            print(f"      F1-Score: {f1:.4f}")
            print(f"      Best params: {grid_search.best_params_}")
            
            # Track best model
            if f1 > self.best_score:
                self.best_score = f1
                self.best_model = grid_search.best_estimator_
                self.best_model_name = name
        
        self.models = results
        return results, X_test, y_test
    
    def evaluate_best_model(self, X_test, y_test):
        """Evaluate the best model in detail"""
        print(f"\n🏆 Best Model: {self.best_model_name} (F1-Score: {self.best_score:.4f})")
        
        # Use scaled data if needed
        if self.best_model_name in ['Logistic Regression', 'SVM']:
            y_pred = self.best_model.predict(self.scaler.transform(X_test))
        else:
            y_pred = self.best_model.predict(X_test)
        
        print("\n📊 Detailed Classification Report:")
        print(classification_report(y_test, y_pred, target_names=['Legitimate', 'Phishing']))
        
        print("\n🔍 Confusion Matrix:")
        cm = confusion_matrix(y_test, y_pred)
        print(f"True Negatives: {cm[0,0]}, False Positives: {cm[0,1]}")
        print(f"False Negatives: {cm[1,0]}, True Positives: {cm[1,1]}")
        
        # Feature importance (if available)
        if hasattr(self.best_model, 'feature_importances_'):
            print("\n🔍 Top 10 Most Important Features:")
            feature_importance = pd.DataFrame({
                'feature': self.feature_names,
                'importance': self.best_model.feature_importances_
            }).sort_values('importance', ascending=False)

            for i, row in feature_importance.head(10).iterrows():
                print(f"   {row['feature']}: {row['importance']:.4f}")

        # Test model with sample data
        print("\n🧪 Testing model with sample data:")

        # Test with a legitimate sample
        legitimate_sample = X_test[y_test==0].iloc[0:1]
        if self.best_model_name in ['Logistic Regression', 'SVM']:
            legitimate_pred = self.best_model.predict(self.scaler.transform(legitimate_sample))
            legitimate_proba = self.best_model.predict_proba(self.scaler.transform(legitimate_sample))
        else:
            legitimate_pred = self.best_model.predict(legitimate_sample)
            legitimate_proba = self.best_model.predict_proba(legitimate_sample)

        print(f"   Legitimate sample prediction: {legitimate_pred[0]} (should be 0)")
        print(f"   Legitimate sample probabilities: {legitimate_proba[0]}")

        # Test with a phishing sample
        phishing_sample = X_test[y_test==1].iloc[0:1]
        if self.best_model_name in ['Logistic Regression', 'SVM']:
            phishing_pred = self.best_model.predict(self.scaler.transform(phishing_sample))
            phishing_proba = self.best_model.predict_proba(self.scaler.transform(phishing_sample))
        else:
            phishing_pred = self.best_model.predict(phishing_sample)
            phishing_proba = self.best_model.predict_proba(phishing_sample)

        print(f"   Phishing sample prediction: {phishing_pred[0]} (should be 1)")
        print(f"   Phishing sample probabilities: {phishing_proba[0]}")
    
    def save_models(self):
        """Save the trained models"""
        print("\n💾 Saving trained models...")
        
        # Create models directory
        os.makedirs('models', exist_ok=True)
        
        # Save best model
        model_path = f'models/best_phishing_model.pkl'
        with open(model_path, 'wb') as f:
            pickle.dump(self.best_model, f)
        print(f"   Saved best model: {model_path}")
        
        # Save scaler
        scaler_path = 'models/feature_scaler.pkl'
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        print(f"   Saved scaler: {scaler_path}")
        
        # Save feature names
        features_path = 'models/feature_names.pkl'
        with open(features_path, 'wb') as f:
            pickle.dump(self.feature_names, f)
        print(f"   Saved feature names: {features_path}")
        
        # Save model metadata
        metadata = {
            'model_name': self.best_model_name,
            'f1_score': self.best_score,
            'accuracy': self.models[self.best_model_name]['accuracy'],
            'feature_count': len(self.feature_names),
            'training_date': datetime.now().isoformat(),
            'feature_names': self.feature_names
        }
        
        metadata_path = 'models/model_metadata.pkl'
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)
        print(f"   Saved metadata: {metadata_path}")
        
        return model_path, scaler_path, features_path, metadata_path

def main():
    """Main training function"""
    print("🚀 Real Phishing Detection Model Training")
    print("=" * 50)
    
    trainer = RealPhishingModelTrainer()
    
    try:
        # Load and prepare data
        X, y = trainer.load_and_prepare_data()
        
        # Train models
        results, X_test, y_test = trainer.train_models(X, y)
        
        # Evaluate best model
        trainer.evaluate_best_model(X_test, y_test)
        
        # Save models
        paths = trainer.save_models()
        
        print("\n✅ Training completed successfully!")
        print(f"🎯 Best model achieved F1-Score: {trainer.best_score:.4f}")
        print(f"📁 Models saved in: models/")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
