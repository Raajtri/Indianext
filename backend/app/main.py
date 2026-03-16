from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv
import os

from app.routes import phishing, url, deepfake, auth
from app.config import settings

load_dotenv()

app = FastAPI(
    title="ThreatLens AI API",
    description="AI-powered Cybersecurity Threat Detection",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(phishing.router, prefix="/api/phishing", tags=["Phishing Detection"])
app.include_router(url.router, prefix="/api/url", tags=["URL Detection"])
app.include_router(deepfake.router, prefix="/api/deepfake", tags=["Deepfake Detection"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to ThreatLens AI API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "phishing": settings.PHISHING_ML_URL,
            "url": settings.URL_ML_URL,
            "deepfake": settings.DEEPFAKE_ML_URL
        },
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )