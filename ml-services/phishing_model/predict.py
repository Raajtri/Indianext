import joblib

# Load model
model = joblib.load("phishing_model.pkl")
vectorizer = joblib.load("tfidf_vectorizer.pkl")

print("Phishing Email Detector Ready")

email = input("\nEnter email text:\n")

email_vec = vectorizer.transform([email])

prediction = model.predict(email_vec)[0]
prob = model.predict_proba(email_vec)[0][1]

if prediction == 1:
    print("\n⚠️ PHISHING EMAIL DETECTED")
else:
    print("\n✅ SAFE EMAIL")

print("Confidence:", round(prob*100,2), "%")