import motor.motor_asyncio
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def q():
    client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGO_URI"))
    db = client.jobly
    
    total = await db.jobs.count_documents({})
    active = await db.jobs.count_documents({"is_active": True})
    print(f"Total jobs: {total}")
    print(f"Active jobs: {active}")
    
    async for j in db.jobs.find().limit(1):
        print(f"Sample job: {j.get('title')} (is_active={j.get('is_active')})")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(q())
