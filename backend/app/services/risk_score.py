from typing import Dict, Any

def calculate_risk_score(
    probability: float,
    features: Dict[str, Any],
    threat_type: str
) -> int:
    """Calculate risk score from 0-100"""
    
    # Base score from ML probability
    base_score = probability * 100
    
    # Adjustments based on features
    adjustments = 0
    
    if threat_type == "phishing":
        if features.get("urgency_count", 0) > 2:
            adjustments += 10
        if features.get("suspicious_count", 0) > 3:
            adjustments += 15
        if features.get("has_links", False):
            adjustments += 5
            
    elif threat_type == "url":
        if features.get("has_ip", False):
            adjustments += 20
        if features.get("has_at", False):
            adjustments += 15
        if features.get("suspicious_count", 0) > 2:
            adjustments += 10
            
    elif threat_type == "deepfake":
        if features.get("file_size", 0) > 50 * 1024 * 1024:
            adjustments += 5
    
    # Calculate final score (capped 0-100)
    final_score = min(100, max(0, base_score + adjustments))
    
    return int(final_score)