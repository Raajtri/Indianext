from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import numpy as np
from typing import Optional, List, Dict
import os
import uvicorn

# Load your trained model and vectorizer
MODEL_PATH = "phishing_model.pkl"
VECTORIZER_PATH = "tfidf_vectorizer.pkl"

# Check if model files exist
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Please run train.py first.")
if not os.path.exists(VECTORIZER_PATH):
    raise FileNotFoundError(f"Vectorizer not found at {VECTORIZER_PATH}. Please run train.py first.")

# Load the model and vectorizer
model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)

print("✅ Phishing Email Detector Ready")
print(f"Model type: {type(model).__name__}")
print(f"Vectorizer features: {len(vectorizer.get_feature_names_out())}")

# Initialize FastAPI
app = FastAPI(
    title="Phishing Detection ML Service",
    description="Your trained XGBoost model for phishing email detection",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class PhishingRequest(BaseModel):
    email_text: str
    sender: Optional[str] = None
    subject: Optional[str] = None

class PhishingResponse(BaseModel):
    probability: float
    confidence: float
    prediction: int
    risk_level: str
    threat_type: str
    explanation: List[str]
    features: Dict

@app.get("/")
async def root():
    return {
        "service": "Phishing Detection ML Service",
        "status": "ready",
        "model": type(model).__name__,
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model_loaded": True,
        "vectorizer_features": len(vectorizer.get_feature_names_out())
    }

@app.post("/predict", response_model=PhishingResponse)
async def predict(request: PhishingRequest):
    """
    Predict if an email is phishing using your trained XGBoost model
    """
    try:
        # Get email text
        email_text = request.email_text
        
        if not email_text or len(email_text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Email text too short (minimum 10 characters)")
        
        # Convert email to TF-IDF features (same as your predict.py)
        email_vec = vectorizer.transform([email_text])
        
        # Make prediction (same as your predict.py)
        prediction = int(model.predict(email_vec)[0])
        probability = float(model.predict_proba(email_vec)[0][1])
        
        # Calculate confidence (same as your predict.py)
        confidence = round(probability * 100, 2)
        
        # Determine risk level (same as your predict.py)
        if confidence > 80:
            risk_level = "HIGH"
        elif confidence > 50:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        # Set threat type
        threat_type = "phishing" if prediction == 1 else "safe"
        
        # Generate explanation based on email content
        explanation = generate_explanation(email_text, prediction, confidence)
        
        # Extract basic features for analysis
        features = extract_features(email_text)
        
        return PhishingResponse(
            probability=probability,
            confidence=confidence,
            prediction=prediction,
            risk_level=risk_level,
            threat_type=threat_type,
            explanation=explanation,
            features=features
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/batch-predict")
async def batch_predict(requests: List[PhishingRequest]):
    """
    Batch prediction for multiple emails
    """
    try:
        texts = [req.email_text for req in requests]
        
        # Vectorize all texts
        text_vecs = vectorizer.transform(texts)
        
        # Get predictions
        predictions = model.predict(text_vecs)
        probabilities = model.predict_proba(text_vecs)
        
        results = []
        for i, (pred, probs) in enumerate(zip(predictions, probabilities)):
            results.append({
                "prediction": int(pred),
                "probability": float(probs[1]),
                "confidence": round(float(probs[1]) * 100, 2),
                "risk_level": "HIGH" if probs[1] > 0.8 else "MEDIUM" if probs[1] > 0.5 else "LOW"
            })
        
        return {"results": results}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")

def generate_explanation(email_text: str, prediction: int, confidence: float) -> List[str]:
    """Generate human-readable explanation for the prediction"""
    text_lower = email_text.lower()
    explanations = []
    
    if prediction == 1:  # Phishing detected
        explanations.append(f"⚠️ Phishing detected with {confidence}% confidence")
        
        # Check for common phishing indicators
        if any(word in text_lower for word in ['urgent', 'immediately', 'asap', 'action required']):
            explanations.append("• Uses urgency language to pressure you")
        
        if any(word in text_lower for word in ['verify', 'account', 'password', 'credit card', 'ssn']):
            explanations.append("• Requests sensitive personal information")
        
        if 'http' in text_lower:
            # Count links
            link_count = text_lower.count('http')
            explanations.append(f"• Contains {link_count} suspicious link(s)")
        
        if any(word in text_lower for word in ['paypal', 'bank', 'amazon', 'apple', 'microsoft']):
            explanations.append("• Impersonates well-known companies")
        
        if 'click here' in text_lower:
            explanations.append("• Contains 'click here' phrases common in phishing")
            
    else:  # Safe email
        explanations.append(f"✅ Email appears safe ({confidence}% confidence)")
        explanations.append("• No phishing indicators detected")
    
    # Add model info
    explanations.append(f"• Analyzed using XGBoost model trained on multiple datasets")
    
    return explanations

def extract_features(email_text: str) -> Dict:
    """Extract basic features from email for analysis"""
    text_lower = email_text.lower()
    
    return {
        "length": len(email_text),
        "word_count": len(email_text.split()),
        "link_count": text_lower.count('http'),
        "urgent_words": sum(1 for w in ['urgent', 'immediately', 'asap'] if w in text_lower),
        "suspicious_words": sum(1 for w in ['verify', 'account', 'password', 'bank'] if w in text_lower),
        "exclamation_count": email_text.count('!'),
        "question_count": email_text.count('?'),
        "has_html": 1 if '<' in email_text and '>' in email_text else 0
    }

# For running directly
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5001, reload=True)