from bson import ObjectId

class StatsService:
    def __init__(self, db):
        self.db = db

    async def get_dashboard(self, user_id: str) -> dict:
        uid  = ObjectId(user_id)
        user = await self.db.users.find_one({"_id": uid})

        if not user:
            return {}

        stats = user.get("stats", {})

        # Status breakdown via aggregation
        pipeline = [
            {"$match": {"user_id": uid}},
            {"$group": {
                "_id":   "$status",
                "count": {"$sum": 1}
            }}
        ]
        status_counts = {}
        async for row in self.db.applications.aggregate(
            pipeline
        ):
            status_counts[row["_id"]] = row["count"]

        # Recent feed — last 20 applications
        cursor = self.db.applications.find(
            {"user_id": uid}
        ).sort("created_at", -1).limit(20)

        feed = []
        async for a in cursor:
            job = await self.db.jobs.find_one(
                {"_id": a["job_id"]}
            )
            if job:
                feed.append({
                    "application_id": str(a["_id"]),
                    "job_title":      job["title"],
                    "company":        job["company"],
                    "location":       job["location"],
                    "apply_url":      job["apply_url"],
                    "source":         job["source"],
                    "match_score":    round(
                        a.get("match_score", 0), 1
                    ),
                    "status":         a.get("status"),
                    "applied_at":     a.get("applied_at"),
                    "reasons":        a.get("reasons", ""),
                })

        # Average match score
        avg_pipeline = [
            {"$match": {
                "user_id": uid,
                "match_score": {"$gt": 0}
            }},
            {"$group": {
                "_id": None,
                "avg": {"$avg": "$match_score"}
            }}
        ]
        avg_score = 0.0
        async for row in self.db.applications.aggregate(
            avg_pipeline
        ):
            avg_score = round(row["avg"], 1)

        return {
            "autopilot_enabled":    user.get(
                "autopilot_enabled", False
            ),
            "is_paused":            user.get(
                "is_paused", False
            ),
            "last_scraped_at":      user.get(
                "last_scraped_at"
            ),
            "autopilot_started_at": user.get(
                "autopilot_started_at"
            ),
            "stats": {
                "total_applied":      stats.get(
                    "total_applied", 0
                ),
                "applied_today":      stats.get(
                    "applied_today", 0
                ),
                "applied_this_week":  stats.get(
                    "applied_this_week", 0
                ),
                "avg_match_score":    avg_score,
            },
            "status_counts": status_counts,
            "feed":          feed,
        }
