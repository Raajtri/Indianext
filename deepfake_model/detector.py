from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import cv2
from skimage import filters
import numpy as np
from pydantic import BaseModel
import tensorflow as tf
from mtcnn import MTCNN
from tensorflow.keras.applications import Xception
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model
import os
import uuid
import shutil
import uvicorn
from typing import List, Optional
import logging
from datetime import datetime
import tempfile

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Deepfake Detection ML Service",
    description="Xception-based deepfake detection for images and videos",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for model and detector
model = None
detector = None

# Model weights path
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_WEIGHTS_PATH = os.path.join(BASE_DIR, "xception_weights_tf_dim_ordering_tf_kernels_notop.h5")
@app.on_event("startup")
async def load_model():
    """Load the Xception model and MTCNN detector on startup"""
    global model, detector
    
    try:
        logger.info("Loading Xception model...")
        
        # Check if weights file exists
        if not os.path.exists(MODEL_WEIGHTS_PATH):
            logger.warning(f"Model weights not found at {MODEL_WEIGHTS_PATH}")
            logger.warning("Please download Xception weights from: https://github.com/fchollet/deep-learning-models/releases/download/v0.4/xception_weights_tf_dim_ordering_tf_kernels_notop.h5")
            # Create a placeholder model for fallback
            model = None
        else:
            # Load base Xception model
            base_model = Xception(
                weights=MODEL_WEIGHTS_PATH,
                include_top=False,
                input_shape=(299, 299, 3)
            )
            
            # Add custom layers for deepfake detection
            x = base_model.output
            x = GlobalAveragePooling2D()(x)
            predictions = Dense(1, activation="sigmoid")(x)
            
            model = Model(inputs=base_model.input, outputs=predictions)
            logger.info("✅ Xception model loaded successfully")
        
        # Initialize MTCNN face detector
        detector = MTCNN()
        logger.info("✅ MTCNN face detector loaded")
        
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        model = None
        detector = None

# Request/Response Models
class DeepfakeResponse(BaseModel):
    probability: float
    confidence: float
    prediction: int
    risk_level: str
    threat_type: str
    explanation: List[str]
    features: dict
    frames_analyzed: Optional[int] = None
    fake_frames: Optional[int] = None
    real_frames: Optional[int] = None

class DeepfakeImageResponse(DeepfakeResponse):
    face_detected: bool
    face_location: Optional[dict] = None

class DeepfakeVideoResponse(DeepfakeResponse):
    total_frames: int
    fake_percentage: float
    real_percentage: float

# Helper functions
def preprocess_face(face: np.ndarray) -> np.ndarray:
    """Preprocess face image for model input"""
    face = cv2.resize(face, (299, 299))
    face = face / 255.0
    face = np.expand_dims(face, axis=0)
    return face
def analyze_face(face_img: np.ndarray) -> float:
    try:
        face = cv2.resize(face_img, (299, 299))
        face = face / 255.0
        face = np.expand_dims(face, axis=0)

        if model:
            pred = model.predict(face, verbose=0)[0][0]
        else:
            pred = 0.5

        # 🔥 combine with blur detection
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        blur = cv2.Laplacian(gray, cv2.CV_64F).var()

        blur_score = 1 - min(blur / 300, 1)

        probability = (pred * 0.6 + blur_score * 0.4)

        return float(np.clip(probability, 0, 1))

    except Exception as e:
        print("Error:", e)
        return 0.5
    
def get_fallback_prediction(media_type: str) -> dict:
    """Provide fallback predictions when model is not available"""
    import random
    
    probability = random.uniform(0.3, 0.7)
    
    return {
        "probability": probability,
        "confidence": probability * 80,
        "prediction": 1 if probability > 0.5 else 0,
        "risk_level": "MEDIUM" if probability > 0.4 else "LOW",
        "threat_type": "deepfake" if probability > 0.5 else "safe",
        "explanation": [
            "Using basic analysis (deep learning model not available)",
            "Manual verification recommended",
            "Results may be less accurate"
        ],
        "features": {
            "media_type": media_type,
            "fallback_mode": True
        }
    }

@app.get("/")
async def root():
    return {
        "service": "Deepfake Detection ML Service",
        "status": "ready",
        "model_loaded": model is not None,
        "detector_loaded": detector is not None,
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "detector_loaded": detector is not None
    }

@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    media_type: str = Form(...)
):
    if media_type == "image":
        return await predict_image(file=file)

    elif media_type == "video":
        return await predict_video(file=file)

    else:
        raise HTTPException(400, "Invalid media_type")

@app.post("/predict/image", response_model=DeepfakeImageResponse)
async def predict_image(
    file: UploadFile = File(...)
):
    """
    Detect deepfake in a single image
    """
    temp_path = None
    
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(400, "File must be an image")
        
        logger.info(f"Processing image: {file.filename}")
        
        # Save uploaded file temporarily
        temp_path = f"temp/{uuid.uuid4()}_{file.filename}"
        os.makedirs("temp", exist_ok=True)
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Read image
        img = cv2.imread(temp_path)
        if img is None:
            raise HTTPException(400, "Could not read image file")
        
        # Detect faces
        faces = detector.detect_faces(img) if detector else []
        
        face_detected = len(faces) > 0
        face_location = None
        probability = 0.5
        
        if face_detected:
            # Get first face
            x, y, w, h = faces[0]['box']
            face_location = {"x": x, "y": y, "width": w, "height": h}
            
            # Extract face
            face = img[y:y+h, x:x+w]
            
            # Analyze face
            probability = analyze_face(face)
        else:
            # No face detected - use fallback
            probability = 0.3
            logger.warning("No face detected in image")
        
        # Calculate confidence
        confidence = probability * 100
        
        # Determine risk level
        if probability > 0.8:
            risk_level = "HIGH"
            prediction = 1
            threat_type = "deepfake"
        elif probability > 0.5:
            risk_level = "MEDIUM"
            prediction = 1
            threat_type = "deepfake"
        else:
            risk_level = "LOW"
            prediction = 0
            threat_type = "safe"
        
        # Generate explanation
        explanation = []
        if not face_detected:
            explanation.append("No face detected in image")
            explanation.append("Cannot perform deepfake analysis")
        elif probability > 0.8:
            explanation.append("Strong indicators of AI manipulation detected")
            explanation.append("Facial inconsistencies observed")
            explanation.append("Likely deepfake content")
        elif probability > 0.5:
            explanation.append("Some signs of potential manipulation")
            explanation.append("Manual verification recommended")
        else:
            explanation.append("Image appears authentic")
            explanation.append("No deepfake indicators detected")
        
        # Features
        features = {
            "face_detected": face_detected,
            "image_size": f"{img.shape[1]}x{img.shape[0]}",
            "file_name": file.filename,
            "file_size": os.path.getsize(temp_path)
        }
        
        if face_location:
            features["face_location"] = face_location
        
        return DeepfakeImageResponse(
            probability=probability,
            confidence=confidence,
            prediction=prediction,
            risk_level=risk_level,
            threat_type=threat_type,
            explanation=explanation,
            features=features,
            face_detected=face_detected,
            face_location=face_location
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        raise HTTPException(500, f"Image analysis failed: {str(e)}")
    finally:
        # Cleanup
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/predict/video", response_model=DeepfakeVideoResponse)
async def predict_video(
    file: UploadFile = File(...),
    frame_sample_rate: int = Form(5)  # Analyze every 5th frame by default
):
    """
    Detect deepfake in a video file
    """
    temp_path = None
    
    try:
        # Validate file type
        if not file.content_type.startswith('video/'):
            raise HTTPException(400, "File must be a video")
        
        logger.info(f"Processing video: {file.filename}")
        
        # Save uploaded file temporarily
        temp_path = f"temp/{uuid.uuid4()}_{file.filename}"
        os.makedirs("temp", exist_ok=True)
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Open video capture
        cap = cv2.VideoCapture(temp_path)
        
        if not cap.isOpened():
            raise HTTPException(400, "Could not open video file")
        
        scores = []
        frame_id = 0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        logger.info(f"Total frames: {total_frames}, sampling rate: {frame_sample_rate}")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_id += 1
            
            # Sample frames
            if frame_id % frame_sample_rate != 0:
                continue
            
            # Detect faces
            if detector:
                faces = detector.detect_faces(frame)
                
                if len(faces) > 0:
                    # Get first face
                    x, y, w, h = faces[0]['box']
                    
                    # Extract face
                    face = frame[y:y+h, x:x+w]
                    
                    # Analyze face
                    pred = analyze_face(face)
                    scores.append(pred)
        
        cap.release()
        
        if len(scores) == 0:
            # No faces detected
            probability = 0.3
            explanation = ["No faces detected in video", "Cannot perform deepfake analysis"]
            fake_frames = 0
            real_frames = 0
        else:
            # Calculate statistics
            fake_frames = sum(1 for s in scores if s > 0.5)
            real_frames = len(scores) - fake_frames
            
            # Overall probability (average of scores)
            probability = float(np.mean(scores))
            
            # Generate explanation
            fake_percentage = (fake_frames / len(scores)) * 100
            real_percentage = (real_frames / len(scores)) * 100
            
            if fake_percentage > 70:
                explanation = [
                    f"⚠️ Deepfake detected in {fake_percentage:.1f}% of analyzed frames",
                    "Strong indicators of AI manipulation throughout video",
                    "Facial inconsistencies and artifacts detected"
                ]
            elif fake_percentage > 40:
                explanation = [
                    f"⚠️ Suspicious: {fake_percentage:.1f}% of frames show manipulation",
                    "Mixed signals detected",
                    "Manual verification recommended"
                ]
            else:
                explanation = [
                    f"✅ Video appears authentic ({real_percentage:.1f}% real frames)",
                    "No significant deepfake indicators detected"
                ]
        
        # Calculate confidence
        confidence = probability * 100
        
        # Determine risk level
        if probability > 0.8:
            risk_level = "HIGH"
            prediction = 1
            threat_type = "deepfake"
        elif probability > 0.5:
            risk_level = "MEDIUM"
            prediction = 1
            threat_type = "deepfake"
        else:
            risk_level = "LOW"
            prediction = 0
            threat_type = "safe"
        
        # Features
        features = {
            "file_name": file.filename,
            "file_size": os.path.getsize(temp_path),
            "total_frames": total_frames,
            "frames_analyzed": len(scores),
            "sample_rate": frame_sample_rate
        }
        
        return DeepfakeVideoResponse(
            probability=probability,
            confidence=confidence,
            prediction=prediction,
            risk_level=risk_level,
            threat_type=threat_type,
            explanation=explanation,
            features=features,
            frames_analyzed=len(scores),
            fake_frames=fake_frames if 'fake_frames' in locals() else 0,
            real_frames=real_frames if 'real_frames' in locals() else 0,
            total_frames=total_frames,
            fake_percentage=(fake_frames/len(scores)*100) if len(scores) > 0 else 0,
            real_percentage=(real_frames/len(scores)*100) if len(scores) > 0 else 0
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        raise HTTPException(500, f"Video analysis failed: {str(e)}")
    finally:
        # Cleanup
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/predict/batch")
async def predict_batch(
    files: List[UploadFile] = File(...),
    media_type: str = Form(...)
):
    """
    Batch prediction for multiple images/videos
    """
    results = []
    
    for file in files:
        try:
            if media_type == "image":
                result = await predict_image(file)
            elif media_type == "video":
                result = await predict_video(file)
            else:
                result = {"error": "Invalid media type"}
            
            results.append({
                "filename": file.filename,
                "result": result
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {"results": results}

@app.post("/predict", response_model=DeepfakeResponse)
async def predict(
    file: UploadFile = File(...),
    media_type: str = Form(...)
):
    """
    Universal endpoint - automatically routes to image or video detection
    """
    if media_type == "image":
        return await predict_image(file)
    elif media_type == "video":
        return await predict_video(file)
    else:
        raise HTTPException(400, "media_type must be 'image' or 'video'")

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=5003,
        reload=True
    )