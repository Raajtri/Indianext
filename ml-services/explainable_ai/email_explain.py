def explain_email(text):

    reasons = []

    suspicious_words = [
        "urgent",
        "verify your account",
        "click here",
        "login now",
        "update payment",
        "confirm your identity",
        "bank account",
        "limited time",
        "act now"
    ]

    for word in suspicious_words:
        if word in text.lower():
            reasons.append(f"Suspicious phrase detected: '{word}'")

    if "http://" in text.lower() or "https://" in text.lower():
        reasons.append("Email contains external links")

    if "attachment" in text.lower():
        reasons.append("Email references attachments")

    return reasons