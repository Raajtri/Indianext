from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
import os
import uuid
import shutil
from datetime import datetime

from app.models.schemas import ScanResponse
from app.core.ml_client import ml_client
from app.core.risk_score import calculate_risk_score
from app.core.recommendations import get_recommendations
from app.db.supabase import supabase
from app.api.auth import get_current_user_optional
from app.config import settings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

ALLOWED_VIDEO = ['video/mp4', 'video/avi', 'video/quicktime']
ALLOWED_AUDIO = ['audio/mpeg', 'audio/wav', 'audio/mp3']

@router.post("/scan", response_model=ScanResponse)
async def scan_deepfake(
    file: UploadFile = File(...),
    media_type: str = Form(...),
    user = Depends(get_current_user_optional)
):
    """Scan video/audio for deepfake content"""
    temp_path = None
    
    try:
        # Validate file type
        if media_type == "video" and file.content_type not in ALLOWED_VIDEO:
            raise HTTPException(400, "Invalid video format")
        if media_type == "audio" and file.content_type not in ALLOWED_AUDIO:
            raise HTTPException(400, "Invalid audio format")
        
        # Save temp file
        temp_path = f"uploads/{uuid.uuid4()}_{file.filename}"
        os.makedirs("uploads", exist_ok=True)
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Check file size
        file_size = os.path.getsize(temp_path)
        if file_size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(400, f"File too large. Max: {settings.MAX_UPLOAD_SIZE//1048576}MB")
        
        # Call ML model
        ml_result = await ml_client.predict_deepfake(temp_path, media_type)
        
        probability = ml_result.get("probability", 0.5)
        
        # Features
        features = {
            "file_name": file.filename,
            "file_size": file_size,
            "media_type": media_type,
            **ml_result.get("features", {})
        }
        
        # Calculate risk score
        risk_score = calculate_risk_score(
            probability,
            features,
            "deepfake"
        )
        
        # Determine risk level
        if risk_score >= 70:
            risk_level = "HIGH"
            threat_type = "deepfake"
        elif risk_score >= 40:
            risk_level = "MEDIUM"
            threat_type = "deepfake"
        else:
            risk_level = "LOW"
            threat_type = "safe"
        
        explanation = ml_result.get(
            "explanation",
            ["Media analyzed by AI model"]
        )
        
        recommendations = get_recommendations("deepfake", risk_score)
        
        # Save to database
        scan_id = None
        if user:
            scan_data = {
                "input_type": "deepfake",
                "input_data": file.filename,
                "threat_type": threat_type,
                "probability": probability,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "explanation": explanation,
                "recommendations": recommendations,
                "features": features
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
            features=features,
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in deepfake scan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)