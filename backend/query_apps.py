import motor.motor_asyncio
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def q():
    client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGO_URI"))
    db = client.jobly
    
    print("\n--- APPLICATIONS ---")
    async for a in db.applications.find().sort("created_at", -1).limit(5):
        print(f"ID: {a['_id']}")
        print(f"Status: {a['status']}")
        print(f"Score: {a.get('match_score')}")
        print(f"Reasons: {a.get('reasons')[:100]}...")
        print("-" * 20)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(q())
