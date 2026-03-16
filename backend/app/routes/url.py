from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime

from app.models.schemas import UrlScanRequest, ScanResponse
from app.core.ml_client import ml_client
from app.core.risk_score import calculate_risk_score
from app.core.recommendations import get_recommendations
from app.db.supabase import supabase
from app.utils.helpers import extract_url_features
from app.api.auth import get_current_user_optional
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/scan", response_model=ScanResponse)
async def scan_url(
    request: UrlScanRequest,
    user = Depends(get_current_user_optional)
):
    """Scan URL for malicious content"""
    try:
        url_str = str(request.url)
        
        # Extract features
        features = extract_url_features(url_str)
        
        # Call ML model
        ml_result = await ml_client.predict_url(url_str, features)
        
        probability = ml_result.get("probability", 0.5)
        
        # Calculate risk score
        risk_score = calculate_risk_score(
            probability,
            features,
            "url"
        )
        
        # Determine risk level
        if risk_score >= 70:
            risk_level = "HIGH"
            threat_type = "malicious_url"
        elif risk_score >= 40:
            risk_level = "MEDIUM"
            threat_type = "malicious_url"
        else:
            risk_level = "LOW"
            threat_type = "safe"
        
        explanation = ml_result.get(
            "explanation",
            ["URL analyzed by AI model"]
        )
        
        recommendations = get_recommendations("url", risk_score)
        
        # Save to database
        scan_id = None
        if user:
            scan_data = {
                "input_type": "url",
                "input_data": url_str,
                "threat_type": threat_type,
                "probability": probability,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "explanation": explanation,
                "recommendations": recommendations,
                "features": ml_result.get("features", features)
            }
            result = await supabase.save_scan(user["id"], scan_data)
            if result and result.data:
                scan_id = result.data[0]["id"]
        
        return ScanResponse(
            scan_id=scan_id,
            threat_type=threat_type,
            probability=probability,
            confidence=ml_result.get("confidence", probability * 100),
            risk_score=risk_score,
            risk_level=risk_level,
            explanation=explanation,
            recommendations=recommendations,
            features=ml_result.get("features", features),
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error in URL scan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))