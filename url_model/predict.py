from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

import joblib
import tldextract
import os

from explainable_ai.url_explain import explain_url
from explainable_ai.suggestion import get_suggestions


# ----------------------------
# FastAPI App
# ----------------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------
# Paths
# ----------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "url_model.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "url_vectorizer.pkl")


print("Loading URL model...")

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)

print("🔗 URL ML Service Ready")


# ----------------------------
# Request Schema
# ----------------------------

class UrlRequest(BaseModel):
    url: str


# ----------------------------
# Brands targeted by phishing
# ----------------------------

BRANDS = [
    "google","amazon","paypal","github",
    "facebook","microsoft","apple","bank",
    "netflix","openai"
]


# ----------------------------
# Normalize URL
# ----------------------------

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

    return extracted.domain + "." + extracted.suffix


# ----------------------------
# Brand spoof detection
# ----------------------------

def brand_spoof(url, domain):

    for brand in BRANDS:
        if brand in url and brand not in domain:
            return True

    return False


# ----------------------------
# Domain heuristic
# ----------------------------

def domain_legitimacy(domain):

    suspicious_words = [
        "login","verify","secure",
        "account","update","bank",
        "paypal","confirm"
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

    score, reasons = explain_url(original_url)


    # Brand spoof detection
    if brand_spoof(url, domain):

        suggestions = get_suggestions("url", "phishing")

        return {
            "threat_type": "malicious_url",
            "probability": 0.99,
            "confidence": 99.0,
            "risk_level": "HIGH",
            "explanation": ["Domain impersonates a trusted brand"],
            "recommendations": suggestions
        }


    # ML prediction
    url_vec = vectorizer.transform([url])

    prob = float(model.predict_proba(url_vec)[0][1])


    if domain_legitimacy(domain):
        prob = prob * 0.35


    confidence = float(round(prob * 100,2))


    if prob >= 0.85:

        level = "HIGH"
        prediction = "malicious_url"

    elif prob >= 0.60:

        level = "MEDIUM"
        prediction = "malicious_url"

    else:

        level = "LOW"
        prediction = "safe"


    suggestions = get_suggestions("url", prediction)


    return {
        "threat_type": prediction,
        "probability": prob,
        "confidence": confidence,
        "risk_level": level,
        "explanation": reasons,
        "recommendations": suggestions
    }


# ----------------------------
# API Endpoint
# ----------------------------

@app.post("/predict")
def predict_url(data: UrlRequest):

    result = scan_url(data.url)

    return result


# ----------------------------
# Health Check
# ----------------------------

@app.get("/")
def health():
    return {"status": "URL ML Service Running"}