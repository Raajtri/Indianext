from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import os

from explainable_ai.email_explain import explain_email
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

MODEL_PATH = os.path.join(BASE_DIR, "phishing_model.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "tfidf_vectorizer.pkl")


# ----------------------------
# Load Model
# ----------------------------

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model not found at {MODEL_PATH}")

if not os.path.exists(VECTORIZER_PATH):
    raise FileNotFoundError(f"Vectorizer not found at {VECTORIZER_PATH}")

print("Loading phishing model...")

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)

print("✅ Phishing ML service ready")


# ----------------------------
# Request Schema
# ----------------------------

class EmailRequest(BaseModel):
    email_text: str


# ----------------------------
# Email Scanner
# ----------------------------

def scan_email(email_text):

    # Convert email to TF-IDF features
    email_vec = vectorizer.transform([email_text])

    # ML prediction
    prediction = int(model.predict(email_vec)[0])
    probability = float(model.predict_proba(email_vec)[0][1])
    confidence = float(round(probability * 100, 2))

    # ----------------------------
    # Risk Level
    # ----------------------------

    if confidence > 80:
        risk = "HIGH"
        result = "phishing"
        prediction_label = "phishing"

    elif confidence > 50:
        risk = "MEDIUM"
        result = "phishing"
        prediction_label = "phishing"

    else:
        risk = "LOW"
        result = "safe"
        prediction_label = "safe"

    # Explainable AI
    reasons = explain_email(email_text)

    # Suggestions
    suggestions = get_suggestions("email", prediction_label)

    return {
        "threat_type": result,
        "confidence": confidence,
        "risk_level": risk,
        "explanation": reasons,
        "recommendations": suggestions
    }


# ----------------------------
# API Endpoint
# ----------------------------

@app.post("/predict")
def predict_email(data: EmailRequest):

    result = scan_email(data.email_text)

    return {
        "probability": result["confidence"] / 100,
        "confidence": result["confidence"],
        "risk_level": result["risk_level"],
        "explanation": result["explanation"],
        "recommendations": result["recommendations"]
    }


# ----------------------------
# Health Check
# ----------------------------

@app.get("/")
def health():
    return {"status": "Phishing ML Service Running"}