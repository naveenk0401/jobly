from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ApplyRequest(BaseModel):
    user_id: str
    job_id: str

class ApplicationResponse(BaseModel):
    application_id: str
    status: str
    match_score: float
    job_title: str
    company: str
    location: str
    apply_url: str
    applied_at: Optional[datetime]
    reasons: Optional[str] = ""
    error: Optional[str] = ""
