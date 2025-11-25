"""Test ML model accuracy with known phishing and legitimate URLs"""
import pickle
import numpy as np
from real_feature_extractor import RealFeatureExtractor

# Load model components
print("Loading model components...")
model = pickle.load(open('models/best_phishing_model.pkl', 'rb'))
scaler = pickle.load(open('models/feature_scaler.pkl', 'rb'))
feature_names = pickle.load(open('models/feature_names.pkl', 'rb'))
print(f"✅ Model loaded: {model.__class__.__name__}")
print(f"✅ Feature names: {len(feature_names)} features")

# Initialize feature extractor
extractor = RealFeatureExtractor()

# Test URLs - Known phishing sites
phishing_urls = [
    "http://paypal-secure-login.com/verify",
    "http://amazon-account-update.tk/signin",
    "http://secure-banking-login.ml/account",
    "http://192.168.1.1/login.php",
    "http://bit.ly/3xYz123",  # Shortened URL (suspicious)
]

# Test URLs - Known legitimate sites
legitimate_urls = [
    "https://www.google.com",
    "https://www.github.com",
    "https://www.microsoft.com",
    "https://www.wikipedia.org",
    "https://www.amazon.com",
]

def test_url(url, expected_label):
    """Test a single URL"""
    # Extract features
    features_dict = extractor.extract_url_features(url)
    features_vector = np.array([features_dict.get(name, 0) for name in feature_names])
    
    # Scale features
    features_scaled = scaler.transform(features_vector.reshape(1, -1))
    
    # Predict
    prediction = model.predict(features_scaled)[0]
    probability = model.predict_proba(features_scaled)[0]
    
    # Check if correct
    is_correct = (prediction == 1 and expected_label == "phishing") or (prediction == 0 and expected_label == "legitimate")
    
    result = "✅ CORRECT" if is_correct else "❌ WRONG"
    print(f"\n{result}")
    print(f"  URL: {url}")
    print(f"  Expected: {expected_label}")
    print(f"  Predicted: {'phishing' if prediction == 1 else 'legitimate'}")
    print(f"  Confidence: {max(probability):.2%}")
    print(f"  Probabilities: [Legit: {probability[0]:.2%}, Phishing: {probability[1]:.2%}]")
    
    return is_correct

print("\n" + "="*80)
print("TESTING PHISHING URLs (Should predict PHISHING)")
print("="*80)

phishing_correct = 0
for url in phishing_urls:
    if test_url(url, "phishing"):
        phishing_correct += 1

print("\n" + "="*80)
print("TESTING LEGITIMATE URLs (Should predict LEGITIMATE)")
print("="*80)

legitimate_correct = 0
for url in legitimate_urls:
    if test_url(url, "legitimate"):
        legitimate_correct += 1

print("\n" + "="*80)
print("FINAL RESULTS")
print("="*80)
print(f"Phishing URLs: {phishing_correct}/{len(phishing_urls)} correct ({phishing_correct/len(phishing_urls)*100:.1f}%)")
print(f"Legitimate URLs: {legitimate_correct}/{len(legitimate_urls)} correct ({legitimate_correct/len(legitimate_urls)*100:.1f}%)")
print(f"Overall Accuracy: {(phishing_correct + legitimate_correct)/(len(phishing_urls) + len(legitimate_urls))*100:.1f}%")

# Show feature importance
print("\n" + "="*80)
print("TOP 10 MOST IMPORTANT FEATURES")
print("="*80)
if hasattr(model, 'feature_importances_'):
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1][:10]
    for i, idx in enumerate(indices, 1):
        print(f"{i}. {feature_names[idx]}: {importances[idx]:.4f}")

