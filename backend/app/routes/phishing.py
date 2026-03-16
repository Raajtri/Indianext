from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from datetime import datetime

from app.models.schemas import EmailScanRequest, ScanResponse
from app.core.ml_client import ml_client
from app.core.risk_score import calculate_risk_score
from app.core.recommendations import get_recommendations
from app.db.supabase import supabase
from app.utils.helpers import extract_email_features
from app.api.auth import get_current_user_optional
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/scan", response_model=ScanResponse)
async def scan_email(
    request: EmailScanRequest,
    user = Depends(get_current_user_optional)
):
    """
    Scan email content for phishing attempts
    Uses your trained XGBoost model
    """
    try:
        logger.info(f"Processing phishing scan request")
        
        # Extract basic features
        features = extract_email_features(
            request.email_text,
            request.sender,
            request.subject
        )
        
        # Call your ML model
        ml_result = await ml_client.predict_phishing(
            request.email_text,
            features
        )
        
        # Get probability
        probability = ml_result.get("probability", 0.5)
        
        # Calculate risk score (0-100)
        risk_score = calculate_risk_score(
            probability,
            features,
            "phishing"
        )
        
        # Determine risk level
        if risk_score >= 70:
            risk_level = "HIGH"
            threat_type = "phishing"
        elif risk_score >= 40:
            risk_level = "MEDIUM"
            threat_type = "phishing"
        else:
            risk_level = "LOW"
            threat_type = "safe"
        
        # Get explanation (from ML or generate)
        explanation = ml_result.get(
            "explanation", 
            ["Email analyzed by AI model", f"Confidence: {probability*100:.1f}%"]
        )
        
        # Get recommendations
        recommendations = get_recommendations(
            "phishing",
            risk_score
        )
        
        # Save to Supabase if user authenticated
        scan_id = None
        if user:
            scan_data = {
                "input_type": "email",
                "input_data": request.email_text[:500],  # Store preview
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
        logger.error(f"Error in phishing scan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))