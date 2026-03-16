from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
    
    # ML Service URLs - Your existing models
    PHISHING_ML_URL: str = os.getenv("PHISHING_ML_URL", "http://localhost:5001")
    URL_ML_URL: str = os.getenv("URL_ML_URL", "http://localhost:5002")
    DEEPFAKE_ML_URL: str = os.getenv("DEEPFAKE_ML_URL", "http://localhost:5003")
    
    # App Settings
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "https://threatlens.vercel.app"
    ]

settings = Settings()