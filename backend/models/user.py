from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class UserPreferences(BaseModel):
    roles: List[str] = []
    locations: List[str] = []
    target_companies: List[str] = []
    platforms: List[str] = ["greenhouse", "lever"]
    match_threshold: int = 65
    experience_level: str = "mid"

class UserCreate(BaseModel):
    email: str
    name: str
    phone: Optional[str] = ""
    summary: Optional[str] = ""
    preferences: UserPreferences = UserPreferences()

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    summary: Optional[str] = None
    preferences: Optional[UserPreferences] = None

class AutopilotRequest(BaseModel):
    user_id: str
