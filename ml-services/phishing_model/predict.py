import joblib

# Load trained model and vectorizer
model = joblib.load("phishing_model.pkl")
vectorizer = joblib.load("tfidf_vectorizer.pkl")

print("📧 Phishing Email Detector Ready")

# Take email input
email = input("\nPaste email content:\n")

# Convert email to TF-IDF features
email_vec = vectorizer.transform([email])

# Predict
prediction = model.predict(email_vec)[0]
probability = model.predict_proba(email_vec)[0][1]

confidence = round(probability * 100, 2)

# Risk Level
if confidence > 80:
    risk = "HIGH"
elif confidence > 50:
    risk = "MEDIUM"
else:
    risk = "LOW"

# Output
print("\n🔎 Scan Result\n")

if prediction == 1:
    print("⚠️ PHISHING EMAIL DETECTED")
else:
    print("✅ SAFE EMAIL")

print("Risk Level:", risk)
print("Confidence:", confidence, "%")

# Recommended Action
print("\nRecommended Action:")

if prediction == 1:
    print("- Do NOT click any links")
    print("- Verify sender identity")
    print("- Report email to security team")
else:
    print("- Email appears safe")