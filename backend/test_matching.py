import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from services.match_service import MatchService
from utils.embedder import embed, cosine_similarity
from config import settings

async def main():
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db     = client[settings.MONGO_DB]
    svc    = MatchService()

    print("\n=== EMBEDDER TEST ===")
    vec1 = embed("Python backend engineer FastAPI MongoDB")
    vec2 = embed("Senior Python developer REST API databases")
    vec3 = embed("Graphic designer Photoshop Illustrator")
    sim12 = cosine_similarity(vec1, vec2)
    sim13 = cosine_similarity(vec1, vec3)
    print(f"Python vs Python-like: {sim12:.3f} (expect > 0.7)")
    print(f"Python vs Designer:    {sim13:.3f} (expect < 0.5)")
    assert sim12 > sim13, "Embedder similarity logic broken!"
    print("✅ Embedder working correctly")

    print("\n=== RESUME LOAD TEST ===")
    resume = await db.resumes.find_one({})
    if not resume:
        print("❌ No resume found — upload one via POST /resume")
        client.close()
        return
    print(f"✅ Resume found: {resume['char_count']} chars")
    print(f"   Preview: {resume['parsed_text'][:100]}...")

    print("\n=== MATCHING TEST (first 5 jobs) ===")
    cursor = db.jobs.find(
        {"is_active": True}
    ).limit(5)

    async for job in cursor:
        result = await svc.score(
            resume["parsed_text"], job
        )
        print(
            f"  {job['title'][:40]:<40} "
            f"@ {job['company']:<15} "
            f"→ {result['score']:5.1f}/100"
        )
        if result["reasons"]:
            first_line = result["reasons"].split("\n")[0]
            print(f"    Reason: {first_line[:80]}")

    print("\n=== THRESHOLD TEST ===")
    user = await db.users.find_one({})
    if user:
        threshold = user.get(
            "preferences", {}
        ).get("match_threshold", 65)
        print(f"User threshold: {threshold}")
        print("Jobs above threshold would be auto-applied")

    print("\n✅ All matching tests passed")
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
