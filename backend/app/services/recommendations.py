from typing import List

def get_recommendations(threat_type: str, risk_score: int) -> List[str]:
    """Get security recommendations based on risk"""
    
    if risk_score >= 70:  # HIGH
        if threat_type == "phishing":
            return [
                "🚨 Do NOT click any links",
                "🚨 Do NOT download attachments",
                "🔍 Verify sender through official channels",
                "📢 Report to IT security team",
                "🗑️ Delete the email immediately"
            ]
        elif threat_type == "malicious_url":
            return [
                "🚨 Do NOT visit this website",
                "🚫 Block this domain immediately",
                "📢 Report to security team",
                "🔍 Check for similar legitimate URLs",
                "⚠️ Warn colleagues about this threat"
            ]
        elif threat_type == "deepfake":
            return [
                "🚨 Do NOT trust or share this media",
                "📞 Contact the person through alternative channels",
                "🔍 Verify with official sources",
                "📢 Report to platform administrators",
                "⚠️ Be aware of social engineering attempts"
            ]
            
    elif risk_score >= 40:  # MEDIUM
        if threat_type == "phishing":
            return [
                "⚠️ Exercise caution with this email",
                "🔍 Verify links before clicking",
                "👀 Check sender address carefully",
                "📋 Look for other red flags"
            ]
        elif threat_type == "malicious_url":
            return [
                "⚠️ Verify website legitimacy before proceeding",
                "🔒 Check for HTTPS and valid SSL certificate",
                "🔍 Research the domain reputation",
                "🔄 Use a URL scanner for second opinion"
            ]
        elif threat_type == "deepfake":
            return [
                "⚠️ Verify content through multiple sources",
                "🔍 Check for other versions of this media",
                "⚠️ Be cautious about acting on this content",
                "👀 Look for signs of manipulation"
            ]
    
    # LOW risk
    return [
        "✅ Content appears safe",
        "🛡️ Always maintain general security awareness",
        "🔄 Keep software and security tools updated",
        "📢 Report anything suspicious in the future"
    ]