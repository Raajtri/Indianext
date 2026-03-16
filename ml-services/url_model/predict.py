<<<<<<< HEAD
=======
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
>>>>>>> 53980e7c26e83a488ff25aef9d17e360703c8634
import joblib
import tldextract
from urllib.parse import urlparse
import re
<<<<<<< HEAD

from explainable_ai.url_explain import explain_url
from explainable_ai.suggestions import get_suggestions


model = joblib.load("url_model.pkl")
vectorizer = joblib.load("url_vectorizer.pkl")

print("🔗 AI URL Security Scanner Ready")

=======
from typing import List, Dict, Optional
import uvicorn
import os

# Load your trained model and vectorizer
MODEL_PATH = "url_model.pkl"
VECTORIZER_PATH = "url_vectorizer.pkl"

# Check if model files exist
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
if not os.path.exists(VECTORIZER_PATH):
    raise FileNotFoundError(f"Vectorizer not found at {VECTORIZER_PATH}")

# Load the model and vectorizer
model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)

print("✅ URL Security Scanner Ready")
print(f"Model type: {type(model).__name__}")
>>>>>>> 53980e7c26e83a488ff25aef9d17e360703c8634

# ----------------------------
# Brands commonly targeted
# ----------------------------
BRANDS = [
<<<<<<< HEAD
    "google","amazon","paypal","github",
    "facebook","microsoft","apple","bank",
    "netflix","openai"
]

=======
    "google", "amazon", "paypal", "github",
    "facebook", "microsoft", "apple", "bank",
    "netflix", "openai", "instagram", "twitter",
    "linkedin", "whatsapp", "telegram", "yahoo",
    "ebay", "walmart", "target", "bestbuy"
]

# Initialize FastAPI
app = FastAPI(
    title="URL Detection ML Service",
    description="Your trained model for malicious URL detection",
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
class URLRequest(BaseModel):
    url: str

class URLResponse(BaseModel):
    probability: float
    confidence: float
    prediction: int
    risk_level: str
    threat_type: str
    explanation: List[str]
    features: Dict
    brand_spoofed: Optional[bool] = False
    domain: Optional[str] = None
>>>>>>> 53980e7c26e83a488ff25aef9d17e360703c8634

# ----------------------------
# Normalize URL
# ----------------------------
<<<<<<< HEAD
def normalize_url(url):

    url = url.lower().strip()

    url = url.replace("https://","")
    url = url.replace("http://","")
    url = url.replace("www.","")

    return url


# ----------------------------
# Extract root domain
# ----------------------------
def extract_domain(url):

    extracted = tldextract.extract(url)

    domain = extracted.domain + "." + extracted.suffix

    return domain


# ----------------------------
# Detect brand spoofing
# Example:
# google.com.malicious.xyz
# ----------------------------
def brand_spoof(url, domain):

    for brand in BRANDS:

        if brand in url and brand not in domain:

            return True

    return False

=======
def normalize_url(url: str) -> str:
    url = url.lower().strip()
    url = url.replace("https://", "")
    url = url.replace("http://", "")
    url = url.replace("www.", "")
    return url

# ----------------------------
# Extract root domain
# ----------------------------
def extract_domain(url: str) -> str:
    try:
        extracted = tldextract.extract(url)
        domain = extracted.domain + "." + extracted.suffix
        return domain
    except:
        return ""

# ----------------------------
# Detect brand spoofing
# ----------------------------
def detect_brand_spoof(url: str, domain: str) -> tuple:
    for brand in BRANDS:
        if brand in url and brand not in domain:
            return True, brand
    return False, None
>>>>>>> 53980e7c26e83a488ff25aef9d17e360703c8634

# ----------------------------
# Domain heuristic analysis
# ----------------------------
<<<<<<< HEAD
def domain_legitimacy(domain):

    suspicious_words = [
        "login","verify","secure","account",
        "update","bank","paypal","confirm"
    ]

    for word in suspicious_words:
        if word in domain:
            return False

    if domain.count("-") > 2:
        return False

    if len(domain) > 35:
        return False

    return True


# ----------------------------
# Main Scanner
# ----------------------------
def scan_url(url):

    original_url = url

    url = normalize_url(url)

    domain = extract_domain(url)


    # ----------------------------
    # Explainable AI analysis
    # ----------------------------
    score, reasons = explain_url(original_url)


    # ----------------------------
    # Brand spoof detection
    # ----------------------------
    if brand_spoof(url, domain):

        prediction = "phishing"

        suggestions = get_suggestions("url", prediction)

        return {
            "result": "⚠️ MALICIOUS URL",
            "confidence": 99.0,
            "threat_level": "HIGH",
            "reasons": ["Domain impersonates a trusted brand"],
            "suggestions": suggestions
        }


    # ----------------------------
    # ML prediction
    # ----------------------------
    url_vec = vectorizer.transform([url])

    prob = model.predict_proba(url_vec)[0][1]


    # ----------------------------
    # Domain heuristic adjustment
    # ----------------------------
    if domain_legitimacy(domain):

        prob = prob * 0.35


    confidence = round(prob * 100,2)


    # ----------------------------
    # Final decision
    # ----------------------------
    if prob >= 0.85:

        result = "⚠️ MALICIOUS URL"
        level = "HIGH"
        prediction = "phishing"

    elif prob >= 0.60:

        result = "⚠️ SUSPICIOUS URL"
        level = "MEDIUM"
        prediction = "phishing"

    else:

        result = "✅ SAFE URL"
        level = "LOW"
        prediction = "safe"


    # ----------------------------
    # Suggestions
    # ----------------------------
    suggestions = get_suggestions("url", prediction)


    return {
        "result": result,
        "confidence": confidence,
        "threat_level": level,
        "reasons": reasons,
        "suggestions": suggestions
    }


# ----------------------------
# CLI Interface
# ----------------------------
while True:

    url = input("\nEnter URL to scan (or type exit): ")

    if url.lower() == "exit":
        break

    response = scan_url(url)

    print("\nScan Result")
    print("------------------------")

    print(response["result"])
    print("Confidence:", response["confidence"], "%")
    print("Threat Level:", response["threat_level"])

    print("\nWhy this was flagged:")

    if len(response["reasons"]) == 0:
        print("- No suspicious indicators detected")

    else:
        for r in response["reasons"]:
            print("-", r)


    print("\nSuggestions:")

    for s in response["suggestions"]:
        print("-", s)
=======
def analyze_domain(domain: str) -> Dict:
    suspicious_words = [
        "login", "verify", "secure", "account",
        "update", "bank", "paypal", "confirm",
        "signin", "auth", "authenticate", "validation"
    ]
    
    features = {
        "has_suspicious_word": False,
        "hyphen_count": domain.count("-"),
        "length": len(domain),
        "digit_count": sum(c.isdigit() for c in domain)
    }
    
    for word in suspicious_words:
        if word in domain:
            features["has_suspicious_word"] = True
            features["suspicious_word"] = word
            break
    
    return features

# ----------------------------
# Extract URL features for explanation
# ----------------------------
def extract_url_features(url: str) -> Dict:
    features = {
        "length": len(url),
        "dot_count": url.count('.'),
        "hyphen_count": url.count('-'),
        "underscore_count": url.count('_'),
        "slash_count": url.count('/'),
        "digit_count": sum(c.isdigit() for c in url),
        "has_ip": bool(re.match(r'\d+\.\d+\.\d+\.\d+', url)),
        "has_https": url.startswith('https'),
        "subdomain_count": url.count('.') - 1 if url.count('.') > 1 else 0
    }
    return features

# ----------------------------
# Generate explanation
# ----------------------------
def generate_explanation(url: str, domain: str, probability: float, 
                         brand_spoofed: bool, spoofed_brand: str = None,
                         domain_features: Dict = None) -> List[str]:
    explanations = []
    
    if probability >= 0.85:
        explanations.append(f"⚠️ Malicious URL detected with {probability*100:.1f}% confidence")
    elif probability >= 0.60:
        explanations.append(f"⚠️ Suspicious URL detected with {probability*100:.1f}% confidence")
    else:
        explanations.append(f"✅ URL appears safe ({probability*100:.1f}% confidence)")
    
    # Brand spoofing detection
    if brand_spoofed and spoofed_brand:
        explanations.append(f"• Attempting to impersonate '{spoofed_brand}' brand")
    
    # Domain analysis
    if domain_features:
        if domain_features.get("has_suspicious_word"):
            explanations.append(f"• Contains suspicious word '{domain_features.get('suspicious_word')}' in domain")
        if domain_features.get("hyphen_count", 0) > 2:
            explanations.append(f"• Unusual number of hyphens ({domain_features['hyphen_count']}) in domain")
        if domain_features.get("length", 0) > 35:
            explanations.append("• Domain name is unusually long")
        if domain_features.get("digit_count", 0) > 3:
            explanations.append("• Contains many digits, often used in malicious URLs")
    
    # Check for IP address
    if re.match(r'\d+\.\d+\.\d+\.\d+', url):
        explanations.append("• Uses IP address instead of domain name (common in attacks)")
    
    # Check for URL shorteners
    shorteners = ['bit.ly', 'tinyurl', 'goo.gl', 'ow.ly', 'is.gd', 'buff.ly']
    if any(shortener in url for shortener in shorteners):
        explanations.append("• Uses URL shortener that can hide real destination")
    
    # Add model info
    explanations.append("• Analyzed using ML model trained on malicious URL datasets")
    
    return explanations

@app.get("/")
async def root():
    return {
        "service": "URL Detection ML Service",
        "status": "ready",
        "model": type(model).__name__,
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model_loaded": True
    }

@app.post("/predict", response_model=URLResponse)
async def predict(request: URLRequest):
    """
    Predict if a URL is malicious using your trained model
    """
    try:
        url = request.url
        
        if not url or len(url.strip()) < 4:
            raise HTTPException(status_code=400, detail="Invalid URL")
        
        # Normalize URL
        normalized_url = normalize_url(url)
        
        # Extract domain
        domain = extract_domain(normalized_url)
        
        # Check for brand spoofing
        brand_spoofed, spoofed_brand = detect_brand_spoof(normalized_url, domain)
        
        # Analyze domain
        domain_features = analyze_domain(domain)
        
        # ML prediction
        url_vec = vectorizer.transform([normalized_url])
        probability = float(model.predict_proba(url_vec)[0][1])
        
        # Domain heuristic adjustment (as in your original code)
        if not domain_features.get("has_suspicious_word") and domain_features.get("hyphen_count", 0) <= 2:
            probability = probability * 0.35
        
        # Ensure probability is within bounds
        probability = min(0.99, max(0.01, probability))
        
        # Calculate confidence
        confidence = round(probability * 100, 2)
        
        # Determine risk level and prediction
        if probability >= 0.85:
            risk_level = "HIGH"
            prediction = 1
            threat_type = "malicious_url"
        elif probability >= 0.60:
            risk_level = "MEDIUM"
            prediction = 1
            threat_type = "malicious_url"
        else:
            risk_level = "LOW"
            prediction = 0
            threat_type = "safe"
        
        # Generate explanation
        explanation = generate_explanation(
            url, domain, probability, 
            brand_spoofed, spoofed_brand,
            domain_features
        )
        
        # Extract basic features
        features = extract_url_features(url)
        features.update({
            "domain": domain,
            "brand_spoofed": brand_spoofed,
            "spoofed_brand": spoofed_brand,
            **domain_features
        })
        
        return URLResponse(
            probability=probability,
            confidence=confidence,
            prediction=prediction,
            risk_level=risk_level,
            threat_type=threat_type,
            explanation=explanation,
            features=features,
            brand_spoofed=brand_spoofed,
            domain=domain
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/batch-predict")
async def batch_predict(requests: List[URLRequest]):
    """
    Batch prediction for multiple URLs
    """
    try:
        results = []
        for req in requests:
            url = req.url
            normalized_url = normalize_url(url)
            url_vec = vectorizer.transform([normalized_url])
            prob = float(model.predict_proba(url_vec)[0][1])
            
            results.append({
                "url": url,
                "probability": prob,
                "confidence": round(prob * 100, 2),
                "risk_level": "HIGH" if prob >= 0.85 else "MEDIUM" if prob >= 0.60 else "LOW"
            })
        
        return {"results": results}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")

# For running directly
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5002, reload=True)
>>>>>>> 53980e7c26e83a488ff25aef9d17e360703c8634
