from bson import ObjectId
from datetime import datetime
from typing import Optional

class ApplyService:
    def __init__(self, db):
        self.db = db

    async def create_pending(
        self, user_id: str, job_id: str
    ) -> dict:
        """Creates a pending application record."""
        doc = {
            "user_id":     ObjectId(user_id),
            "job_id":      ObjectId(job_id),
            "status":      "pending",
            "match_score": 0.0,
            "applied_at":  None,
            "error":       "",
            "reasons":     "",
            "created_at":  datetime.utcnow(),
        }
        result = await self.db.applications.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    async def set_status(
        self,
        app_id: str,
        status: str,
        error: str = ""
    ):
        await self.db.applications.update_one(
            {"_id": ObjectId(app_id)},
            {"$set": {
                "status": status,
                "error":  error,
                "applied_at": datetime.utcnow()
                     if status == "applied" else None
            }}
        )

    async def list_for_user(
        self,
        user_id: str,
        status: Optional[str] = None,
        limit: int = 50
    ) -> list:
        query = {"user_id": ObjectId(user_id)}
        if status:
            query["status"] = status

        cursor = self.db.applications.find(
            query
        ).sort("created_at", -1).limit(limit)

        apps = []
        async for a in cursor:
            job = await self.db.jobs.find_one(
                {"_id": a["job_id"]}
            )
            apps.append({
                "application_id": str(a["_id"]),
                "status":         a.get("status", ""),
                "match_score":    a.get("match_score", 0),
                "job_title":  job["title"] if job else "",
                "company":    job["company"] if job else "",
                "location":   job["location"] if job else "",
                "apply_url":  job["apply_url"] if job else "",
                "applied_at": a.get("applied_at"),
                "reasons":    a.get("reasons", ""),
                "error":      a.get("error", ""),
            })
        return apps
