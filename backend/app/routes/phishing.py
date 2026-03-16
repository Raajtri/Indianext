from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from datetime import datetime
import logging

from app.models.schemas import EmailScanRequest, ScanResponse
from app.services.ml_client import ml_client
from app.services.risk_score import calculate_risk_score
from app.services.recommendations import get_recommendations
from app.database.supabase_client import supabase
from app.utils.helpers import extract_email_features
from app.routes.auth import get_current_user_optional

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/scan", response_model=ScanResponse)
async def scan_email(
    request: EmailScanRequest,
    user=Depends(get_current_user_optional)
):
    """
    Scan email content for phishing attempts
    Uses your trained XGBoost model
    """

    try:
        logger.info("Processing phishing scan request")

        # Extract email features
        features = extract_email_features(
            request.email_text,
            request.sender,
            request.subject
        )

        # Run ML model
        ml_result = await ml_client.predict_phishing(
            request.email_text,
            features
        )

        probability = ml_result.get("probability", 0.5)

        # Risk score (0-100)
        risk_score = calculate_risk_score(
            probability,
            features,
            "phishing"
        )

        # Risk level
        if risk_score >= 70:
            risk_level = "HIGH"
            threat_type = "phishing"
        elif risk_score >= 40:
            risk_level = "MEDIUM"
            threat_type = "phishing"
        else:
            risk_level = "LOW"
            threat_type = "safe"

        explanation = ml_result.get(
            "explanation",
            ["Email analyzed by AI model", f"Confidence: {probability*100:.1f}%"]
        )

        recommendations = get_recommendations(
            "phishing",
            risk_score
        )

        scan_id = None

        # Save scan if user logged in
        if True:

            scan_data = {
                "input_type": "email",
                "input_data": request.email_text[:500],
                "threat_type": threat_type,
                "probability": probability,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "explanation": explanation,
                "recommendations": recommendations,
                "features": ml_result.get("features", features)
            }

            result = supabase.save_scan("demo-user", scan_data)

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