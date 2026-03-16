import re
from typing import Dict, Optional
from urllib.parse import urlparse

def extract_email_features(
    email_text: str,
    sender: Optional[str] = None,
    subject: Optional[str] = None
) -> Dict:
    """Extract features from email for analysis"""
    text = email_text.lower()
    
    urgency_words = ['urgent', 'immediately', 'asap', 'action']
    suspicious_words = ['verify', 'account', 'password', 'bank', 'paypal', 'credit card']
    
    features = {
        "length": len(text),
        "word_count": len(text.split()),
        "urgency_count": sum(1 for w in urgency_words if w in text),
        "suspicious_count": sum(1 for w in suspicious_words if w in text),
        "has_links": bool(re.search(r'https?://', text)),
        "link_count": len(re.findall(r'https?://[^\s]+', text)),
        "has_html": bool(re.search(r'<[^>]+>', text)),
    }
    
    # Extract sender domain if available
    if sender and '@' in sender:
        features["sender_domain"] = sender.split('@')[1]
    
    return features

def extract_url_features(url: str) -> Dict:
    """Extract features from URL for analysis"""
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname or ""
        
        features = {
            "length": len(url),
            "dot_count": hostname.count('.'),
            "hyphen_count": hostname.count('-'),
            "has_https": url.startswith('https'),
            "has_ip": bool(re.match(r'\d+\.\d+\.\d+\.\d+', hostname)),
            "has_at": '@' in url,
            "special_char_count": len(re.findall(r'[<>{}|\\^~\[\]`;]', url)),
        }
        
        return features
    except:
        return {}