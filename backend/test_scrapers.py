import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from scrapers.greenhouse import GreenhouseScraper
from scrapers.lever import LeverScraper
from config import settings

async def main():
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB]

    print("\n=== GREENHOUSE: stripe ===")
    gh = GreenhouseScraper()
    jobs = await gh.scrape("stripe")
    print(f"Found: {len(jobs)} jobs")
    if jobs:
        print(f"Sample: {jobs[0]['title']} | {jobs[0]['location']}")

        # Store in MongoDB
        saved = 0
        for job in jobs:
            try:
                await db.jobs.update_one(
                    {"dedup_hash": job["dedup_hash"]},
                    {"$setOnInsert": job},
                    upsert=True
                )
                saved += 1
            except Exception:
                pass
        print(f"Saved: {saved} new jobs to MongoDB")

    print("\n=== LEVER: vercel ===")
    lv = LeverScraper()
    jobs = await lv.scrape("vercel")
    print(f"Found: {len(jobs)} jobs")
    if jobs:
        print(f"Sample: {jobs[0]['title']} | {jobs[0]['location']}")

    print("\n=== DEDUP TEST (run again) ===")
    jobs2 = await gh.scrape("stripe")
    saved2 = 0
    for job in jobs2:
        try:
            await db.jobs.update_one(
                {"dedup_hash": job["dedup_hash"]},
                {"$setOnInsert": job},
                upsert=True
            )
            saved2 += 1
        except Exception:
            pass
    print(f"Re-run saved: {saved2} (should be 0 — all duplicates)")

    total = await db.jobs.count_documents({})
    print(f"\nTotal jobs in MongoDB: {total}")
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
