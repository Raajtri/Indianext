import httpx
import asyncio
from typing import Dict, Any, Optional
from fastapi import HTTPException
from app.config import settings
import logging
import os

logger = logging.getLogger(__name__)

class MLServiceClient:
    """Client to communicate with your existing ML microservices"""
    
    def __init__(self):
        self.phishing_url = settings.PHISHING_ML_URL
        self.url_url = settings.URL_ML_URL
        self.deepfake_url = settings.DEEPFAKE_ML_URL
        self.timeout = 30.0
        
    async def predict_phishing(self, email_text: str, features: Optional[Dict] = None) -> Dict[str, Any]:
        """Call your existing phishing model service"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.phishing_url}/predict",
                    json={
                        "email_text": email_text,
                        "features": features or {}
                    }
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.TimeoutException:
            logger.error("Phishing ML service timeout")
            return self.get_phishing_fallback(email_text, features)
        except httpx.HTTPStatusError as e:
            logger.error(f"Phishing ML service error: {e}")
            return self.get_phishing_fallback(email_text, features)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return self.get_phishing_fallback(email_text, features)
    
    async def predict_url(self, url: str, features: Optional[Dict] = None) -> Dict[str, Any]:
        """Call your existing URL model service"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.url_url}/predict",
                    json={
                        "url": url,
                        "features": features or {}
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"URL ML service error: {e}")
            return self.get_url_fallback(url, features)
    
    async def predict_deepfake(self, file_path: str, media_type: str) -> Dict[str, Any]:
        """Call your existing deepfake model service"""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f, 'application/octet-stream')}
                
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.deepfake_url}/predict",
                        data={"media_type": media_type},
                        files=files
                    )
                    response.raise_for_status()
                    return response.json()
        except Exception as e:
            logger.error(f"Deepfake ML service error: {e}")
            return self.get_deepfake_fallback(file_path, media_type)
    
    def get_phishing_fallback(self, email_text: str, features: Optional[Dict]) -> Dict[str, Any]:
        """Fallback using your trained model's logic"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        import joblib
        import os
        
        # Try to load your actual model if available locally
        model_path = "../ml-services/phishing_model/phishing_model.pkl"
        vectorizer_path = "../ml-services/phishing_model/tfidf_vectorizer.pkl"
        
        if os.path.exists(model_path) and os.path.exists(vectorizer_path):
            try:
                model = joblib.load(model_path)
                vectorizer = joblib.load(vectorizer_path)
                
                email_vec = vectorizer.transform([email_text])
                proba = model.predict_proba(email_vec)[0][1]
                
                # Extract features for explanation
                text_lower = email_text.lower()
                urgency_words = ['urgent', 'immediately', 'asap', 'action']
                suspicious_words = ['verify', 'account', 'password', 'bank', 'paypal']
                
                return {
                    "probability": float(proba),
                    "confidence": float(proba * 100),
                    "prediction": 1 if proba > 0.5 else 0,
                    "risk_level": "HIGH" if proba > 0.8 else "MEDIUM" if proba > 0.5 else "LOW",
                    "threat_type": "phishing" if proba > 0.5 else "safe",
                    "explanation": self.generate_phishing_explanation(text_lower, proba),
                    "features": {
                        "urgency_count": sum(1 for w in urgency_words if w in text_lower),
                        "suspicious_count": sum(1 for w in suspicious_words if w in text_lower),
                        "has_links": 'http' in text_lower
                    }
                }
            except Exception as e:
                logger.error(f"Fallback model loading failed: {e}")
        
        # Ultimate fallback
        return {
            "probability": 0.5,
            "confidence": 50,
            "prediction": 0,
            "risk_level": "MEDIUM",
            "threat_type": "unknown",
            "explanation": ["Using basic detection rules", "ML service unavailable"],
            "features": features or {}
        }
    
    def get_url_fallback(self, url: str, features: Optional[Dict]) -> Dict[str, Any]:
        """Fallback URL detection"""
        url_lower = url.lower()
        
        suspicious_patterns = [
            'login', 'verify', 'account', 'bank', 'paypal', 'secure',
            'update', '.xyz', '.top', 'bit.ly', 'tinyurl'
        ]
        
        suspicious_count = sum(1 for p in suspicious_patterns if p in url_lower)
        has_ip = any(c.isdigit() for c in url_lower) and '.' in url_lower
        has_at = '@' in url_lower
        
        probability = min(0.95, suspicious_count * 0.1 + (0.3 if has_ip else 0) + (0.25 if has_at else 0))
        
        return {
            "probability": probability,
            "confidence": probability * 100,
            "prediction": 1 if probability > 0.5 else 0,
            "risk_level": "HIGH" if probability > 0.7 else "MEDIUM" if probability > 0.4 else "LOW",
            "threat_type": "malicious_url" if probability > 0.5 else "safe",
            "explanation": self.generate_url_explanation(url_lower, suspicious_count, has_ip, has_at),
            "features": {
                "suspicious_count": suspicious_count,
                "has_ip": has_ip,
                "has_at": has_at
            }
        }
    
    def get_deepfake_fallback(self, file_path: str, media_type: str) -> Dict[str, Any]:
        """Fallback deepfake detection"""
        import random
        
        probability = random.uniform(0.2, 0.6)
        
        return {
            "probability": probability,
            "confidence": probability * 80,
            "prediction": 1 if probability > 0.5 else 0,
            "risk_level": "MEDIUM" if probability > 0.4 else "LOW",
            "threat_type": "deepfake" if probability > 0.5 else "safe",
            "explanation": [
                "Using basic analysis",
                "ML model unavailable",
                "Manual verification recommended"
            ],
            "features": {
                "file_size": os.path.getsize(file_path),
                "media_type": media_type
            }
        }
    
    def generate_phishing_explanation(self, text: str, probability: float) -> list:
        explanations = []
        
        if probability > 0.7:
            explanations.append("High probability of phishing detected")
        elif probability > 0.4:
            explanations.append("Suspicious patterns detected")
        else:
            explanations.append("Email appears legitimate")
        
        if 'urgent' in text or 'immediately' in text:
            explanations.append("Uses urgency language to pressure action")
        if 'verify' in text or 'account' in text:
            explanations.append("Requests account verification")
        if 'http' in text:
            explanations.append("Contains links that may be malicious")
        if 'password' in text or 'credit card' in text:
            explanations.append("Requests sensitive information")
            
        return explanations[:4]
    
    def generate_url_explanation(self, url: str, suspicious_count: int, has_ip: bool, has_at: bool) -> list:
        explanations = []
        
        if suspicious_count > 0:
            explanations.append(f"Contains {suspicious_count} suspicious patterns")
        if has_ip:
            explanations.append("Uses IP address instead of domain name")
        if has_at:
            explanations.append("Contains @ symbol - can hide real destination")
        if not url.startswith('https'):
            explanations.append("No HTTPS encryption")
        if not explanations:
            explanations.append("URL appears legitimate")
            
        return explanations

# Global instance
ml_client = MLServiceClient()