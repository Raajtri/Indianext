from supabase import create_client, Client
from app.config import settings
from typing import Optional, Dict, Any
import jwt
from datetime import datetime

class SupabaseClient:
    def __init__(self):
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        self.service_client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )
    
    def get_user_from_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token and get user"""
        try:
            # Verify with Supabase
            user = self.client.auth.get_user(token)
            if user and user.user:
                return {
                    "id": user.user.id,
                    "email": user.user.email
                }
        except Exception as e:
            return None
        return None
    
    async def save_scan(self, user_id: str, scan_data: Dict[str, Any]):
        """Save scan result to database"""
        data = {
            "user_id": user_id,
            "input_type": scan_data["input_type"],
            "input_data": scan_data["input_data"],
            "threat_type": scan_data["threat_type"],
            "probability": scan_data["probability"],
            "risk_score": scan_data["risk_score"],
            "risk_level": scan_data["risk_level"],
            "explanation": scan_data["explanation"],
            "recommendations": scan_data["recommendations"],
            "features": scan_data.get("features", {}),
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = self.service_client.table("scans").insert(data).execute()
        return result
    
    async def get_user_scans(self, user_id: str, limit: int = 10):
        """Get user's scan history"""
        result = self.service_client.table("scans")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()
        return result.data

supabase = SupabaseClient()