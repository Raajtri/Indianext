import re
import tldextract

def explain_url(url):

    reasons = []
    score = 0

    if re.search(r'\d+\.\d+\.\d+\.\d+', url):
        reasons.append("URL uses IP address instead of domain")
        score += 3

    if url.count('.') > 4:
        reasons.append("Too many subdomains detected")
        score += 2

    if "@" in url:
        reasons.append("URL contains '@' symbol which may hide redirects")
        score += 2

    suspicious_tlds = ["tk","xyz","top","gq","ml"]

    ext = tldextract.extract(url)

    if ext.suffix in suspicious_tlds:
        reasons.append("Suspicious domain extension detected")
        score += 2

    return score, reasons