import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from config import settings

load_dotenv()

async def manual_scrape():
    # Use a mock company
    platform = "greenhouse"
    company  = "stripe"
    user_id  = "69bcdaa40d8db9c658e885d5"
    
    print(f"--- MOCK SCRAPE START ({platform}, {company}) ---")
    # Simulate what the scraper would do
    jobs = [
        {"title": "Senior Python Engineer", "company": company, "location": "Remote", "url": "http://example.com/1"},
        {"title": "Backend Developer", "company": company, "location": "NYC", "url": "http://example.com/2"},
        {"title": "Fullstack Wizard", "company": company, "location": "SF", "url": "http://example.com/3"},
    ]
    
    client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
    db     = client.jobly
    
    from utils.dedup import make_hash
    
    new_jobs = []
    for j in jobs:
        j["scraped_at"] = "2026-03-20T11:00:00Z"
        j["is_active"]  = True
        j["dedup_hash"] = make_hash(j["company"], j["title"], j["location"])
        
        try:
            res = await db.jobs.insert_one(j)
            new_jobs.append(str(res.inserted_id))
            print(f"Inserted: {j['title']}")
        except Exception as e:
            print(f"Skip/Error: {e}")
            
    print(f"Total inserted: {len(new_jobs)}")
    
    if new_jobs:
        print(f"Kicking off matching for {len(new_jobs)} jobs...")
        from workers.match_tasks import match_new_jobs_for_user
        # We can't use .delay() here without a running worker picking it up, 
        # but we can see if the import works.
        print("Import workers.match_tasks: SUCCESS")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(manual_scrape())
