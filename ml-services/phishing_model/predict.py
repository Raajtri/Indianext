import joblib
from explainable_ai.email_explain import explain_email
from explainable_ai.suggestions import get_suggestions

# ----------------------------
# Load trained model
# ----------------------------
model = joblib.load("phishing_model.pkl")
vectorizer = joblib.load("tfidf_vectorizer.pkl")

print("📧 Phishing Email Detector Ready")


# ----------------------------
# Email Scanner
# ----------------------------
def scan_email(email_text):

    # Convert email to TF-IDF features
    email_vec = vectorizer.transform([email_text])

    # ML prediction
    prediction = model.predict(email_vec)[0]
    probability = model.predict_proba(email_vec)[0][1]

    confidence = round(probability * 100, 2)


    # ----------------------------
    # Risk Level
    # ----------------------------
    if confidence > 80:
        risk = "HIGH"
        result = "⚠️ PHISHING EMAIL DETECTED"
        prediction_label = "phishing"

    elif confidence > 50:
        risk = "MEDIUM"
        result = "⚠️ SUSPICIOUS EMAIL"
        prediction_label = "phishing"

    else:
        risk = "LOW"
        result = "✅ SAFE EMAIL"
        prediction_label = "safe"


    # ----------------------------
    # Explainable AI
    # ----------------------------
    reasons = explain_email(email_text)

    # Suggestions
    suggestions = get_suggestions("email", prediction_label)


    # Return structured result
    return {
        "result": result,
        "confidence": confidence,
        "risk_level": risk,
        "reasons": reasons,
        "suggestions": suggestions
    }


# ----------------------------
# CLI Interface
# ----------------------------
while True:

    email = input("\nPaste email content (or type exit):\n")

    if email.lower() == "exit":
        break

    response = scan_email(email)

    print("\n🔎 Scan Result")
    print("-----------------------------")

    print(response["result"])
    print("Risk Level:", response["risk_level"])
    print("Confidence:", response["confidence"], "%")


    # ----------------------------
    # Explainable AI Output
    # ----------------------------
    print("\nWhy this was flagged:")

    if len(response["reasons"]) == 0:
        print("- No suspicious indicators detected")

    else:
        for r in response["reasons"]:
            print("-", r)


    # ----------------------------
    # Suggestions
    # ----------------------------
    print("\nRecommended Action:")

    for s in response["suggestions"]:
        print("-", s)