from workers.celery_app import app
from scrapers.greenhouse import GreenhouseScraper
from scrapers.lever import LeverScraper
from scrapers.workday import WorkdayScraper
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from datetime import datetime
import asyncio

SCRAPERS = {
    "greenhouse": GreenhouseScraper,
    "lever":      LeverScraper,
    "workday":    WorkdayScraper,
}

@app.task
def scrape_for_all_autopilot_users():
    """
    Called by Celery Beat every 6h.
    Finds all active autopilot users and queues
    one scrape task per platform per company.
    """
    async def _run():
        client = AsyncIOMotorClient(settings.MONGO_URI)
        db     = client[settings.MONGO_DB]

        cursor = db.users.find({
            "autopilot_enabled": True,
            "is_paused": False
        })

        queued = 0
        async for user in cursor:
            user_id   = str(user["_id"])
            prefs     = user.get("preferences", {})
            companies = prefs.get("target_companies", [])
            platforms = prefs.get(
                "platforms", ["greenhouse", "lever"]
            )

            for platform in platforms:
                for company in companies:
                    scrape_company_for_user.delay(
                        user_id, platform, company
                    )
                    queued += 1

            await db.users.update_one(
                {"_id": user["_id"]},
                {"$set": {
                    "last_scraped_at": datetime.utcnow()
                }}
            )

        print(f"[Beat] Queued {queued} scrape tasks")
        client.close()

    asyncio.run(_run())


@app.task(bind=True, max_retries=3, default_retry_delay=60)
def scrape_company_for_user(
    self, user_id: str, platform: str, company: str
):
    """
    Scrapes one company on one platform for one user.
    Stores new jobs in MongoDB (dedup via unique index).
    Auto-triggers match_new_jobs_for_user for new jobs only.
    """
    async def _run():
        client = AsyncIOMotorClient(settings.MONGO_URI)
        db     = client[settings.MONGO_DB]

        scraper_cls = SCRAPERS.get(platform)
        if not scraper_cls:
            client.close()
            return

        scraper     = scraper_cls()
        jobs        = await scraper.scrape(company)
        new_job_ids = []

        for job in jobs:
            # Convert datetime to ISO string for JSON serialization
            job["scraped_at"] = datetime.utcnow().isoformat()
            try:
                result = await db.jobs.update_one(
                    {"dedup_hash": job["dedup_hash"]},
                    {"$setOnInsert": job},
                    upsert=True
                )
                if result.upserted_id:
                    new_job_ids.append(
                        str(result.upserted_id)
                    )
            except Exception:
                pass  # duplicate key — already stored

        client.close()
        print(
            f"[{platform}] {company} → "
            f"{len(new_job_ids)} new / {len(jobs)} total"
        )

        # Auto-chain: trigger matching for new jobs only
        if new_job_ids:
            from workers.match_tasks import (
                match_new_jobs_for_user
            )
            match_new_jobs_for_user.delay(
                user_id, new_job_ids
            )

    try:
        asyncio.run(_run())
    except Exception as exc:
        raise self.retry(exc=exc)


@app.task
def reset_daily_stats():
    """Resets applied_today counter at midnight UTC."""
    async def _run():
        client = AsyncIOMotorClient(settings.MONGO_URI)
        db     = client[settings.MONGO_DB]
        result = await db.users.update_many(
            {},
            {"$set": {"stats.applied_today": 0}}
        )
        print(
            f"[Stats] Reset applied_today "
            f"for {result.modified_count} users"
        )
        client.close()
    asyncio.run(_run())
