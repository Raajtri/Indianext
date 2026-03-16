import joblib
import tldextract
from urllib.parse import urlparse
import re

from explainable_ai.url_explain import explain_url
from explainable_ai.suggestions import get_suggestions


model = joblib.load("url_model.pkl")
vectorizer = joblib.load("url_vectorizer.pkl")

print("🔗 AI URL Security Scanner Ready")


# ----------------------------
# Brands commonly targeted
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


# ----------------------------
# Domain heuristic analysis
# ----------------------------
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