from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
import jwt
from datetime import datetime, timedelta

from app.db.supabase import supabase
from app.config import settings
from app.models.schemas import UserCreate, UserLogin, UserResponse

router = APIRouter()

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

async def get_current_user_optional(authorization: Optional[str] = Header(None)):
    """Get current user from token (optional)"""
    if not authorization:
        return None
    
    try:
        token = authorization.replace("Bearer ", "")
        user = supabase.get_user_from_token(token)
        return user
    except:
        return None

async def get_current_user_required(authorization: str = Header(...)):
    """Get current user from token (required)"""
    token = authorization.replace("Bearer ", "")
    user = supabase.get_user_from_token(token)
    if not user:
        raise HTTPException(401, "Invalid token")
    return user

@router.post("/signup", response_model=UserResponse)
async def signup(user_data: UserCreate):
    """Register new user"""
    try:
        # Create user in Supabase Auth
        auth_response = supabase.client.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
        })
        
        if not auth_response.user:
            raise HTTPException(400, "Signup failed")
        
        # Create profile
        profile_data = {
            "id": auth_response.user.id,
            "email": user_data.email,
            "name": user_data.name,
            "role": "user",
            "created_at": datetime.utcnow().isoformat()
        }
        
        supabase.service_client.table("profiles").insert(profile_data).execute()
        
        return UserResponse(
            id=auth_response.user.id,
            email=user_data.email,
            name=user_data.name,
            role="user",
            created_at=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(400, str(e))

@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    """Login user"""
    try:
        auth_response = supabase.client.auth.sign_in_with_password({
            "email": user_data.email,
            "password": user_data.password,
        })
        
        if not auth_response.user:
            raise HTTPException(401, "Invalid credentials")
        
        return TokenResponse(
            access_token=auth_response.session.access_token,
            token_type="bearer",
            user={
                "id": auth_response.user.id,
                "email": auth_response.user.email
            }
        )
        
    except Exception as e:
        raise HTTPException(401, "Invalid credentials")