from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ResumeResponse(BaseModel):
    user_id: str
    filename: str
    file_url: str
    parsed_text_preview: str
    char_count: int
    uploaded_at: datetime
