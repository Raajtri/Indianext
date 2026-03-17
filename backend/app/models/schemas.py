from pydantic import BaseModel, Field, HttpUrl, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ThreatType(str, Enum):
    PHISHING = "phishing"
    MALICIOUS_URL = "malicious_url"
    DEEPFAKE = "deepfake"
    SAFE = "safe"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

# Request Models
class EmailScanRequest(BaseModel):
    email_text: str
    sender: Optional[str] = None
    subject: Optional[str] = None   

class UrlScanRequest(BaseModel):
    url: HttpUrl

# Response Models
class ScanResponse(BaseModel):
    scan_id: Optional[str] = None
    threat_type: str
    probability: float = Field(..., ge=0, le=1)
    confidence: float = Field(..., ge=0, le=100)
    risk_score: int = Field(..., ge=0, le=100)
    risk_level: str
    explanation: List[str]
    recommendations: List[str]
    features: Dict[str, Any]
    timestamp: datetime

# User Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str]
    role: str
    created_at: datetime