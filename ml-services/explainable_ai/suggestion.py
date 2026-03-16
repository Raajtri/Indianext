def get_suggestions(module, prediction):

    if module == "url" and prediction == "phishing":
        return [
            "Do not enter login credentials",
            "Verify the website domain",
            "Access the official website directly",
            "Report the URL as phishing"
        ]

    if module == "url" and prediction == "safe":
        return [
            "Always check SSL certificate",
            "Ensure the domain belongs to the official organization"
        ]

    if module == "email" and prediction == "phishing":
        return [
            "Do NOT click suspicious links",
            "Verify sender identity",
            "Report email to security team",
            "Delete the email if unsure"
        ]

    if module == "email" and prediction == "safe":
        return [
            "Email appears safe but always verify sender",
            "Avoid downloading unknown attachments"
        ]
    return []