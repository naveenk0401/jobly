from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Job(BaseModel):
    source: str          # greenhouse | lever | workday
    company: str         # company slug e.g. "stripe"
    title: str
    location: str
    description: str
    apply_url: str
    dedup_hash: str
    is_active: bool = True
    scraped_at: Optional[datetime] = None

    def to_mongo(self) -> dict:
        d = self.model_dump()
        if not d["scraped_at"]:
            d["scraped_at"] = datetime.utcnow()
        return d
