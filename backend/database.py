import dns.resolver
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

# Force Google DNS for SRV resolution (fixes network/VPN timeouts)
dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ["8.8.8.8", "1.1.1.1"]

client = None
db = None

async def connect_db():
    global client, db
    client = AsyncIOMotorClient(
        settings.MONGO_URI,
        serverSelectionTimeoutMS=10000,
        connectTimeoutMS=10000
    )
    db = client[settings.MONGO_DB]

    # Create all indexes
    await db.users.create_index("email", unique=True)
    await db.jobs.create_index("dedup_hash", unique=True)
    await db.jobs.create_index("scraped_at")
    await db.jobs.create_index("is_active")
    await db.resumes.create_index("user_id")
    await db.applications.create_index(
        [("user_id", 1), ("status", 1)]
    )
    await db.applications.create_index(
        [("user_id", 1), ("job_id", 1)], unique=True
    )

    print(f"✅ MongoDB connected → {settings.MONGO_DB}")
    print(f"✅ All indexes created")

async def close_db():
    if client:
        client.close()

def get_db():
    return db
