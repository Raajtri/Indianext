import joblib
import tldextract
from urllib.parse import urlparse
import re

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

    url = normalize_url(url)

    domain = extract_domain(url)


    # Brand spoof detection
    if brand_spoof(url, domain):
        return "⚠️ MALICIOUS URL", 99.0, "HIGH"


    # ML prediction
    url_vec = vectorizer.transform([url])

    prob = model.predict_proba(url_vec)[0][1]


    # Domain heuristic adjustment
    if domain_legitimacy(domain):
        prob = prob * 0.35


    confidence = round(prob * 100,2)


    if prob >= 0.85:

        result = "⚠️ MALICIOUS URL"
        level = "HIGH"

    elif prob >= 0.60:

        result = "⚠️ SUSPICIOUS URL"
        level = "MEDIUM"

    else:

        result = "✅ SAFE URL"
        level = "LOW"


    return result, confidence, level


# ----------------------------
# CLI Interface
# ----------------------------
while True:

    url = input("\nEnter URL to scan (or type exit): ")

    if url.lower() == "exit":
        break

    result, confidence, level = scan_url(url)

    print("\nScan Result")
    print("------------------------")
    print(result)
    print("Confidence:", confidence, "%")
    print("Threat Level:", level)